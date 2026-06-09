#!/usr/bin/env python3
"""Audit DTLR experiment logs for paper-readiness.

This is a read-only helper. It scans ``logs/*`` and reports:

1. runs with test metric JSON files;
2. runs with validation CER in ``log.txt``;
3. checkpointed runs that still lack test postprocess JSON files.

It does not evaluate checkpoints or modify result files.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TEST_PATTERNS = (
    "micro_test*.json",
    "ctc_error_summary_test*.json",
)
VALID_PATTERNS = (
    "micro_valid*.json",
    "ctc_error_summary_valid*.json",
    "decode_bias_sweep_valid*.json",
)


@dataclass(frozen=True)
class ValidationRow:
    run: Path
    cer: float
    epoch: int | None
    blank_ratio: float | None
    rows: int


@dataclass(frozen=True)
class MetricRow:
    path: Path
    cer: float
    samples: int | None
    ar: float | None
    cr: float | None
    blank_bias: float | None
    nonblank_bias: float | None


@dataclass(frozen=True)
class PostprocessCandidate:
    run: Path
    checkpoint: str
    validation: ValidationRow | None
    has_valid_json: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Audit DTLR experiment run artifacts.")
    parser.add_argument("--logs-root", default="logs")
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument(
        "--filter",
        default="",
        help="Only report runs whose path contains this substring.",
    )
    parser.add_argument(
        "--max-valid-cer",
        type=float,
        default=None,
        help="Only list missing-postprocess candidates with best validation CER at or below this value.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def micro_ar(row: dict[str, Any]) -> float | None:
    if "micro_ar" in row:
        return as_float(row["micro_ar"])
    cer = as_float(row.get("micro_cer", row.get("cer_micro")))
    if cer is not None:
        return 1.0 - cer
    return None


def micro_cr(row: dict[str, Any]) -> float | None:
    if "micro_cr" in row:
        return as_float(row["micro_cr"])
    del_rate = as_float(row.get("del_rate"))
    sub_rate = as_float(row.get("sub_rate"))
    if del_rate is not None and sub_rate is not None:
        return 1.0 - del_rate - sub_rate
    return None


def metric_from_summary(path: Path, row: dict[str, Any]) -> MetricRow | None:
    cer = as_float(row.get("micro_cer", row.get("cer_micro")))
    if cer is None:
        return None
    samples = row.get("samples", row.get("evaluated_samples"))
    return MetricRow(
        path=path,
        cer=cer,
        samples=int(samples) if samples is not None else None,
        ar=micro_ar(row),
        cr=micro_cr(row),
        blank_bias=as_float(row.get("blank_bias")),
        nonblank_bias=as_float(row.get("nonblank_bias")),
    )


def best_from_sweep(path: Path, data: Any) -> MetricRow | None:
    candidates: list[dict[str, Any]] = []
    if isinstance(data, list):
        candidates = [item for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        if isinstance(data.get("best"), dict):
            candidates.append(data["best"])
        for key in ("results", "rows", "sweep", "grid"):
            value = data.get(key)
            if isinstance(value, list):
                candidates.extend(item for item in value if isinstance(item, dict))

    best: MetricRow | None = None
    for row in candidates:
        metric = metric_from_summary(path, row)
        if metric is None:
            continue
        if best is None or metric.cer < best.cer:
            best = metric
    return best


def scan_metric_json(run_dir: Path, patterns: tuple[str, ...]) -> list[MetricRow]:
    rows: list[MetricRow] = []
    for pattern in patterns:
        for path in sorted(run_dir.glob(pattern)):
            data = load_json(path)
            if isinstance(data, dict):
                metric = metric_from_summary(path, data)
                if metric is not None:
                    rows.append(metric)
                    continue
            metric = best_from_sweep(path, data)
            if metric is not None:
                rows.append(metric)
    return rows


def scan_validation_log(run_dir: Path) -> ValidationRow | None:
    log_path = run_dir / "log.txt"
    if not log_path.exists():
        return None
    best: tuple[float, int | None, float | None] | None = None
    rows = 0
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        cer = as_float(row.get("test_cer_oracle_direction"))
        if cer is None:
            continue
        rows += 1
        epoch_value = row.get("epoch")
        epoch = int(epoch_value) if epoch_value is not None else None
        blank_ratio = as_float(row.get("test_blank_pred_ratio_unscaled"))
        if best is None or cer < best[0]:
            best = (cer, epoch, blank_ratio)
    if best is None:
        return None
    return ValidationRow(
        run=run_dir,
        cer=best[0],
        epoch=best[1],
        blank_ratio=best[2],
        rows=rows,
    )


def pct(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{100.0 * value:.2f}"


def bias_text(row: MetricRow) -> str:
    if row.blank_bias is None and row.nonblank_bias is None:
        return "-"
    return f"{row.blank_bias:g}/{row.nonblank_bias:g}"


def print_metric_rows(title: str, rows: list[MetricRow], top_k: int) -> None:
    print(f"\n## {title}")
    if not rows:
        print("(none)")
        return
    print("CER\tAR\tCR\tSamples\tBias\tPath")
    for row in sorted(rows, key=lambda item: item.cer)[:top_k]:
        print(
            f"{pct(row.cer)}\t{pct(row.ar)}\t{pct(row.cr)}\t"
            f"{row.samples if row.samples is not None else '-'}\t"
            f"{bias_text(row)}\t{row.path}"
        )


def print_validation_rows(rows: list[ValidationRow], top_k: int) -> None:
    print("\n## Best Validation CER From log.txt")
    if not rows:
        print("(none)")
        return
    print("ValidCER\tEpoch\tBlankRatio\tRows\tRun")
    for row in sorted(rows, key=lambda item: item.cer)[:top_k]:
        blank = f"{row.blank_ratio:.6f}" if row.blank_ratio is not None else "-"
        print(
            f"{row.cer:.6f}\t{row.epoch if row.epoch is not None else '-'}\t"
            f"{blank}\t{row.rows}\t{row.run}"
        )


def print_missing_postprocess(
    run_dirs: list[Path],
    top_k: int,
    max_valid_cer: float | None,
) -> None:
    print("\n## Checkpointed Runs Missing Test JSON")
    print("Run\tCheckpoint\tValidCER\tHasValidJSON")
    candidates: list[PostprocessCandidate] = []
    for run_dir in run_dirs:
        if not (run_dir / "checkpoint_best_regular.pth").exists():
            continue
        if scan_metric_json(run_dir, TEST_PATTERNS):
            continue
        validation = scan_validation_log(run_dir)
        if (
            max_valid_cer is not None
            and validation is not None
            and validation.cer > max_valid_cer
        ):
            continue
        valid_json = bool(scan_metric_json(run_dir, VALID_PATTERNS))
        candidates.append(
            PostprocessCandidate(
                run=run_dir,
                checkpoint="checkpoint_best_regular.pth",
                validation=validation,
                has_valid_json=valid_json,
            )
        )

    def sort_key(candidate: PostprocessCandidate) -> tuple[int, float, str]:
        if candidate.validation is None:
            return (1, float("inf"), str(candidate.run))
        return (0, candidate.validation.cer, str(candidate.run))

    count = 0
    for candidate in sorted(candidates, key=sort_key):
        valid_cer = (
            f"{candidate.validation.cer:.6f}" if candidate.validation is not None else "-"
        )
        print(
            f"{candidate.run}\t{candidate.checkpoint}\t"
            f"{valid_cer}\t{candidate.has_valid_json}"
        )
        count += 1
        if count >= top_k:
            break
    if count == 0:
        print("(none)")


def main() -> int:
    args = parse_args()
    logs_root = Path(args.logs_root)
    run_dirs = [path for path in sorted(logs_root.iterdir()) if path.is_dir()]
    if args.filter:
        run_dirs = [path for path in run_dirs if args.filter in str(path)]

    test_rows: list[MetricRow] = []
    validation_rows: list[ValidationRow] = []
    for run_dir in run_dirs:
        test_rows.extend(scan_metric_json(run_dir, TEST_PATTERNS))
        validation = scan_validation_log(run_dir)
        if validation is not None:
            validation_rows.append(validation)

    print(f"logs_root={logs_root}")
    print(f"run_dirs={len(run_dirs)}")
    print_metric_rows("Test Metric JSON Rows", test_rows, args.top_k)
    print_validation_rows(validation_rows, args.top_k)
    print_missing_postprocess(run_dirs, args.top_k, args.max_valid_cer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
