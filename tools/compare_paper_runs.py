#!/usr/bin/env python3
"""Aggregate paper metrics reports into a unified markdown/json comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_report_path(item: str) -> Path:
    path = Path(item)
    if path.is_dir():
        candidate = path / "paper_metrics_report.json"
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"missing paper_metrics_report.json under {path}")
    if path.is_file():
        return path
    raise FileNotFoundError(f"cannot resolve report path: {item}")


def fmt_float(value: Any, digits: int = 4) -> str:
    if value is None:
        return "-"
    return f"{float(value):.{digits}f}"


def bucket_metric(report: dict[str, Any], bucket: str, key: str) -> Any:
    return report.get("len_bins", {}).get(bucket, {}).get(key)


def build_rows(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report in reports:
        rows.append(
            {
                "run_dir": report["run_dir"],
                "best_epoch": report.get("best_epoch"),
                "best_test_cer_oracle_direction": report.get(
                    "best_test_cer_oracle_direction"
                ),
                "best_test_ar_assuming_1_minus_cer": report.get(
                    "best_test_ar_assuming_1_minus_cer"
                ),
                "best_test_wer_oracle_direction": report.get(
                    "best_test_wer_oracle_direction"
                ),
                "best_test_blank_pred_ratio": report.get("best_test_blank_pred_ratio"),
                "ctc_summary_cer_micro": report.get("ctc_summary_cer_micro"),
                "ctc_summary_ar_assuming_1_minus_cer": report.get(
                    "ctc_summary_ar_assuming_1_minus_cer"
                ),
                "ctc_summary_empty_pred_rate": report.get("ctc_summary_empty_pred_rate"),
                "ctc_summary_pred_gt_len_ratio": report.get(
                    "ctc_summary_pred_gt_len_ratio"
                ),
                "len1_cer": bucket_metric(report, "1", "cer_micro"),
                "len1_empty": bucket_metric(report, "1", "empty_pred_rate"),
                "len2_cer": bucket_metric(report, "2", "cer_micro"),
                "len2_empty": bucket_metric(report, "2", "empty_pred_rate"),
                "len3_5_cer": bucket_metric(report, "3-5", "cer_micro"),
                "len6_10_cer": bucket_metric(report, "6-10", "cer_micro"),
                "len11p_cer": bucket_metric(report, "11+", "cer_micro"),
            }
        )
    return rows


def sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            float("inf")
            if row.get("best_test_cer_oracle_direction") is None
            else row["best_test_cer_oracle_direction"]
        ),
    )


def make_markdown(rows: list[dict[str, Any]], baseline_run_dir: str | None) -> str:
    lines = [
        "# MTH1000 Paper Run Comparison",
        "",
        "> `best_test_*` comes from training log best epoch. `ctc_summary_*` comes from fixed valid-set error summary.",
        "",
    ]
    if baseline_run_dir:
        lines.extend(
            [
                f"Baseline run: `{baseline_run_dir}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Core Table",
            "",
            "| Run | Best epoch | Best test CER | Best test AR~1-CER | Best WER | Blank pred ratio | CTC summary CER | CTC summary AR~1-CER | Empty pred rate | Len=1 CER | Len=1 empty | Len=2 CER | Len=2 empty | Len>=11 CER |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["run_dir"],
                    str(row.get("best_epoch", "-")),
                    fmt_float(row.get("best_test_cer_oracle_direction")),
                    fmt_float(row.get("best_test_ar_assuming_1_minus_cer")),
                    fmt_float(row.get("best_test_wer_oracle_direction")),
                    fmt_float(row.get("best_test_blank_pred_ratio")),
                    fmt_float(row.get("ctc_summary_cer_micro")),
                    fmt_float(row.get("ctc_summary_ar_assuming_1_minus_cer")),
                    fmt_float(row.get("ctc_summary_empty_pred_rate")),
                    fmt_float(row.get("len1_cer")),
                    fmt_float(row.get("len1_empty")),
                    fmt_float(row.get("len2_cer")),
                    fmt_float(row.get("len2_empty")),
                    fmt_float(row.get("len11p_cer")),
                ]
            )
            + " |"
        )

    if baseline_run_dir:
        baseline = next((row for row in rows if row["run_dir"] == baseline_run_dir), None)
        if baseline is not None:
            lines.extend(
                [
                    "",
                    "## Delta Vs Baseline",
                    "",
                    "| Run | Delta best CER | Delta CTC summary CER | Delta len=1 CER | Delta len=2 CER | Delta len>=11 CER |",
                    "| --- | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for row in rows:
                def delta(key: str) -> str:
                    if row.get(key) is None or baseline.get(key) is None:
                        return "-"
                    return f"{row[key] - baseline[key]:+.4f}"

                lines.append(
                    "| "
                    + " | ".join(
                        [
                            row["run_dir"],
                            delta("best_test_cer_oracle_direction"),
                            delta("ctc_summary_cer_micro"),
                            delta("len1_cer"),
                            delta("len2_cer"),
                            delta("len11p_cer"),
                        ]
                    )
                    + " |"
                )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Lower CER / WER / empty-rate is better.",
            "- `AR~1-CER` is a temporary proxy, not a confirmed MTHv2 paper metric.",
            "- Prefer selecting the paper mainline by `ctc_summary_cer_micro` plus short-text buckets, not by train loss.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Run directories or paper_metrics_report.json files.",
    )
    parser.add_argument(
        "--baseline_run_dir",
        default=None,
        help="Run directory string used as baseline in delta table.",
    )
    parser.add_argument("--output_json", default=None)
    parser.add_argument("--output_md", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports = [load_report(resolve_report_path(item)) for item in args.inputs]
    rows = sort_rows(build_rows(reports))
    payload = {
        "baseline_run_dir": args.baseline_run_dir,
        "rows": rows,
    }
    md = make_markdown(rows, args.baseline_run_dir)

    output_json = (
        Path(args.output_json)
        if args.output_json
        else Path("logs") / "mth1000_paper_run_comparison.json"
    )
    output_md = (
        Path(args.output_md)
        if args.output_md
        else Path("logs") / "mth1000_paper_run_comparison.md"
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    output_md.write_text(md, encoding="utf-8")
    print(f"Saved JSON -> {output_json}")
    print(f"Saved Markdown -> {output_md}")


if __name__ == "__main__":
    main()
