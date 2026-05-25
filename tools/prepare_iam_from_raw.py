import argparse
import pickle
import shutil
from pathlib import Path

from PIL import Image, ImageOps


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare IAM raw line images into DTLR/PyLaia-style processed data."
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=Path("data/IAM"),
        help="IAM raw root containing ascii/ and lines/ directories.",
    )
    parser.add_argument(
        "--split-labels",
        type=Path,
        default=Path("util/data/IAM_new/labels.pkl"),
        help="Reference labels.pkl with correct IAM splits (e.g. util/data/IAM_new/labels.pkl).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/IAM_new"),
        help="Output processed IAM root.",
    )
    parser.add_argument(
        "--output-labels",
        type=Path,
        default=Path("data/IAM/labels.pkl"),
        help="DTLR IAM loader reads labels from data/IAM/labels.pkl.",
    )
    parser.add_argument(
        "--image-folder-name",
        type=str,
        default="imgs",
        help="Subfolder name under output_root/data/ used by datasets/IAM.py.",
    )
    parser.add_argument(
        "--resize-height",
        type=int,
        default=128,
        help="Resize processed lines to this fixed height while preserving aspect ratio.",
    )
    parser.add_argument(
        "--horizontal-pad",
        type=int,
        default=20,
        help="Add white padding to left and right after trimming.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite previously processed images and labels.",
    )
    return parser.parse_args()


def trim_white_borders(image: Image.Image, threshold: int = 250) -> Image.Image:
    gray = image.convert("L")
    inv = gray.point(lambda p: 255 if p < threshold else 0)
    bbox = inv.getbbox()
    if bbox is None:
        return image
    return image.crop(bbox)


def process_image(src_path: Path, dst_path: Path, resize_height: int, horizontal_pad: int):
    with Image.open(src_path) as img:
        img = img.convert("L")
        img = trim_white_borders(img)
        img = ImageOps.expand(img, border=(horizontal_pad, 0, horizontal_pad, 0), fill=255)
        w, h = img.size
        if h != resize_height:
            new_w = max(1, round(w * (resize_height / h)))
            img = img.resize((new_w, resize_height), Image.Resampling.BICUBIC)
        img = img.convert("RGB")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(dst_path, format="JPEG", quality=95)


def main():
    args = parse_args()

    raw_root = args.raw_root
    lines_root = raw_root / "lines"
    output_images = args.output_root / "data" / args.image_folder_name / "lines"
    output_labels = args.output_labels

    if not lines_root.exists():
        raise FileNotFoundError(f"Raw lines directory not found: {lines_root}")
    if not args.split_labels.exists():
        raise FileNotFoundError(f"Split labels file not found: {args.split_labels}")

    split_data = pickle.load(open(args.split_labels, "rb"))
    ground_truth = split_data["ground_truth"]

    if output_labels.exists() and not args.overwrite:
        backup_path = output_labels.with_suffix(".backup.pkl")
        if not backup_path.exists():
            shutil.copy2(output_labels, backup_path)
            print(f"Backed up existing labels to: {backup_path}")

    total = 0
    missing = []
    for split_name, samples in ground_truth.items():
        for sample in samples:
            total += 1
            line_id = sample["id"]
            folder = sample.get("folder") or "-".join(line_id.split("-")[:2])
            src_path = lines_root / folder.split("-")[0] / folder / f"{line_id}.png"
            dst_path = output_images / f"{line_id}.jpg"

            if not src_path.exists():
                missing.append(str(src_path))
                continue

            if dst_path.exists() and not args.overwrite:
                continue
            process_image(src_path, dst_path, args.resize_height, args.horizontal_pad)

    output_labels.parent.mkdir(parents=True, exist_ok=True)
    with output_labels.open("wb") as f:
        pickle.dump({"ground_truth": ground_truth}, f)

    print(f"Processed IAM samples: {total}")
    print(f"Output images dir: {output_images}")
    print(f"Output labels: {output_labels}")
    if missing:
        print(f"Missing raw images: {len(missing)}")
        for path in missing[:20]:
            print(f"  missing: {path}")
        if len(missing) > 20:
            print("  ...")
    else:
        print("All split images found and processed.")


if __name__ == "__main__":
    main()
