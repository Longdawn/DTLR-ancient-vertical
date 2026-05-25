import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PaperWorkflowToolsTest(unittest.TestCase):
    def test_pick_best_epoch_and_build_report(self):
        tool = load_module(ROOT / "tools" / "report_mth1000_paper_metrics.py")
        rows = [
            {"epoch": 0, "test_cer_oracle_direction": 0.20, "test_wer_oracle_direction": 0.50, "test_blank_pred_ratio_unscaled": 0.99},
            {"epoch": 1, "test_cer_oracle_direction": 0.15, "test_wer_oracle_direction": 0.45, "test_blank_pred_ratio_unscaled": 0.98},
        ]
        best = tool.pick_best_epoch(rows)
        self.assertEqual(best["epoch"], 1)

        ctc_summary = {
            "cer_micro": 0.10,
            "empty_pred_rate": 0.05,
            "pred_gt_len_ratio": 0.96,
            "by_gt_len_bin": {
                "1": {"samples": 10, "cer_micro": 0.30, "empty_pred_rate": 0.20, "pred_gt_len_ratio": 0.80},
                "11+": {"samples": 50, "cer_micro": 0.05, "empty_pred_rate": 0.00, "pred_gt_len_ratio": 0.98},
            },
        }
        report = tool.build_report(best, ctc_summary, Path("/tmp/run"), Path("/tmp/summary.json"))
        self.assertAlmostEqual(report["best_test_ar_assuming_1_minus_cer"], 0.85)
        self.assertAlmostEqual(report["ctc_summary_ar_assuming_1_minus_cer"], 0.90)
        self.assertEqual(report["len_bins"]["1"]["samples"], 10)

    def test_stage1_gate_fails_blank_collapse(self):
        tool = load_module(ROOT / "tools" / "check_stage1_gate.py")
        candidate = {
            "avg_blank_ratio_full": 0.9922,
            "avg_pred_nonblank_count": 7.0,
            "avg_gt_len": 7.49,
            "real_gt_box_rate": 0.98,
        }
        baseline = {
            "avg_blank_ratio_full": 0.9547,
            "avg_pred_nonblank_count": 40.79,
            "avg_gt_len": 7.49,
            "real_gt_box_rate": 0.98,
        }
        result = tool.evaluate_gate(candidate, baseline, 0.01, 0.8, 1.5, 0.9)
        self.assertFalse(result["pass"])
        self.assertTrue(any("blank_ratio" in reason for reason in result["reasons"]))
        self.assertTrue(any("pred_nonblank_count too low" in reason for reason in result["reasons"]))

    def test_compare_paper_runs_sorts_and_formats(self):
        tool = load_module(ROOT / "tools" / "compare_paper_runs.py")
        reports = [
            {
                "run_dir": "run_b",
                "best_epoch": 2,
                "best_test_cer_oracle_direction": 0.20,
                "best_test_ar_assuming_1_minus_cer": 0.80,
                "ctc_summary_cer_micro": 0.10,
                "len_bins": {"1": {"cer_micro": 0.30}, "11+": {"cer_micro": 0.05}},
            },
            {
                "run_dir": "run_a",
                "best_epoch": 1,
                "best_test_cer_oracle_direction": 0.15,
                "best_test_ar_assuming_1_minus_cer": 0.85,
                "ctc_summary_cer_micro": 0.09,
                "len_bins": {"1": {"cer_micro": 0.28}, "11+": {"cer_micro": 0.06}},
            },
        ]
        rows = tool.sort_rows(tool.build_rows(reports))
        self.assertEqual(rows[0]["run_dir"], "run_a")
        md = tool.make_markdown(rows, "run_b")
        self.assertIn("MTH1000 Paper Run Comparison", md)
        self.assertIn("Delta Vs Baseline", md)
        self.assertIn("run_a", md)


if __name__ == "__main__":
    unittest.main()
