import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import os
import sys
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import util.misc as utils
from datasets import build_dataset
from finetuning import build_model_main
from util.slconfig import DictAction, SLConfig


def parse_args():
    parser = argparse.ArgumentParser("Analyze CTC errors for DTLR checkpoints")
    parser.add_argument("--config_file", "-c", type=str, required=True)
    parser.add_argument("--dataset_file", type=str, default="mth1000")
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--split", type=str, default="val", choices=["train", "val", "test"])
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--num_workers", type=int, default=2)
    parser.add_argument("--max_samples", type=int, default=300)
    parser.add_argument("--new_class_embedding", action="store_true")
    parser.add_argument("--output_json", type=str, default="logs/error_analysis_summary.json")
    parser.add_argument("--output_cases", type=str, default="logs/error_analysis_cases.jsonl")
    parser.add_argument("--max_output_cases", type=int, default=200)
    parser.add_argument("--save_all_cases", action="store_true")
    parser.add_argument(
        "--blank_bias",
        type=float,
        default=0.0,
        help="Additive log-probability bias for the CTC blank token during decoding.",
    )
    parser.add_argument(
        "--nonblank_bias",
        type=float,
        default=0.0,
        help="Additive log-probability bias for all nonblank tokens during decoding.",
    )
    parser.add_argument(
        "--ratio_nonblank_bias",
        type=float,
        default=0.0,
        help=(
            "Additional nonblank log-probability bias applied only when "
            "orig_height / orig_width is inside the configured ratio range."
        ),
    )
    parser.add_argument("--ratio_min", type=float, default=1.5)
    parser.add_argument("--ratio_max", type=float, default=2.0)
    parser.add_argument(
        "--options",
        nargs="+",
        action=DictAction,
        help="Override config values, same format as finetuning.py --options.",
    )
    return parser.parse_args()


def load_cfg_to_args(args):
    cfg = SLConfig.fromfile(args.config_file)
    if args.options is not None:
        cfg.merge_from_dict(args.options)
    cfg_dict = cfg._cfg_dict.to_dict()
    base = vars(args).copy()
    for k, v in cfg_dict.items():
        if k not in base:
            base[k] = v
    for k, v in {
        "mode_chr": True,
        "amp": False,
        "eval": True,
        "distributed": False,
        "rank": 0,
        "world_size": 1,
        "local_rank": 0,
    }.items():
        if k not in base:
            base[k] = v
    return argparse.Namespace(**base)


def remove_duplicates(sequence: List[int]) -> List[int]:
    output = []
    prev = None
    for token in sequence:
        if token != prev and token != 0:
            output.append(token)
        prev = token
    return output


def labels_to_text(labels: List[int], charset) -> str:
    if not labels:
        return ""
    values = [charset[x] for x in labels]
    if values and isinstance(values[0], int):
        return " ".join(str(v) for v in values)
    return "".join(str(v) for v in values)


def levenshtein_ops(a: List[int], b: List[int]) -> Tuple[int, int, int, int]:
    # returns (distance, insertions, deletions, substitutions)
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    op = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i
        op[i][0] = "del"
    for j in range(1, m + 1):
        dp[0][j] = j
        op[0][j] = "ins"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                op[i][j] = "eq"
            else:
                cand = [
                    (dp[i - 1][j] + 1, "del"),
                    (dp[i][j - 1] + 1, "ins"),
                    (dp[i - 1][j - 1] + 1, "sub"),
                ]
                dp[i][j], op[i][j] = min(cand, key=lambda x: x[0])
    i, j = n, m
    ins = dels = subs = 0
    while i > 0 or j > 0:
        step = op[i][j]
        if step == "eq":
            i -= 1
            j -= 1
        elif step == "sub":
            subs += 1
            i -= 1
            j -= 1
        elif step == "del":
            dels += 1
            i -= 1
        elif step == "ins":
            ins += 1
            j -= 1
        else:
            break
    return dp[n][m], ins, dels, subs


def _adapt_class_head(model, charset_size, device):
    features_dim = model.class_embed[0].weight.data.shape[1]
    new_class_embed = nn.Linear(features_dim, charset_size)
    new_decoder_class_embed = nn.Linear(features_dim, charset_size)
    new_enc_out_class_embed = nn.Linear(features_dim, charset_size)

    if model.dec_pred_class_embed_share:
        class_embed_layerlist = [new_class_embed for _ in range(model.transformer.num_decoder_layers)]
    else:
        class_embed_layerlist = [nn.Linear(features_dim, charset_size) for _ in range(model.transformer.num_decoder_layers)]
    model.class_embed = nn.ModuleList(class_embed_layerlist).to(device)
    model.transformer.decoder.class_embed = new_decoder_class_embed.to(device)
    model.transformer.enc_out_class_embed = new_enc_out_class_embed.to(device)
    model.label_enc = nn.Embedding(charset_size + 1, features_dim).to(device)


def _load_compatible_state(model, checkpoint_model):
    clean_state = utils.clean_state_dict(checkpoint_model)
    model_state = model.state_dict()
    filtered = {}
    skipped = []
    for k, v in clean_state.items():
        if k in model_state and model_state[k].shape == v.shape:
            filtered[k] = v
        else:
            skipped.append(k)
    model.load_state_dict(filtered, strict=False)
    return skipped


