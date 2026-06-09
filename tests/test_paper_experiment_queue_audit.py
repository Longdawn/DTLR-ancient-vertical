import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_audit_tool():
    path = ROOT / "tools" / "audit_paper_experiment_queue.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


class PaperExperimentQueueAuditTest(unittest.TestCase):
    def setUp(self):
        self.tool = load_audit_tool()

    def make_item(self, root, name="mthv2_ctc_count003"):
        run_dir = Path("logs") / name
        item = self.tool.QueueItem(
            name=name,
            purpose="unit-test item",
            run_dir=run_dir,
            train_script=run_dir / "train.sh",
            post_script=run_dir / "post.sh",
        )
        abs_run_dir = root / run_dir
        abs_run_dir.mkdir(parents=True)
        (root / item.train_script).write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        (root / item.post_script).write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        return item, abs_run_dir

    def test_ready_to_run_when_scripts_exist_but_no_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, _ = self.make_item(root)

            row = self.tool.audit_item(root, item)

        self.assertEqual(row["status"], "READY_TO_RUN")
        self.assertEqual(row["decision"], "RUN_NEXT")
        self.assertEqual(row["gate"], "NOT_EVALUABLE_YET")
        self.assertIn("checkpoint", row["missing"])

    def test_checkpoint_without_json_needs_postprocess(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, run_dir = self.make_item(root)
            (run_dir / "checkpoint_best_regular.pth").write_bytes(b"fake checkpoint")

            row = self.tool.audit_item(root, item)

        self.assertEqual(row["status"], "NEEDS_POSTPROCESS")
        self.assertEqual(row["decision"], "RUN_POSTPROCESS")
        self.assertEqual(row["gate"], "NOT_EVALUABLE_YET")

    def test_complete_mthv2_count003_can_compete_with_count001(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, run_dir = self.make_item(root)
            (run_dir / "checkpoint_best_regular.pth").write_bytes(b"fake checkpoint")
            write_json(run_dir / "micro_valid_clean_0608.json", {"micro_cer": 0.04})
            write_json(run_dir / "micro_test_clean_0608.json", {"micro_cer": 0.035})
            write_json(
                run_dir / "decode_bias_sweep_valid_0608.json",
                [{"micro_cer": 0.032, "blank_bias": -2.0, "nonblank_bias": 0.8}],
            )
            write_json(run_dir / "micro_test_bias_0608.json", {"micro_cer": 0.0325})

            row = self.tool.audit_item(root, item)

        self.assertEqual(row["status"], "PAPER_READY_ARTIFACTS")
        self.assertEqual(row["decision"], "COMPARE_TO_MTHV2_COUNT001")
        self.assertEqual(row["gate"], "CAN_COMPETE_WITH_COUNT001")

    def test_hdrc_no_structure_complete_is_lower_bound_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, run_dir = self.make_item(root, name="hdrc_no_structure")
            (run_dir / "checkpoint_best_regular.pth").write_bytes(b"fake checkpoint")
            write_json(run_dir / "micro_valid_clean_0608.json", {"micro_cer": 0.99})
            write_json(run_dir / "micro_test_clean_0608.json", {"micro_cer": 0.99})
            write_json(
                run_dir / "decode_bias_sweep_valid_0608.json",
                [{"micro_cer": 0.98, "blank_bias": -2.0, "nonblank_bias": 0.4}],
            )
            write_json(run_dir / "micro_test_bias_0608.json", {"micro_cer": 0.98})

            row = self.tool.audit_item(root, item)

        self.assertEqual(row["status"], "PAPER_READY_ARTIFACTS")
        self.assertEqual(row["decision"], "USE_ONLY_AS_LOWER_BOUND_CONTROL")
        self.assertEqual(row["gate"], "LOWER_BOUND_CONTROL_ONLY")

    def test_complete_length_balance_reports_length_buckets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, run_dir = self.make_item(root, name="mthv2_length_balance")
            (run_dir / "checkpoint_best_regular.pth").write_bytes(b"fake checkpoint")
            bucket_metrics = {
                "by_gt_len_bin": {
                    "1": {"micro_cer": 0.20},
                    "2": {"micro_cer": 0.15},
                    "3-5": {"micro_cer": 0.10},
                    "6-10": {"micro_cer": 0.08},
                    "11+": {"micro_cer": 0.02},
                }
            }
            write_json(run_dir / "micro_valid_clean_0608.json", {"micro_cer": 0.11, **bucket_metrics})
            write_json(run_dir / "micro_test_clean_0608.json", {"micro_cer": 0.10, **bucket_metrics})
            write_json(
                run_dir / "decode_bias_sweep_valid_0608.json",
                [{"micro_cer": 0.09, "blank_bias": -2.0, "nonblank_bias": 0.8}],
            )
            write_json(run_dir / "micro_test_bias_0608.json", {"micro_cer": 0.09})

            row = self.tool.audit_item(root, item)

        self.assertEqual(row["status"], "PAPER_READY_ARTIFACTS")
        self.assertIn("1=20.00", row["valid_buckets"])
        self.assertIn("11+=2.00", row["valid_buckets"])
        self.assertIn("2=15.00", row["test_buckets"])

    def test_audit_uses_latest_metric_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, run_dir = self.make_item(root)
            (run_dir / "checkpoint_best_regular.pth").write_bytes(b"fake checkpoint")
            write_json(run_dir / "micro_valid_clean_0607.json", {"micro_cer": 0.50})
            write_json(run_dir / "micro_valid_clean_0608.json", {"micro_cer": 0.04})
            write_json(run_dir / "micro_test_clean_0608.json", {"micro_cer": 0.035})
            write_json(
                run_dir / "decode_bias_sweep_valid_0607.json",
                [{"micro_cer": 0.50, "blank_bias": 0.0, "nonblank_bias": 0.0}],
            )
            write_json(
                run_dir / "decode_bias_sweep_valid_0608.json",
                [{"micro_cer": 0.032, "blank_bias": -2.0, "nonblank_bias": 0.8}],
            )
            write_json(run_dir / "micro_test_bias_0607.json", {"micro_cer": 0.50})
            write_json(run_dir / "micro_test_bias_0608.json", {"micro_cer": 0.0325})

            row = self.tool.audit_item(root, item)

        self.assertIn("CER=4.00", row["valid_clean"])
        self.assertIn("CER=3.20", row["valid_sweep"])
        self.assertIn("CER=3.25", row["test_bias"])
        self.assertEqual(row["gate"], "CAN_COMPETE_WITH_COUNT001")

    def test_audit_queue_accepts_custom_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item, _ = self.make_item(root)

            rows = self.tool.audit_queue(root, [item])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "mthv2_ctc_count003")
        self.assertEqual(rows[0]["status"], "READY_TO_RUN")

    def test_rows_to_json_is_machine_readable(self):
        rows = [
            {
                "name": "mthv2_ctc_count003",
                "status": "PAPER_READY_ARTIFACTS",
                "decision": "COMPARE_TO_MTHV2_COUNT001",
                "gate": "CAN_COMPETE_WITH_COUNT001",
            }
        ]

        text = self.tool.rows_to_json(Path("/repo"), rows)
        payload = json.loads(text)

        self.assertEqual(payload["root"], "/repo")
        self.assertEqual(payload["rows"][0]["gate"], "CAN_COMPETE_WITH_COUNT001")


if __name__ == "__main__":
    unittest.main()
