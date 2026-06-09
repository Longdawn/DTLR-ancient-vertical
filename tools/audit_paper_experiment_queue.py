#!/usr/bin/env python3
"""Audit the remaining paper experiment queue.

This read-only helper checks the four GPU0 queue experiments prepared under
``logs/*_0608`` and reports whether each run is ready to launch, needs
postprocess, or has complete clean/bias JSON artifacts.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QueueItem:
    name: str
    purpose: str
    run_dir: Path
    train_script: Path
    post_script: Path


QUEUE: tuple[QueueItem, ...] = (
    QueueItem(
        name="mthv2_length_balance",
        purpose="short-column sampling probe",
        run_dir=Path("logs/mthv2_length_balance_v2_resume_1000_0608"),
        train_script=Path(
            "logs/mthv2_length_balance_v2_resume_1000_0608/"
            "run_length_balance_probe_0608.sh"
        ),
        post_script=Path(
            "logs/mthv2_length_balance_v2_resume_1000_0608/"
            "run_postprocess_after_finish_0608.sh"
        ),
    ),
    QueueItem(
        name="hdrc_no_structure",
        purpose="HDRC no-localization lower-bound control",
        run_dir=Path("logs/hdrc_no_structure_ctc_full_0608"),
        train_script=Path(
            "logs/hdrc_no_structure_ctc_full_0608/run_hdrc_no_structure_0608.sh"
        ),
        post_script=Path(
            "logs/hdrc_no_structure_ctc_full_0608/"
            "run_postprocess_after_finish_0608.sh"
        ),
    ),
    QueueItem(
        name="mthv2_ctc_count003",
        purpose="MTHv2 weak expected-count sanity check",
        run_dir=Path("logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count003_0608"),
        train_script=Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count003_0608/"
            "run_full_ctc_count003_0608.sh"
        ),
        post_script=Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count003_0608/"
            "run_postprocess_after_finish_0608.sh"
        ),
    ),
    QueueItem(
        name="hdrc_ctc_count003",
        purpose="HDRC weak expected-count sanity check",
        run_dir=Path("logs/hdrc_qbudget_full_ctc_count003_0608"),
        train_script=Path(
            "logs/hdrc_qbudget_full_ctc_count003_0608/"
            "run_full_ctc_count003_0608.sh"
        ),
        post_script=Path(
            "logs/hdrc_qbudget_full_ctc_count003_0608/"
            "run_postprocess_after_finish_0608.sh"
        ),
    ),
)

MTHV2_LENGTH_BALANCE_VALID_CER_TARGET = 0.11879202286282202
MTHV2_COUNT001_TEST_BIAS_CER = 0.0325
MTHV2_QBUDGET_TEST_BIAS_CER = 0.0331
HDRC_QBUDGET_TEST_BIAS_CER = 0.0656
HDRC_ORIGINAL_MAINLINE_TEST_BIAS_CER = 0.0930


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Audit the paper experiment queue.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--format",
        choices=["tsv", "json"],
        default="tsv",
        help="Output format. Default keeps the human-readable TSV table.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def metric_summary(path: Path | None) -> str:
    if path is None or not path.exists():
        return "-"
    data = load_json(path)
    if not isinstance(data, dict):
        return path.name

    cer = as_float(data.get("micro_cer", data.get("cer_micro")))
    ar = as_float(data.get("micro_ar"))
    cr = as_float(data.get("micro_cr"))
    if ar is None and cer is not None:
        ar = 1.0 - cer
    if cr is None:
        del_rate = as_float(data.get("del_rate"))
        sub_rate = as_float(data.get("sub_rate"))
        if del_rate is not None and sub_rate is not None:
            cr = 1.0 - del_rate - sub_rate

    if cer is None:
        return path.name
    ar_text = f"{100.0 * ar:.2f}" if ar is not None else "-"
    cr_text = f"{100.0 * cr:.2f}" if cr is not None else "-"
    return f"CER={100.0 * cer:.2f}, AR={ar_text}, CR={cr_text}"


def metric_cer(path: Path | None) -> float | None:
    if path is None or not path.exists():
        return None
    data = load_json(path)
    if not isinstance(data, dict):
        return None
    return as_float(data.get("micro_cer", data.get("cer_micro")))


def length_bucket_summary(path: Path | None) -> str:
    if path is None or not path.exists():
        return "-"
    data = load_json(path)
    if not isinstance(data, dict):
        return "-"
    buckets = data.get("by_gt_len_bin")
    if not isinstance(buckets, dict):
        return "-"

    parts = []
    for key in ("1", "2", "3-5", "6-10", "11+"):
        row = buckets.get(key)
        if not isinstance(row, dict):
            continue
        cer = as_float(row.get("micro_cer", row.get("cer_micro")))
        if cer is None:
            continue
        parts.append(f"{key}={100.0 * cer:.2f}")
    return ", ".join(parts) if parts else "-"


def best_sweep_summary(path: Path | None) -> str:
    if path is None or not path.exists():
        return "-"
    data = load_json(path)
    rows = data if isinstance(data, list) else []
    rows = [row for row in rows if isinstance(row, dict)]
    if not rows:
        return path.name
    best = min(
        rows,
        key=lambda row: as_float(row.get("micro_cer", row.get("cer_micro")))
        if as_float(row.get("micro_cer", row.get("cer_micro"))) is not None
        else float("inf"),
    )
    cer = as_float(best.get("micro_cer", best.get("cer_micro")))
    blank = best.get("blank_bias", "-")
    nonblank = best.get("nonblank_bias", "-")
    if cer is None:
        return path.name
    return f"CER={100.0 * cer:.2f}, bias={blank}/{nonblank}"


def gate_recommendation(
    item: QueueItem,
    status: str,
    valid_clean: Path | None,
    test_bias: Path | None,
) -> str:
    if status in {"BROKEN_SETUP", "READY_TO_RUN", "TRAINING_OR_INCOMPLETE", "NEEDS_POSTPROCESS"}:
        return "NOT_EVALUABLE_YET"

    valid_clean_cer = metric_cer(valid_clean)
    test_bias_cer = metric_cer(test_bias)

    if item.name == "mthv2_length_balance":
        if valid_clean_cer is None:
            return "NEEDS_VALID_METRIC"
        if valid_clean_cer < MTHV2_LENGTH_BALANCE_VALID_CER_TARGET:
            return "CANDIDATE_IF_SHORT_BUCKETS_AND_LONG_BUCKET_OK"
        return "INTERNAL_ONLY_UNLESS_BUCKETS_EXPLAIN_FAILURE"

    if item.name == "hdrc_no_structure":
        return "LOWER_BOUND_CONTROL_ONLY"

    if item.name == "mthv2_ctc_count003":
        if test_bias_cer is None:
            return "NEEDS_TEST_BIAS_METRIC"
        if test_bias_cer <= MTHV2_COUNT001_TEST_BIAS_CER:
            return "CAN_COMPETE_WITH_COUNT001"
        if test_bias_cer <= MTHV2_QBUDGET_TEST_BIAS_CER:
            return "SAFER_OPTIONAL_THAN_COUNT001_ONLY_IF_HDRC_OK"
        return "INTERNAL_ONLY_WEAKER_THAN_MTHV2_QBUDGET"

    if item.name == "hdrc_ctc_count003":
        if test_bias_cer is None:
            return "NEEDS_TEST_BIAS_METRIC"
        if test_bias_cer <= HDRC_QBUDGET_TEST_BIAS_CER:
            return "CROSS_DATASET_COUNT_CANDIDATE"
        if test_bias_cer <= HDRC_ORIGINAL_MAINLINE_TEST_BIAS_CER:
            return "DO_NOT_OVERCLAIM_OPTIONAL_ONLY"
        return "INTERNAL_ONLY_HDRC_REGRESSION"

    return "REVIEW"


def latest_existing(paths: list[Path]) -> Path | None:
    for path in sorted(paths, reverse=True):
        if path.exists():
            return path
    return None


def audit_item(root: Path, item: QueueItem) -> dict[str, str]:
    run_dir = root / item.run_dir
    checkpoint = run_dir / "checkpoint_best_regular.pth"
    log_path = run_dir / "log.txt"
    valid_clean = latest_existing(list(run_dir.glob("micro_valid_clean_*.json")))
    test_clean = latest_existing(list(run_dir.glob("micro_test_clean_*.json")))
    valid_sweep = latest_existing(list(run_dir.glob("decode_bias_sweep_valid_*.json")))
    test_bias = latest_existing(list(run_dir.glob("micro_test_bias_*.json")))

    missing: list[str] = []
    for label, path in (
        ("train_script", root / item.train_script),
        ("post_script", root / item.post_script),
    ):
        if not path.exists():
            missing.append(label)
    if not checkpoint.exists():
        missing.append("checkpoint")
    if valid_clean is None:
        missing.append("valid_clean")
    if test_clean is None:
        missing.append("test_clean")
    if valid_sweep is None:
        missing.append("valid_sweep")
    if test_bias is None:
        missing.append("test_bias")

    if not (root / item.train_script).exists() or not (root / item.post_script).exists():
        status = "BROKEN_SETUP"
    elif checkpoint.exists() and not any(
        key in missing for key in ("valid_clean", "test_clean", "valid_sweep", "test_bias")
    ):
        status = "PAPER_READY_ARTIFACTS"
    elif checkpoint.exists():
        status = "NEEDS_POSTPROCESS"
    elif log_path.exists():
        status = "TRAINING_OR_INCOMPLETE"
    else:
        status = "READY_TO_RUN"

    if status == "BROKEN_SETUP":
        decision = "FIX_SCRIPTS"
    elif status == "READY_TO_RUN":
        decision = "RUN_NEXT"
    elif status == "TRAINING_OR_INCOMPLETE":
        decision = "CHECK_LOG_OR_RESUME"
    elif status == "NEEDS_POSTPROCESS":
        decision = "RUN_POSTPROCESS"
    elif item.name == "mthv2_length_balance":
        decision = "REVIEW_SHORT_BUCKETS_BEFORE_PAPER"
    elif item.name == "hdrc_no_structure":
        decision = "USE_ONLY_AS_LOWER_BOUND_CONTROL"
    elif item.name == "mthv2_ctc_count003":
        decision = "COMPARE_TO_MTHV2_COUNT001"
    elif item.name == "hdrc_ctc_count003":
        decision = "KEEP_ONLY_IF_HDRC_DOES_NOT_REGRESS"
    else:
        decision = "REVIEW"
    gate = gate_recommendation(item, status, valid_clean, test_bias)

    return {
        "name": item.name,
        "purpose": item.purpose,
        "status": status,
        "decision": decision,
        "gate": gate,
        "missing": ",".join(missing) if missing else "-",
        "valid_clean": metric_summary(valid_clean),
        "test_clean": metric_summary(test_clean),
        "valid_sweep": best_sweep_summary(valid_sweep),
        "test_bias": metric_summary(test_bias),
        "valid_buckets": length_bucket_summary(valid_clean),
        "test_buckets": length_bucket_summary(test_clean),
        "run_dir": str(item.run_dir),
    }


def audit_queue(root: Path, queue: list[QueueItem] | tuple[QueueItem, ...] = QUEUE) -> list[dict[str, str]]:
    return [audit_item(root, item) for item in queue]


def rows_to_json(root: Path, rows: list[dict[str, str]]) -> str:
    payload = {
        "root": str(root),
        "rows": rows,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def print_tsv(root: Path, rows: list[dict[str, str]]) -> None:
    print(f"root={root}")
    print(
        "Name\tPurpose\tStatus\tDecision\tGate\tMissing\tValidClean\tTestClean\t"
        "ValidSweep\tTestBias\tValidBuckets\tTestBuckets\tRunDir"
    )
    for row in rows:
        print(
            f"{row['name']}\t{row['purpose']}\t{row['status']}\t"
            f"{row['decision']}\t{row['gate']}\t{row['missing']}\t"
            f"{row['valid_clean']}\t{row['test_clean']}\t"
            f"{row['valid_sweep']}\t{row['test_bias']}\t"
            f"{row['valid_buckets']}\t{row['test_buckets']}\t{row['run_dir']}"
        )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    rows = audit_queue(root)
    if args.format == "json":
        print(rows_to_json(root, rows))
    else:
        print_tsv(root, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