@dataclass
class Totals:
    n: int = 0
    gt_chars: int = 0
    pred_chars: int = 0
    dist: int = 0
    ins: int = 0
    dels: int = 0
    subs: int = 0
    empty_pred: int = 0

    def add(self, gt_len, pred_len, dist, ins, dels, subs):
        self.n += 1
        self.gt_chars += gt_len
        self.pred_chars += pred_len
        self.dist += dist
        self.ins += ins
        self.dels += dels
        self.subs += subs
        self.empty_pred += int(pred_len == 0)

    def to_summary(self):
        return {
            "samples": self.n,
            "cer_micro": self.dist / max(self.gt_chars, 1),
            "avg_gt_len": self.gt_chars / max(self.n, 1),
            "avg_pred_len": self.pred_chars / max(self.n, 1),
            "pred_gt_len_ratio": self.pred_chars / max(self.gt_chars, 1),
            "empty_pred_rate": self.empty_pred / max(self.n, 1),
            "ins_rate": self.ins / max(self.gt_chars, 1),
            "del_rate": self.dels / max(self.gt_chars, 1),
            "sub_rate": self.subs / max(self.gt_chars, 1),
        }


def length_bin(gt_len):
    if gt_len == 1:
        return "1"
    if gt_len == 2:
        return "2"
    if gt_len <= 5:
        return "3-5"
    if gt_len <= 10:
        return "6-10"
    return "11+"


def apply_decode_calibration(pred_probs, target, cli):
    if (
        cli.blank_bias == 0.0
        and cli.nonblank_bias == 0.0
        and cli.ratio_nonblank_bias == 0.0
    ):
        return pred_probs

    scores = torch.log(pred_probs.clamp(min=1e-12))
    scores[..., 0] += cli.blank_bias
    scores[..., 1:] += cli.nonblank_bias

    if cli.ratio_nonblank_bias != 0.0 and "orig_size" in target:
        orig_size = target["orig_size"]
        if torch.is_tensor(orig_size):
            h, w = orig_size.detach().cpu().tolist()
        else:
            h, w = orig_size
        ratio = float(h) / max(float(w), 1.0)
        if float(cli.ratio_min) < ratio <= float(cli.ratio_max):
            scores[..., 1:] += cli.ratio_nonblank_bias

    return scores


def main():
    cli = parse_args()
    args = load_cfg_to_args(cli)
    device = torch.device(cli.device if torch.cuda.is_available() and "cuda" in cli.device else "cpu")

    dataset = build_dataset(image_set=cli.split, args=args)
    args.charset = dataset.charset
    model, criterion, _ = build_model_main(args)
    model.to(device)
    model.eval()
    criterion.eval()

    if cli.new_class_embedding:
        _adapt_class_head(model, len(dataset.charset), device)

    ckpt = torch.load(cli.checkpoint, map_location="cpu")
    ckpt_model = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
    skipped = _load_compatible_state(model, ckpt_model)
    print(f"Loaded checkpoint with {len(skipped)} skipped keys")

    loader = DataLoader(
        dataset,
        batch_size=1,
        shuffle=False,
        num_workers=cli.num_workers,
        collate_fn=utils.collate_fn,
    )

    totals = Totals()
    by_len_bin = defaultdict(Totals)
    by_len_exact = defaultdict(Totals)
    cases = []

    with torch.no_grad():
        for i, (samples, targets) in enumerate(loader):
            if i >= cli.max_samples:
                break
            samples = samples.to(device)
            targets = [{k: (v.to(device) if torch.is_tensor(v) else v) for k, v in t.items()} for t in targets]
            outputs = model(samples)
            _, pred_probs, _ = criterion.loss_CTC(outputs, targets, None, None, return_preds=True)
            decode_scores = apply_decode_calibration(pred_probs, targets[0], cli)

            pred_tokens = decode_scores.argmax(-1)[0].tolist()
            pred_tokens = remove_duplicates(pred_tokens)
            pred_labels = [t - 1 for t in pred_tokens if 1 <= t <= len(dataset.charset)]
            gt_labels = [int(x) for x in targets[0]["labels"].tolist()]

            dist, ins, dels, subs = levenshtein_ops(gt_labels, pred_labels)
            cer = dist / max(len(gt_labels), 1)
            gt_text = labels_to_text(gt_labels, dataset.charset)
            pred_text = labels_to_text(pred_labels, dataset.charset)

            gt_len = len(gt_labels)
            pred_len = len(pred_labels)
            totals.add(gt_len, pred_len, dist, ins, dels, subs)
            by_len_bin[length_bin(gt_len)].add(gt_len, pred_len, dist, ins, dels, subs)
            by_len_exact[str(gt_len)].add(gt_len, pred_len, dist, ins, dels, subs)

            cases.append(
                {
                    "idx": i,
                    "gt_len": gt_len,
                    "pred_len": pred_len,
                    "cer": cer,
                    "ins": ins,
                    "del": dels,
                    "sub": subs,
                    "gt": gt_text,
                    "pred": pred_text,
                }
            )

    cases_sorted = sorted(cases, key=lambda x: x["cer"], reverse=True)
    summary = totals.to_summary()
    summary.update({
        "by_gt_len_bin": {
            key: by_len_bin[key].to_summary()
            for key in ["1", "2", "3-5", "6-10", "11+"]
            if by_len_bin[key].n > 0
        },
        "by_gt_len_exact": {
            key: value.to_summary()
            for key, value in sorted(by_len_exact.items(), key=lambda item: int(item[0]))
        },
        "skipped_keys": len(skipped),
    })

    out_json = Path(cli.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    out_cases = Path(cli.output_cases)
    out_cases.parent.mkdir(parents=True, exist_ok=True)
    output_cases = cases_sorted if cli.save_all_cases else cases_sorted[: cli.max_output_cases]
    with out_cases.open("w", encoding="utf-8") as f:
        for row in output_cases:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved summary -> {out_json}")
    if cli.save_all_cases:
        print(f"Saved all {len(output_cases)} cases sorted by CER -> {out_cases}")
    else:
        print(f"Saved worst {len(output_cases)} cases -> {out_cases}")


if __name__ == "__main__":
    main()
