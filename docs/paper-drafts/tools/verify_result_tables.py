#!/usr/bin/env python3
"""Static consistency checks for SAQT paper result tables.

This script does not run model evaluation. It verifies that paper-facing table
rows match the stored JSON metric artifacts after rounding AR/CR to two
percentage points.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Row:
    table: str
    name: str
    path: str
    samples: int
    ar: str
    cr: str
    blank_bias: float | None = None
    nonblank_bias: float | None = None


ROWS: list[Row] = [
    # Main SAQT results.
    Row("main", "MTHv2 direct", "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_clean_0608.json", 10455, "96.33", "96.50", 0.0, 0.0),
    Row("main", "MTHv2 calibrated", "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_bias_b-20_nb08_0608.json", 10455, "96.75", "97.00", -2.0, 0.8),
    Row("main", "HDRC direct", "logs/hdrc_qbudget_full_0607/micro_test_clean_0607.json", 3381, "91.50", "91.64", 0.0, 0.0),
    Row("main", "HDRC calibrated", "logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json", 3381, "93.44", "94.36", -2.0, 1.0),

    # Adapted scene-text recognizer baselines used in the paper table.
    Row("baseline", "MTHv2 CRNN", "/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_metrics.json", 10455, "95.51", "95.63"),
    Row("baseline", "MTHv2 SVTR-tiny", "/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_metrics.json", 10455, "95.56", "95.68"),
    Row("baseline", "MTHv2 SVTR-small", "/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530/svtr_small_k3_epoch29_test_metrics.json", 10455, "95.34", "95.44"),
    Row("baseline", "MTHv2 SVTR-L", "/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601/svtr_large_k3_officialgeom_epoch29_test_metrics.json", 10455, "95.16", "95.26"),
    Row("baseline", "MTHv2 ABINet", "/home/ubuntu/mmocr/work_dirs/eval_mthv2_abinet_k3_epoch19_test_0603_gpu/abinet_k3_epoch19_test_metrics.json", 10455, "90.75", "90.91"),
    Row("baseline", "MTHv2 SAR", "/home/ubuntu/mmocr/work_dirs/eval_mthv2_sar_k3_768_epoch20_test_0604/sar_k3_epoch20_test_metrics.json", 10455, "73.20", "87.65"),
    Row("baseline", "HDRC CRNN", "/home/ubuntu/mmocr/work_dirs/eval_hdrc_crnn_k3_best_epoch29_test_0603/hdrc_crnn_k3_epoch29_test_metrics.json", 3381, "84.91", "85.21"),
    Row("baseline", "HDRC SVTR-tiny", "/home/ubuntu/mmocr/work_dirs/eval_hdrc_svtr_tiny_k3_epoch30_test_0603/hdrc_svtr_tiny_k3_epoch30_test_metrics.json", 3381, "83.71", "83.89"),
    Row("baseline", "HDRC SVTR-L", "/home/ubuntu/mmocr/work_dirs/eval_hdrc_svtr_large_k3_officialgeom_epoch29_test_0603/hdrc_svtr_large_k3_officialgeom_epoch29_test_metrics.json", 3381, "78.16", "78.43"),
    Row("baseline", "HDRC ABINet", "/home/ubuntu/mmocr/work_dirs/eval_hdrc_abinet_k3_epoch19_test_0603/hdrc_abinet_k3_epoch19_test_metrics.json", 3381, "77.61", "77.84"),
    Row("baseline", "HDRC SAR", "/home/ubuntu/mmocr/work_dirs/eval_hdrc_sar_k3_768_epoch20_test_0604/hdrc_sar_k3_768_epoch20_test_metrics.json", 3381, "70.74", "73.24"),

    # Query budget and expected-count ablations.
    Row("qbudget", "MTHv2 w/o qbudget direct", "logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_test_clean_0528.json", 10455, "95.53", "95.71"),
    Row("qbudget", "MTHv2 w/o qbudget calibrated", "logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_test_bias_b-20_nb10_0528.json", 10455, "96.10", "96.37"),
    Row("qbudget", "MTHv2 qbudget direct", "logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_clean_0603.json", 10455, "96.17", "96.29", 0.0, 0.0),
    Row("qbudget", "MTHv2 qbudget calibrated", "logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_bias_b-20_nb08_0603.json", 10455, "96.69", "96.90", -2.0, 0.8),
    Row("expected-count", "MTHv2 count direct", "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_clean_0608.json", 10455, "96.33", "96.50", 0.0, 0.0),
    Row("expected-count", "MTHv2 count calibrated", "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_bias_b-20_nb08_0608.json", 10455, "96.75", "97.00", -2.0, 0.8),

    # HDRC variant, localization, charset, and training-stage ablations.
    Row("hdrc-qbudget", "HDRC main direct", "logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_clean_0527.json", 3381, "89.99", "90.33"),
    Row("hdrc-qbudget", "HDRC main calibrated", "logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_bias_b-20_nb04_0527.json", 3381, "90.70", "91.80"),
    Row("localization", "MTHv2 no-localization direct", "logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0606.json", 10455, "0.00", "0.00", 0.0, 0.0),
    Row("localization", "MTHv2 no-localization calibrated", "logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_b-20_nb04_0606.json", 10455, "0.11", "0.16", -2.0, 0.4),
    Row("charset", "HDRC random direct", "logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.json", 3381, "81.01", "81.41", 0.0, 0.0),
    Row("charset", "HDRC random calibrated", "logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_b-12_nb10_0605.json", 3381, "82.72", "83.97", -1.2, 1.0),
    Row("stage", "MTHv2 head direct", "logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_clean_0607.json", 10455, "93.00", "93.42", 0.0, 0.0),
    Row("stage", "MTHv2 head calibrated", "logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_bias_bm08_nb10_0607.json", 10455, "93.83", "95.03", -0.8, 1.0),
    Row("stage", "HDRC head direct", "logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_clean_0607.json", 3381, "82.28", "82.68", 0.0, 0.0),
    Row("stage", "HDRC head calibrated", "logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_bias_b-20_nb04_0607.json", 3381, "85.97", "89.72", -2.0, 0.4),
]


def resolve_path(path: str) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return REPO_ROOT / p


def pct2(value: float) -> str:
    return f"{value * 100.0:.2f}"


def get_ar_cr(data: dict) -> tuple[str, str]:
    if "micro_ar" in data and "micro_cr" in data:
        return pct2(float(data["micro_ar"])), pct2(float(data["micro_cr"]))
    if "cer_micro" not in data:
        raise KeyError("missing both micro_ar/micro_cr and cer_micro")
    ins = float(data.get("ins_rate", 0.0))
    dele = float(data.get("del_rate", 0.0))
    sub = float(data.get("sub_rate", 0.0))
    ar = 1.0 - (ins + dele + sub)
    cr = 1.0 - (dele + sub)
    return pct2(ar), pct2(cr)


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    checked = 0

    for row in ROWS:
        path = resolve_path(row.path)
        if not path.exists():
            failures.append(f"{row.table}:{row.name}: missing JSON {path}")
            continue

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        checked += 1
        samples = int(data.get("samples", data.get("evaluated_samples", -1)))
        if samples != row.samples:
            failures.append(
                f"{row.table}:{row.name}: samples {samples} != expected {row.samples}"
            )

        try:
            ar, cr = get_ar_cr(data)
        except Exception as exc:  # noqa: BLE001 - report exact row context.
            failures.append(f"{row.table}:{row.name}: cannot compute AR/CR: {exc}")
            continue

        if ar != row.ar or cr != row.cr:
            failures.append(
                f"{row.table}:{row.name}: AR/CR {ar}/{cr} != expected {row.ar}/{row.cr}"
            )

        if row.blank_bias is not None:
            if "blank_bias" in data:
                actual = float(data["blank_bias"])
                if actual != row.blank_bias:
                    failures.append(
                        f"{row.table}:{row.name}: blank_bias {actual} != expected {row.blank_bias}"
                    )
            else:
                warnings.append(f"{row.table}:{row.name}: JSON has no blank_bias field")

        if row.nonblank_bias is not None:
            if "nonblank_bias" in data:
                actual = float(data["nonblank_bias"])
                if actual != row.nonblank_bias:
                    failures.append(
                        f"{row.table}:{row.name}: nonblank_bias {actual} != expected {row.nonblank_bias}"
                    )
            else:
                warnings.append(f"{row.table}:{row.name}: JSON has no nonblank_bias field")

    print(f"checked_rows={checked}")
    print(f"warnings={len(warnings)}")
    for warning in warnings:
        print(f"WARNING {warning}")
    print(f"failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
