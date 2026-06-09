#!/usr/bin/env python3
"""Audit current CCF-B paper readiness from experiment artifacts.

This read-only helper summarizes the current SAQT paper evidence directly from
JSON metric artifacts and the prepared experiment queue. It does not train,
evaluate checkpoints, or edit paper tables.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.audit_paper_experiment_queue import audit_queue


MAIN_CLAIMS = {
    "mthv2_main": {
        "path": Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/"
            "micro_test_bias_b-20_nb08_0608.json"
        ),
        "min_ar": 0.965,
        "min_cr": 0.970,
        "description": "MTHv2 qbudget-count001 calibrated main result.",
    },
    "hdrc_main": {
        "path": Path("logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json"),
        "min_ar": 0.930,
        "min_cr": 0.940,
        "description": "HDRC qbudget-localization-query calibrated main result.",
    },
    "mthv2_no_localization_lower_bound": {
        "path": Path(
            "logs/mthv2_no_structure_ctc_full_0605/"
            "micro_test_bias_b-20_nb04_0606.json"
        ),
        "max_ar": 0.01,
        "description": "MTHv2 no-localization lower-bound control.",
    },
}

CHARSET_RANDOM = Path(
    "logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_b-12_nb10_0605.json"
)
CHARSET_AWARE = Path(
    "logs/mth1000mth1200pre_hdrcft_full_0527-1732/"
    "ctc_error_summary_test_bias_b-20_nb04_0527.json"
)

STOPPED_MODULES = [
    "SQR / sorted CTC refiner",
    "DCTC-lite / Viterbi alignment",
    "Blank probability cap",
    "MSR-v2 resize policy",
    "First LGQ activation-gated adapter",
    "Glyph prototype auxiliary for paper body",
    "Generic backbone replacement for this paper",
]

STOPPED_MODULE_EVIDENCE = {
    "SQR / sorted CTC refiner": {
        "decision": "stop",
        "negative_signal": (
            "SQR valid CER 0.146524 and sorted CTC refiner valid CER 0.142689, "
            "both worse than matched 1000-step base 0.118792."
        ),
        "artifact_refs": [
            "logs/mthv2_qbudgetstage1pre_mthv2_full_sqr_probe_0608",
            "logs/mthv2_qbudgetstage1pre_mthv2_full_sortedctc_refiner_1000_0608",
            "logs/mthv2_base_resume_1000_0607",
        ],
    },
    "DCTC-lite / Viterbi alignment": {
        "decision": "stop",
        "negative_signal": (
            "Best screened valid CER 0.120219, worse than matched base 0.118792, "
            "with extra alignment complexity."
        ),
        "artifact_refs": [
            "logs/mthv2_dctc_lite_short2_resume_1000_0608",
            "logs/mthv2_base_resume_1000_0607",
        ],
    },
    "Blank probability cap": {
        "decision": "stop",
        "negative_signal": "Valid CER 0.122598, worse than matched base 0.118792.",
        "artifact_refs": [
            "logs/mthv2_blankcap_resume_1000_0608",
            "logs/mthv2_base_resume_1000_0607",
        ],
    },
    "MSR-v2 resize policy": {
        "decision": "stop",
        "negative_signal": "Valid CER 0.130381, worse than matched base 0.118792.",
        "artifact_refs": [
            "logs/mthv2_msr_v2_resume_1000_0608",
            "logs/mthv2_base_resume_1000_0607",
        ],
    },
    "First LGQ activation-gated adapter": {
        "decision": "stop_current_setting",
        "negative_signal": (
            "Smoke valid CER 0.148588, worse than the MTHv2 qbudget head-only "
            "starting point."
        ),
        "artifact_refs": [
            "logs/mthv2_lgq_adapter_smoke_0607",
            "logs/mthv2_qbudgetstage1pre_mthv2_head_0603",
        ],
    },
    "Glyph prototype auxiliary for paper body": {
        "decision": "keep_internal",
        "negative_signal": (
            "1000-step positive signal 0.112549 was unstable at 2000 steps "
            "0.116865, and count+prototype was negative at 0.121235."
        ),
        "artifact_refs": [
            "logs/mthv2_proto_aux_resume_1000_0608",
            "logs/mthv2_proto_aux_resume_2000_0608",
            "logs/mthv2_count_proto_aux_resume_1000_0608",
        ],
    },
    "Generic backbone replacement for this paper": {
        "decision": "avoid",
        "negative_signal": (
            "No direct positive evidence in the current DTLR experiment chain; "
            "high cost and weak link to SAQT's query-to-CTC contribution."
        ),
        "artifact_refs": [
            "logs/paper_results_summary.md",
            "docs/paper-drafts/107_experiment_decision_after_code_audit.md",
        ],
    },
}

PAPER_FACING_MODULES = [
    "structure-aware query localization",
    "vertical query sorting and query-to-CTC conversion",
    "charset-aware classifier adaptation",
    "classifier-head reconstruction before full recognition finetuning",
    "full-model recognition finetuning",
    "MTHv2-scoped expected-count auxiliary regularization",
]

MODULE_EVIDENCE = {
    "structure-aware query localization": {
        "paper_handling": "core",
        "code_refs": [
            "models/dino/dino.py",
            "config/MTHV2_stage1_query_budget.py",
            "config/MTHV2_dtlr.py",
        ],
        "artifact_refs": [
            "logs/mthv2_qbudgetstage1pre_mthv2_full_0603",
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608",
            "logs/hdrc_qbudget_full_0607",
        ],
        "evidence_summary": (
            "MTHv2 qbudget improves calibrated AR/CR over the matched MTHv2 "
            "baseline; HDRC qbudget-localization-query is the current HDRC main result."
        ),
    },
    "vertical query sorting and query-to-CTC conversion": {
        "paper_handling": "core",
        "code_refs": [
            "models/dino/dino.py",
            "finetuning.py",
            "util/ctc_decoding.py",
        ],
        "artifact_refs": [
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608",
            "logs/hdrc_qbudget_full_0607",
        ],
        "evidence_summary": (
            "The paper-facing checkpoints are evaluated through sorted query logits "
            "and CTC decoding on single-column line images."
        ),
    },
    "charset-aware classifier adaptation": {
        "paper_handling": "core",
        "code_refs": [
            "finetuning.py",
            "models/dino/dino.py",
        ],
        "artifact_refs": [
            "logs/hdrc_charset_random_full_visible1_0605",
            "logs/mth1000mth1200pre_hdrcft_full_0527-1732",
        ],
        "evidence_summary": (
            "HDRC random-head calibrated AR/CR 82.72/83.97 is clearly below "
            "charset-aware 90.70/91.80."
        ),
    },
    "classifier-head reconstruction before full recognition finetuning": {
        "paper_handling": "pipeline",
        "code_refs": [
            "finetuning.py",
            "models/dino/dino.py",
        ],
        "artifact_refs": [
            "logs/mthv2_qbudgetstage1pre_mthv2_head_0603",
            "logs/mthv2_qbudgetstage1pre_mthv2_full_0603",
            "logs/mth1000mth1200pre_hdrcft_head_0527-1530",
            "logs/mth1000mth1200pre_hdrcft_full_0527-1732",
        ],
        "evidence_summary": (
            "Head-only is weaker than full recognition finetuning on both MTHv2 and HDRC."
        ),
    },
    "full-model recognition finetuning": {
        "paper_handling": "pipeline",
        "code_refs": [
            "finetuning.py",
            "engine.py",
        ],
        "artifact_refs": [
            "logs/mthv2_qbudgetstage1pre_mthv2_full_0603",
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608",
            "logs/hdrc_qbudget_full_0607",
        ],
        "evidence_summary": (
            "Full-model recognition finetuning supplies the paper-facing MTHv2 and HDRC checkpoints."
        ),
    },
    "MTHv2-scoped expected-count auxiliary regularization": {
        "paper_handling": "optional_mthv2_ablation",
        "code_refs": [
            "models/dino/dino.py",
            "config/MTHV2_dtlr_ctc_count001.py",
        ],
        "artifact_refs": [
            "logs/mthv2_qbudgetstage1pre_mthv2_full_0603",
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608",
            "logs/hdrc_qbudget_full_ctc_count001_0608",
        ],
        "evidence_summary": (
            "MTHv2 improves modestly, while HDRC count001 regresses; keep this "
            "as optional MTHv2 evidence only."
        ),
    },
}

NEXT_EXPERIMENT_PLAN = {
    "mthv2_length_balance": {
        "priority": 1,
        "purpose": "Test remaining MTHv2 short-column weakness without changing architecture.",
        "keep_criterion": "valid CER below 0.118792 and no clear long-column regression",
    },
    "hdrc_no_structure": {
        "priority": 2,
        "purpose": "Extend no-localization lower-bound evidence beyond MTHv2.",
        "keep_criterion": "use as lower-bound control; not expected to be competitive",
    },
    "mthv2_ctc_count003": {
        "priority": 3,
        "purpose": "Check whether weaker expected-count preserves the MTHv2 gain.",
        "keep_criterion": "test-bias CER at or below 0.0325",
    },
    "hdrc_ctc_count003": {
        "priority": 4,
        "purpose": "Check whether weaker expected-count avoids HDRC count001 regression.",
        "keep_criterion": "test-bias CER at or below 0.0656; otherwise internal only",
    },
}

BASELINE_COMPARISON_SPECS = {
    "mthv2_vs_mmocr_crnn": {
        "claim": "mthv2_main",
        "dataset": "MTHv2",
        "baseline": "MMOCR CRNN Rot90(k=3)",
        "baseline_cer": 0.0449,
        "baseline_ar": 0.9551,
        "baseline_cr": 0.9563,
        "source": "logs/paper_results_summary.md",
    },
    "mthv2_vs_mmocr_svtr_tiny": {
        "claim": "mthv2_main",
        "dataset": "MTHv2",
        "baseline": "MMOCR SVTR-tiny Rot90(k=3)",
        "baseline_cer": 0.0444,
        "baseline_ar": 0.9556,
        "baseline_cr": 0.9568,
        "source": "logs/paper_results_summary.md",
    },
    "mthv2_vs_paddle_svtrv2": {
        "claim": "mthv2_main",
        "dataset": "MTHv2",
        "baseline": "PaddleOCR SVTRv2 Rot90(k=3), 48x1024",
        "baseline_cer": 0.0558,
        "baseline_ar": 0.9442,
        "baseline_cr": 0.9530,
        "source": "logs/paper_results_summary.md",
    },
    "hdrc_vs_mmocr_crnn": {
        "claim": "hdrc_main",
        "dataset": "HDRC",
        "baseline": "MMOCR CRNN Rot90(k=3)",
        "baseline_cer": 0.1509,
        "baseline_ar": 0.8491,
        "baseline_cr": 0.8521,
        "source": "logs/paper_results_summary.md",
    },
    "hdrc_vs_mmocr_svtr_tiny": {
        "claim": "hdrc_main",
        "dataset": "HDRC",
        "baseline": "MMOCR SVTR-tiny Rot90(k=3)",
        "baseline_cer": 0.1629,
        "baseline_ar": 0.8371,
        "baseline_cr": 0.8389,
        "source": "logs/paper_results_summary.md",
    },
    "hdrc_vs_paddle_svtrv2": {
        "claim": "hdrc_main",
        "dataset": "HDRC",
        "baseline": "PaddleOCR SVTRv2 Rot90(k=3), 48x1024",
        "baseline_cer": 0.3510,
        "baseline_ar": 0.6490,
        "baseline_cr": 0.6618,
        "source": "logs/paper_results_summary.md",
    },
}

MODULE_COMPARISON_SPECS = {
    "mthv2_query_budget": {
        "module": "query-budget localization query",
        "dataset": "MTHv2",
        "before_label": "baseline full",
        "after_label": "qbudget full",
        "before_path": Path(
            "logs/mthv2_mth1000mth1200tkh_full_0528-0957/"
            "ctc_error_summary_test_bias_b-20_nb10_0528.json"
        ),
        "after_path": Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_0603/"
            "micro_test_bias_b-20_nb08_0603.json"
        ),
    },
    "mthv2_expected_count": {
        "module": "expected-count auxiliary",
        "dataset": "MTHv2",
        "before_label": "qbudget full",
        "after_label": "qbudget-count001",
        "before_path": Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_0603/"
            "micro_test_bias_b-20_nb08_0603.json"
        ),
        "after_path": Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/"
            "micro_test_bias_b-20_nb08_0608.json"
        ),
    },
    "mthv2_head_to_full": {
        "module": "full finetuning after head reconstruction",
        "dataset": "MTHv2",
        "before_label": "head-only",
        "after_label": "full finetuning",
        "before_path": Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_head_0603/"
            "micro_test_bias_bm08_nb10_0607.json"
        ),
        "after_path": Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_0603/"
            "micro_test_bias_b-20_nb08_0603.json"
        ),
    },
    "mthv2_localization_vs_none": {
        "module": "localization-supervised structure learning",
        "dataset": "MTHv2",
        "before_label": "no-localization",
        "after_label": "SAQT main",
        "before_path": Path(
            "logs/mthv2_no_structure_ctc_full_0605/"
            "micro_test_bias_b-20_nb04_0606.json"
        ),
        "after_path": Path(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/"
            "micro_test_bias_b-20_nb08_0608.json"
        ),
    },
    "hdrc_charset_aware": {
        "module": "charset-aware classifier adaptation",
        "dataset": "HDRC",
        "before_label": "random head",
        "after_label": "charset-aware head",
        "before_path": Path(
            "logs/hdrc_charset_random_full_visible1_0605/"
            "micro_test_bias_b-12_nb10_0605.json"
        ),
        "after_path": Path(
            "logs/mth1000mth1200pre_hdrcft_full_0527-1732/"
            "ctc_error_summary_test_bias_b-20_nb04_0527.json"
        ),
    },
    "hdrc_head_to_full": {
        "module": "full finetuning after head reconstruction",
        "dataset": "HDRC",
        "before_label": "head-only",
        "after_label": "full finetuning",
        "before_path": Path(
            "logs/mth1000mth1200pre_hdrcft_head_0527-1530/"
            "micro_test_bias_b-20_nb04_0607.json"
        ),
        "after_path": Path(
            "logs/mth1000mth1200pre_hdrcft_full_0527-1732/"
            "ctc_error_summary_test_bias_b-20_nb04_0527.json"
        ),
    },
    "hdrc_qbudget_variant": {
        "module": "qbudget-localization-query variant",
        "dataset": "HDRC",
        "before_label": "mainline full",
        "after_label": "qbudget variant",
        "before_path": Path(
            "logs/mth1000mth1200pre_hdrcft_full_0527-1732/"
            "ctc_error_summary_test_bias_b-20_nb04_0527.json"
        ),
        "after_path": Path("logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json"),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Audit CCF-B paper readiness from artifacts.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format.",
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


def metric_value(row: dict[str, Any], key: str) -> float | None:
    if key == "cer":
        return as_float(row.get("micro_cer", row.get("cer_micro")))
    return as_float(row.get(f"micro_{key}"))


def summarize_metric(root: Path, path: Path) -> dict[str, Any]:
    abs_path = root / path
    data = load_json(abs_path)
    if not isinstance(data, dict):
        return {
            "path": str(path),
            "status": "MISSING",
            "reason": "metric JSON is missing or invalid",
        }

    cer = metric_value(data, "cer")
    ar = metric_value(data, "ar")
    cr = metric_value(data, "cr")
    if ar is None and cer is not None:
        ar = 1.0 - cer
    if cr is None:
        del_rate = as_float(data.get("del_rate"))
        sub_rate = as_float(data.get("sub_rate"))
        if del_rate is not None and sub_rate is not None:
            cr = 1.0 - del_rate - sub_rate

    return {
        "path": str(path),
        "status": "FOUND",
        "evidence_type": "preexisting_artifact",
        "cer": cer,
        "ar": ar,
        "cr": cr,
        "samples": data.get("samples", data.get("evaluated_samples")),
    }


def evaluate_claim(root: Path, claim: dict[str, Any]) -> dict[str, Any]:
    row = summarize_metric(root, claim["path"])
    row["description"] = claim["description"]
    if row["status"] != "FOUND":
        return row

    failures: list[str] = []
    min_ar = claim.get("min_ar")
    min_cr = claim.get("min_cr")
    max_ar = claim.get("max_ar")
    if min_ar is not None and (row.get("ar") is None or row["ar"] < min_ar):
        failures.append(f"AR below {min_ar}")
    if min_cr is not None and (row.get("cr") is None or row["cr"] < min_cr):
        failures.append(f"CR below {min_cr}")
    if max_ar is not None and (row.get("ar") is None or row["ar"] > max_ar):
        failures.append(f"AR above lower-bound ceiling {max_ar}")

    row["status"] = "FAIL" if failures else "PASS"
    if failures:
        row["reason"] = "; ".join(failures)
    return row


def evaluate_charset_adaptation(root: Path) -> dict[str, Any]:
    random_row = summarize_metric(root, CHARSET_RANDOM)
    aware_row = summarize_metric(root, CHARSET_AWARE)
    result: dict[str, Any] = {
        "description": "HDRC charset-aware classifier adaptation.",
        "evidence_type": "preexisting_artifact",
        "random_head": random_row,
        "charset_aware": aware_row,
    }
    if random_row["status"] != "FOUND" or aware_row["status"] != "FOUND":
        result["status"] = "MISSING"
        return result

    random_ar = random_row.get("ar")
    aware_ar = aware_row.get("ar")
    if random_ar is None or aware_ar is None:
        result["status"] = "FAIL"
        result["reason"] = "missing AR metric"
        return result

    delta = aware_ar - random_ar
    result["delta_ar"] = delta
    result["status"] = "PASS" if delta >= 0.05 else "FAIL"
    if result["status"] == "FAIL":
        result["reason"] = "AR gain below 0.05"
    return result


def collect_open_experiment_debts(root: Path) -> list[dict[str, str]]:
    rows = audit_queue(root)
    debts = []
    for row in rows:
        if row["status"] != "PAPER_READY_ARTIFACTS":
            debts.append(
                {
                    "name": row["name"],
                    "status": row["status"],
                    "decision": row["decision"],
                    "gate": row["gate"],
                    "missing": row["missing"],
                    "run_dir": row["run_dir"],
                }
            )
    return debts


def recommend_next_experiments(
    open_experiment_debts: list[dict[str, str]]
) -> list[dict[str, Any]]:
    recommendations = []
    for debt in open_experiment_debts:
        plan = NEXT_EXPERIMENT_PLAN.get(debt["name"])
        if plan is None:
            continue
        recommendations.append(
            {
                "name": debt["name"],
                "status": debt["status"],
                "run_dir": debt["run_dir"],
                **plan,
            }
        )
    return sorted(recommendations, key=lambda row: row["priority"])


def collect_baseline_comparisons(
    paper_claims: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    comparisons = {}
    for name, spec in BASELINE_COMPARISON_SPECS.items():
        claim = paper_claims.get(spec["claim"], {})
        method_ar = claim.get("ar")
        method_cr = claim.get("cr")
        method_cer = claim.get("cer")
        row: dict[str, Any] = {
            "dataset": spec["dataset"],
            "baseline": spec["baseline"],
            "source": spec["source"],
            "method_cer": method_cer,
            "method_ar": method_ar,
            "method_cr": method_cr,
            "baseline_cer": spec["baseline_cer"],
            "baseline_ar": spec["baseline_ar"],
            "baseline_cr": spec["baseline_cr"],
        }
        if method_ar is None or method_cr is None or method_cer is None:
            row["status"] = "MISSING_METHOD_METRIC"
        else:
            row["delta_cer"] = spec["baseline_cer"] - method_cer
            row["delta_ar"] = method_ar - spec["baseline_ar"]
            row["delta_cr"] = method_cr - spec["baseline_cr"]
            row["status"] = (
                "PASS"
                if row["delta_cer"] > 0 and row["delta_ar"] > 0 and row["delta_cr"] > 0
                else "WEAK_OR_FAIL"
            )
        comparisons[name] = row
    return comparisons


def collect_module_comparisons(root: Path) -> dict[str, dict[str, Any]]:
    comparisons = {}
    for name, spec in MODULE_COMPARISON_SPECS.items():
        before = summarize_metric(root, spec["before_path"])
        after = summarize_metric(root, spec["after_path"])
        row: dict[str, Any] = {
            "module": spec["module"],
            "dataset": spec["dataset"],
            "before_label": spec["before_label"],
            "after_label": spec["after_label"],
            "before_path": str(spec["before_path"]),
            "after_path": str(spec["after_path"]),
            "before_status": before["status"],
            "after_status": after["status"],
        }
        if before["status"] != "FOUND" or after["status"] != "FOUND":
            row["status"] = "MISSING"
        else:
            row.update(
                {
                    "before_cer": before.get("cer"),
                    "after_cer": after.get("cer"),
                    "before_ar": before.get("ar"),
                    "after_ar": after.get("ar"),
                    "before_cr": before.get("cr"),
                    "after_cr": after.get("cr"),
                    "delta_cer": before.get("cer") - after.get("cer")
                    if before.get("cer") is not None and after.get("cer") is not None
                    else None,
                    "delta_ar": after.get("ar") - before.get("ar")
                    if before.get("ar") is not None and after.get("ar") is not None
                    else None,
                    "delta_cr": after.get("cr") - before.get("cr")
                    if before.get("cr") is not None and after.get("cr") is not None
                    else None,
                }
            )
            row["status"] = (
                "PASS"
                if (
                    row.get("delta_cer") is not None
                    and row.get("delta_ar") is not None
                    and row.get("delta_cr") is not None
                    and row["delta_cer"] > 0
                    and row["delta_ar"] > 0
                    and row["delta_cr"] > 0
                )
                else "WEAK_OR_FAIL"
            )
        comparisons[name] = row
    return comparisons


def collect_reference_integrity(root: Path) -> dict[str, list[str]]:
    code_refs: set[str] = set()
    artifact_refs: set[str] = set()

    for evidence in MODULE_EVIDENCE.values():
        code_refs.update(evidence["code_refs"])
        artifact_refs.update(evidence["artifact_refs"])
    for evidence in STOPPED_MODULE_EVIDENCE.values():
        artifact_refs.update(evidence["artifact_refs"])

    existing_code_refs = sorted(ref for ref in code_refs if (root / ref).exists())
    missing_code_refs = sorted(ref for ref in code_refs if not (root / ref).exists())
    existing_artifact_refs = sorted(ref for ref in artifact_refs if (root / ref).exists())
    missing_artifact_refs = sorted(ref for ref in artifact_refs if not (root / ref).exists())

    return {
        "existing_code_refs": existing_code_refs,
        "missing_code_refs": missing_code_refs,
        "existing_artifact_refs": existing_artifact_refs,
        "missing_artifact_refs": missing_artifact_refs,
    }


def verdict_from_claims(
    paper_claims: dict[str, dict[str, Any]],
    open_experiment_debts: list[dict[str, str]],
) -> str:
    main_statuses = [paper_claims["mthv2_main"]["status"], paper_claims["hdrc_main"]["status"]]
    if any(status == "MISSING" for status in main_statuses):
        return "NOT_READY_MISSING_MAIN_EVIDENCE"
    if any(status != "PASS" for status in main_statuses):
        return "NOT_READY_MAIN_EVIDENCE_BELOW_GATE"
    if open_experiment_debts:
        return "CCF-B_CANDIDATE_WITH_OPEN_EXPERIMENT_DEBT"
    return "CCF-B_CANDIDATE_EVIDENCE_CLOSED"


def collect_protocol_risks(
    open_experiment_debts: list[dict[str, str]],
) -> list[dict[str, str]]:
    risks = [
        {
            "name": "validation_selected_decode_calibration",
            "level": "medium",
            "mitigation": (
                "Report direct and validation-protocol calibrated decoding separately; "
                "do not present blank/nonblank bias as learned model novelty."
            ),
        },
        {
            "name": "single_run_no_variance",
            "level": "medium",
            "mitigation": (
                "Avoid significance, robustness, and universal generalization claims; "
                "treat results as dataset-scoped evidence."
            ),
        },
        {
            "name": "two_main_datasets",
            "level": "medium",
            "mitigation": (
                "Use MTHv2 and HDRC as focused evidence; keep CHDAC internal until "
                "its result is competitive."
            ),
        },
        {
            "name": "baseline_domain_scope",
            "level": "medium",
            "mitigation": (
                "Describe MMOCR/PaddleOCR baselines as adapted recognition baselines "
                "under a unified single-column protocol."
            ),
        },
    ]
    if open_experiment_debts:
        risks.append(
            {
                "name": "open_experiment_debt",
                "level": "low-to-medium",
                "mitigation": (
                    "Run the prepared GPU0 queue when tmux/CUDA are available; keep "
                    "current submission claims conservative if the queue remains open."
                ),
            }
        )
    return risks


def audit_readiness(root: Path) -> dict[str, Any]:
    root = root.resolve()
    paper_claims = {
        name: evaluate_claim(root, claim) for name, claim in MAIN_CLAIMS.items()
    }
    paper_claims["hdrc_charset_adaptation"] = evaluate_charset_adaptation(root)
    open_experiment_debts = collect_open_experiment_debts(root)
    verdict = verdict_from_claims(paper_claims, open_experiment_debts)

    return {
        "root": str(root),
        "verdict": verdict,
        "paper_claims": paper_claims,
        "open_experiment_debts": open_experiment_debts,
        "paper_facing_modules": PAPER_FACING_MODULES,
        "module_evidence": MODULE_EVIDENCE,
        "baseline_comparisons": collect_baseline_comparisons(paper_claims),
        "module_comparisons": collect_module_comparisons(root),
        "reference_integrity": collect_reference_integrity(root),
        "recommended_next_experiments": recommend_next_experiments(open_experiment_debts),
        "protocol_risks": collect_protocol_risks(open_experiment_debts),
        "stopped_modules": STOPPED_MODULES,
        "stopped_module_evidence": STOPPED_MODULE_EVIDENCE,
        "claim_limits": [
            "Use dataset-scoped CCF-B candidate wording.",
            "Do not claim SOTA, broad robustness, or universal transfer.",
            "Treat validation-selected blank/nonblank bias as evaluation protocol.",
            "Keep expected-count as optional MTHv2 evidence, not the central contribution.",
        ],
    }


def report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)


def report_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# CCF-B Readiness Audit",
        "",
        f"- Verdict: `{report['verdict']}`",
        f"- Root: `{report['root']}`",
        "",
        "## Paper Claims",
        "",
        "| Claim | Status | CER | AR | CR | Path |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for name, row in report["paper_claims"].items():
        if "random_head" in row:
            cer = ar = cr = "-"
            path = "charset random vs aware"
        else:
            cer = "-" if row.get("cer") is None else f"{100.0 * row['cer']:.2f}"
            ar = "-" if row.get("ar") is None else f"{100.0 * row['ar']:.2f}"
            cr = "-" if row.get("cr") is None else f"{100.0 * row['cr']:.2f}"
            path = row.get("path", "-")
        lines.append(f"| {name} | {row['status']} | {cer} | {ar} | {cr} | `{path}` |")

    lines.extend(["", "## Open Experiment Debts", ""])
    if report["open_experiment_debts"]:
        lines.extend(
            [
                "| Name | Status | Decision | Gate |",
                "| --- | --- | --- | --- |",
            ]
        )
        for row in report["open_experiment_debts"]:
            lines.append(
                f"| {row['name']} | {row['status']} | {row['decision']} | {row['gate']} |"
            )
    else:
        lines.append("(none)")

    lines.extend(["", "## Baseline Comparisons", ""])
    if report.get("baseline_comparisons"):
        lines.extend(
            [
                "| Dataset | Baseline | Status | Method AR/CR | Baseline AR/CR | Delta AR/CR |",
                "| --- | --- | --- | ---: | ---: | ---: |",
            ]
        )
        for row in report["baseline_comparisons"].values():
            method_ar = "-" if row.get("method_ar") is None else f"{100.0 * row['method_ar']:.2f}/{100.0 * row['method_cr']:.2f}"
            baseline_ar = f"{100.0 * row['baseline_ar']:.2f}/{100.0 * row['baseline_cr']:.2f}"
            if row.get("delta_ar") is None or row.get("delta_cr") is None:
                delta = "-"
            else:
                delta = f"{100.0 * row['delta_ar']:.2f}/{100.0 * row['delta_cr']:.2f}"
            lines.append(
                f"| {row['dataset']} | {row['baseline']} | {row['status']} | "
                f"{method_ar} | {baseline_ar} | {delta} |"
            )
    else:
        lines.append("(none)")

    lines.extend(["", "## Module Comparisons", ""])
    if report.get("module_comparisons"):
        lines.extend(
            [
                "| Dataset | Module | Status | Before -> After | AR Delta | CR Delta |",
                "| --- | --- | --- | --- | ---: | ---: |",
            ]
        )
        for row in report["module_comparisons"].values():
            if row.get("delta_ar") is None or row.get("delta_cr") is None:
                delta_ar = delta_cr = "-"
            else:
                delta_ar = f"{100.0 * row['delta_ar']:.2f}"
                delta_cr = f"{100.0 * row['delta_cr']:.2f}"
            before_after = f"{row['before_label']} -> {row['after_label']}"
            lines.append(
                f"| {row['dataset']} | {row['module']} | {row['status']} | "
                f"{before_after} | {delta_ar} | {delta_cr} |"
            )
    else:
        lines.append("(none)")

    lines.extend(["", "## Paper-Facing Modules", ""])
    for module in report["paper_facing_modules"]:
        lines.append(f"- {module}")

    lines.extend(["", "## Module Evidence", ""])
    lines.extend(
        [
            "| Module | Paper Handling | Code Refs | Artifact Refs |",
            "| --- | --- | --- | --- |",
        ]
    )
    for name in report["paper_facing_modules"]:
        evidence = report["module_evidence"][name]
        code_refs = ", ".join(f"`{ref}`" for ref in evidence["code_refs"])
        artifact_refs = ", ".join(f"`{ref}`" for ref in evidence["artifact_refs"])
        lines.append(
            f"| {name} | {evidence['paper_handling']} | {code_refs} | {artifact_refs} |"
        )

    lines.extend(["", "## Recommended Next Experiments", ""])
    if report["recommended_next_experiments"]:
        lines.extend(
            [
                "| Priority | Name | Status | Keep Criterion |",
                "| ---: | --- | --- | --- |",
            ]
        )
        for row in report["recommended_next_experiments"]:
            lines.append(
                f"| {row['priority']} | {row['name']} | {row['status']} | "
                f"{row['keep_criterion']} |"
            )
    else:
        lines.append("(none)")

    lines.extend(["", "## Protocol Risks", ""])
    lines.extend(["| Risk | Level | Mitigation |", "| --- | --- | --- |"])
    for risk in report["protocol_risks"]:
        lines.append(f"| {risk['name']} | {risk['level']} | {risk['mitigation']} |")

    lines.extend(["", "## Reference Integrity", ""])
    integrity = report["reference_integrity"]
    lines.append(f"- Missing code refs: `{len(integrity['missing_code_refs'])}`")
    lines.append(f"- Missing artifact refs: `{len(integrity['missing_artifact_refs'])}`")
    if integrity["missing_code_refs"]:
        lines.append(f"- Missing code refs detail: `{', '.join(integrity['missing_code_refs'])}`")
    if integrity["missing_artifact_refs"]:
        lines.append(
            f"- Missing artifact refs detail: `{', '.join(integrity['missing_artifact_refs'])}`"
        )

    lines.extend(["", "## Stopped Module Evidence", ""])
    lines.extend(["| Module | Decision | Negative Signal |", "| --- | --- | --- |"])
    for name in report["stopped_modules"]:
        evidence = report["stopped_module_evidence"][name]
        lines.append(
            f"| {name} | {evidence['decision']} | {evidence['negative_signal']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    report = audit_readiness(Path(args.root))
    if args.format == "markdown":
        print(report_to_markdown(report), end="")
    else:
        print(report_to_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
