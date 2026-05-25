if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.dirname(sys.path[0]))

import json
import os
import pickle

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

import datasets.transforms as T

current_dir = os.path.dirname(os.path.abspath(__file__))

if "dataset" not in current_dir:
    current_dir = os.path.join(current_dir, "dataset")
else:
    current_dir = os.path.join(current_dir, ".")

with open(os.path.join(current_dir, "config.json"), "r") as f:
    datasets_path = json.load(f)

datasets_path = datasets_path["datasets_path"]

with open(current_dir + "/default_charset.json", "r") as f:
    charset = json.load(f)


class ICDAR2015(Dataset):
    def __init__(self, mode, transform=transforms.ToTensor(), target_transform=None, args=None):
        if mode == "val":
            mode = "valid"

        self.mode = mode
        self._transforms = transform
        self.target_transform = target_transform

        root_name = getattr(args, "icdar2015_root", "icdar2015_dtlr")
        labels_name = getattr(args, "icdar2015_labels_file", "labels.pkl")
        images_subdir = getattr(args, "icdar2015_images_subdir", "lines")
        self.im_extension = getattr(args, "icdar2015_image_ext", "jpg")

        self.root_path = os.path.join(datasets_path, root_name)
        labels_path = os.path.join(self.root_path, labels_name)
        self.images_path = os.path.join(self.root_path, images_subdir)

        self.data = pickle.load(open(labels_path, "rb"))
        self.charset = charset

    def __len__(self):
        return len(self.data["ground_truth"][self.mode])

    def convert_str_to_tensor(self, text):
        labels = [self.charset.index(c) for c in list(text)]
        return torch.tensor(labels, dtype=torch.int64)

    def __getitem__(self, idx):
        example = self.data["ground_truth"][self.mode][idx]
        text = example["text"]
        im_id = example["id"]

        path_image = os.path.join(self.images_path, f"{im_id}.{self.im_extension}")
        image = Image.open(path_image).convert("RGB")

        labels = {}
        labels["labels"] = self.convert_str_to_tensor(text)
        labels["orig_size"] = torch.tensor([image.size[1], image.size[0]], dtype=torch.int64)
        labels["size"] = torch.tensor([image.size[1], image.size[0]], dtype=torch.int64)
        labels["img_idx"] = torch.tensor([idx], dtype=torch.int64)
        labels["idx"] = torch.tensor([idx], dtype=torch.int64)

        dummy_boxes = torch.tensor([0, 0, 0, 0], dtype=torch.float32)
        labels["boxes"] = dummy_boxes.repeat(labels["labels"].shape[0], 1)

        image, labels = self._transforms(image, labels)
        return image, labels


def make_coco_transforms(image_set, fix_size=False, strong_aug=False, args=None):
    normalize = T.Compose([
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    scales = [480, 512, 544, 576, 608, 640, 672, 704, 736, 768, 800]
    max_size = 1333
    scales2_resize = [400, 500, 600]
    scales2_crop = [384, 600]

    scales = getattr(args, "data_aug_scales", scales)
    max_size = getattr(args, "data_aug_max_size", max_size)
    scales2_resize = getattr(args, "data_aug_scales2_resize", scales2_resize)
    scales2_crop = getattr(args, "data_aug_scales2_crop", scales2_crop)
    random_erasing = getattr(args, "random_erasing", False)

    data_aug_scale_overlap = getattr(args, "data_aug_scale_overlap", None)
    if data_aug_scale_overlap is not None and data_aug_scale_overlap > 0:
        data_aug_scale_overlap = float(data_aug_scale_overlap)
        scales = [int(i * data_aug_scale_overlap) for i in scales]
        max_size = int(max_size * data_aug_scale_overlap)
        scales2_resize = [int(i * data_aug_scale_overlap) for i in scales2_resize]
        scales2_crop = [int(i * data_aug_scale_overlap) for i in scales2_crop]

    if image_set == "train":
        if random_erasing:
            random_erasing_transforms = [
                T.RandomErasingFullVertical(p=0.5, scale=(0.01, 0.04), ratio=(3, 6))
                for _ in range(5)
            ]
        else:
            random_erasing_transforms = []

        if fix_size:
            return T.Compose([
                T.RandomResize([(max_size, max(scales))]),
                normalize,
                *random_erasing_transforms,
            ])

        if strong_aug:
            import datasets.sltransform as SLT

            return T.Compose([
                T.RandomSelect(
                    T.RandomResize(scales, max_size=max_size),
                    T.Compose([T.RandomResize(scales, max_size=max_size)]),
                ),
                SLT.RandomSelectMulti([
                    SLT.LightingNoise(),
                    SLT.AdjustBrightness(2),
                    SLT.AdjustContrast(2),
                ]),
                normalize,
                *random_erasing_transforms,
            ])

        return T.Compose([
            T.RandomSelect(
                T.RandomResize(scales, max_size=max_size),
                T.Compose([T.RandomResize(scales, max_size=max_size)]),
            ),
            normalize,
            *random_erasing_transforms,
            T.RandomErasing(p=0.5, scale=(0.005, 0.05), ratio=(5, 6)),
            T.RandomErasing(p=0.5, scale=(0.005, 0.05), ratio=(5, 6)),
            T.RandomErasing(p=0.5, scale=(0.005, 0.05), ratio=(5, 6)),
            T.RandomErasing(p=0.5, scale=(0.005, 0.05), ratio=(5, 6)),
        ])

    if image_set in ["val", "eval_debug", "train_reg", "test"]:
        if os.environ.get("GFLOPS_DEBUG_SHILONG", False) == "INFO":
            return T.Compose([
                T.ResizeDebug((1280, 800)),
                normalize,
            ])

        return T.Compose([
            T.RandomResize([max(scales)], max_size=max_size),
            normalize,
        ])

    raise ValueError(f"unknown {image_set}")


def build_icdar2015(image_set, args):
    transforms = make_coco_transforms(image_set, args=args)
    return ICDAR2015(image_set, transforms, args=args)
