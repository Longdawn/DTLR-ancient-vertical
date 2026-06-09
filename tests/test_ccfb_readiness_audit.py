import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_readiness_tool():
    path = ROOT / "tools" / "audit_ccfb_readiness.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class CcfbReadinessAuditTest(unittest.TestCase):
    def setUp(self):
        self.tool = load_readiness_tool()

    def make_minimal_ready_root(self, root, include_code_refs=False):
        write_json(
            root / "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_bias_b-20_nb08_0608.json",
            {"micro_cer": 0.0325, "micro_ar": 0.9675, "micro_cr": 0.9700, "samples": 10455},
        )
        write_json(
            root / "logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json",
            {"micro_cer": 0.0656, "micro_ar": 0.9344, "micro_cr": 0.9436, "samples": 3381},
        )
        write_json(
            root / "logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_b-20_nb04_0606.json",
            {"micro_cer": 0.9989, "micro_ar": 0.0011, "micro_cr": 0.0016, "samples": 10455},
        )
        write_json(
            root / "logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_b-12_nb10_0605.json",
            {"micro_cer": 0.1728, "micro_ar": 0.8272, "micro_cr": 0.8397, "samples": 3381},
        )
        write_json(
            root / "logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_bias_b-20_nb04_0527.json",
            {"cer_micro": 0.0930, "micro_ar": 0.9070, "micro_cr": 0.9180, "samples": 3381},
        )
        write_json(
            root / "logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_bias_b-20_nb08_0603.json",
            {"micro_cer": 0.0331, "micro_ar": 0.9669, "micro_cr": 0.9690, "samples": 10455},
        )
        write_json(
            root / "logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_test_bias_b-20_nb10_0528.json",
            {"cer_micro": 0.0390, "micro_ar": 0.9610, "micro_cr": 0.9637, "samples": 10455},
        )
        write_json(
            root / "logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_bias_bm08_nb10_0607.json",
            {"micro_cer": 0.0617, "micro_ar": 0.9383, "micro_cr": 0.9503, "samples": 10455},
        )
        write_json(
            root / "logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_bias_b-20_nb04_0607.json",
            {"micro_cer": 0.1403, "micro_ar": 0.8597, "micro_cr": 0.8972, "samples": 3381},
        )

        for rel in (
            "logs/mthv2_length_balance_v2_resume_1000_0608/run_length_balance_probe_0608.sh",
            "logs/mthv2_length_balance_v2_resume_1000_0608/run_postprocess_after_finish_0608.sh",
            "logs/hdrc_no_structure_ctc_full_0608/run_hdrc_no_structure_0608.sh",
            "logs/hdrc_no_structure_ctc_full_0608/run_postprocess_after_finish_0608.sh",
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count003_0608/run_full_ctc_count003_0608.sh",
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count003_0608/run_postprocess_after_finish_0608.sh",
            "logs/hdrc_qbudget_full_ctc_count003_0608/run_full_ctc_count003_0608.sh",
            "logs/hdrc_qbudget_full_ctc_count003_0608/run_postprocess_after_finish_0608.sh",
        ):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("#!/usr/bin/env bash\n", encoding="utf-8")

        if include_code_refs:
            for evidence in self.tool.MODULE_EVIDENCE.values():
                for rel in evidence["code_refs"]:
                    path = root / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("# unit-test placeholder\n", encoding="utf-8")

    def test_ready_artifacts_yield_candidate_with_open_queue_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_minimal_ready_root(root, include_code_refs=True)

            report = self.tool.audit_readiness(root)

        self.assertEqual(report["verdict"], "CCF-B_CANDIDATE_WITH_OPEN_EXPERIMENT_DEBT")
        self.assertEqual(report["paper_claims"]["mthv2_main"]["status"], "PASS")
        self.assertEqual(
            report["paper_claims"]["mthv2_main"]["evidence_type"],
            "preexisting_artifact",
        )
        self.assertEqual(report["paper_claims"]["hdrc_main"]["status"], "PASS")
        self.assertEqual(report["paper_claims"]["mthv2_no_localization_lower_bound"]["status"], "PASS")
        self.assertEqual(report["paper_claims"]["hdrc_charset_adaptation"]["status"], "PASS")
        self.assertGreaterEqual(len(report["open_experiment_debts"]), 1)
        self.assertIn("SQR / sorted CTC refiner", report["stopped_modules"])
        stopped = report["stopped_module_evidence"]
        self.assertEqual(
            stopped["SQR / sorted CTC refiner"]["decision"],
            "stop",
        )
        self.assertIn("0.146524", stopped["SQR / sorted CTC refiner"]["negative_signal"])
        self.assertIn(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_sqr_probe_0608",
            stopped["SQR / sorted CTC refiner"]["artifact_refs"],
        )
        self.assertEqual(stopped["Generic backbone replacement for this paper"]["decision"], "avoid")
        self.assertIn("structure-aware query localization", report["paper_facing_modules"])
        module_evidence = report["module_evidence"]
        self.assertEqual(
            module_evidence["structure-aware query localization"]["paper_handling"],
            "core",
        )
        self.assertIn(
            "models/dino/dino.py",
            module_evidence["structure-aware query localization"]["code_refs"],
        )
        self.assertIn(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608",
            module_evidence["MTHv2-scoped expected-count auxiliary regularization"][
                "artifact_refs"
            ],
        )
        self.assertEqual(
            module_evidence["MTHv2-scoped expected-count auxiliary regularization"][
                "paper_handling"
            ],
            "optional_mthv2_ablation",
        )
        self.assertEqual(
            report["recommended_next_experiments"][0]["name"],
            "mthv2_length_balance",
        )
        self.assertEqual(report["recommended_next_experiments"][0]["priority"], 1)
        integrity = report["reference_integrity"]
        self.assertEqual(integrity["missing_code_refs"], [])
        self.assertIn(
            "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608",
            integrity["existing_artifact_refs"],
        )
        risk_names = {risk["name"] for risk in report["protocol_risks"]}
        self.assertIn("validation_selected_decode_calibration", risk_names)
        self.assertIn("single_run_no_variance", risk_names)
        self.assertIn("open_experiment_debt", risk_names)
        comparisons = report["baseline_comparisons"]
        self.assertIn("mthv2_vs_mmocr_svtr_tiny", comparisons)
        self.assertEqual(comparisons["mthv2_vs_mmocr_svtr_tiny"]["status"], "PASS")
        self.assertGreater(comparisons["mthv2_vs_mmocr_svtr_tiny"]["delta_ar"], 0.0)
        self.assertIn("hdrc_vs_mmocr_crnn", comparisons)
        self.assertEqual(comparisons["hdrc_vs_mmocr_crnn"]["status"], "PASS")
        module_comparisons = report["module_comparisons"]
        self.assertEqual(module_comparisons["mthv2_expected_count"]["status"], "PASS")
        self.assertGreater(module_comparisons["mthv2_expected_count"]["delta_ar"], 0.0)
        self.assertEqual(module_comparisons["mthv2_head_to_full"]["status"], "PASS")
        self.assertEqual(module_comparisons["hdrc_charset_aware"]["status"], "PASS")

    def test_reference_integrity_reports_missing_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_minimal_ready_root(root)

            report = self.tool.audit_readiness(root)

        self.assertIn("models/dino/dino.py", report["reference_integrity"]["missing_code_refs"])

    def test_missing_main_artifact_blocks_candidate_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_minimal_ready_root(root)
            (
                root
                / "logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_bias_b-20_nb08_0608.json"
            ).unlink()

            report = self.tool.audit_readiness(root)

        self.assertEqual(report["verdict"], "NOT_READY_MISSING_MAIN_EVIDENCE")
        self.assertEqual(report["paper_claims"]["mthv2_main"]["status"], "MISSING")

    def test_report_to_json_is_parseable(self):
        report = {"verdict": "CCF-B_CANDIDATE_WITH_OPEN_EXPERIMENT_DEBT"}

        text = self.tool.report_to_json(report)

        self.assertEqual(json.loads(text)["verdict"], "CCF-B_CANDIDATE_WITH_OPEN_EXPERIMENT_DEBT")

    def test_markdown_includes_baseline_comparisons(self):
        report = {
            "verdict": "CCF-B_CANDIDATE_WITH_OPEN_EXPERIMENT_DEBT",
            "root": "/repo",
            "paper_claims": {},
            "open_experiment_debts": [],
            "paper_facing_modules": [],
            "module_evidence": {},
            "recommended_next_experiments": [],
            "protocol_risks": [],
            "reference_integrity": {"missing_code_refs": [], "missing_artifact_refs": []},
            "stopped_modules": [],
            "stopped_module_evidence": {},
            "baseline_comparisons": {
                "mthv2_vs_mmocr_svtr_tiny": {
                    "dataset": "MTHv2",
                    "baseline": "MMOCR SVTR-tiny Rot90(k=3)",
                    "status": "PASS",
                    "method_ar": 0.9675,
                    "baseline_ar": 0.9556,
                    "delta_ar": 0.0119,
                    "method_cr": 0.9700,
                    "baseline_cr": 0.9568,
                    "delta_cr": 0.0132,
                }
            },
            "module_comparisons": {
                "mthv2_expected_count": {
                    "module": "expected-count",
                    "dataset": "MTHv2",
                    "status": "PASS",
                    "before_label": "qbudget",
                    "after_label": "qbudget-count001",
                    "before_ar": 0.9669,
                    "after_ar": 0.9675,
                    "delta_ar": 0.0006,
                    "before_cr": 0.9690,
                    "after_cr": 0.9700,
                    "delta_cr": 0.0010,
                }
            },
        }

        text = self.tool.report_to_markdown(report)

        self.assertIn("## Baseline Comparisons", text)
        self.assertIn("MMOCR SVTR-tiny", text)
        self.assertIn("## Module Comparisons", text)
        self.assertIn("expected-count", text)

    def test_cli_json_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_minimal_ready_root(root)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "audit_ccfb_readiness.py"),
                    "--root",
                    str(root),
                    "--format",
                    "json",
                ],
                check=True,
                text=True,
                capture_output=True,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["verdict"], "CCF-B_CANDIDATE_WITH_OPEN_EXPERIMENT_DEBT")


if __name__ == "__main__":
    unittest.main()
