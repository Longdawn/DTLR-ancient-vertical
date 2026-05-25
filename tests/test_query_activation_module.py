import importlib
import importlib.util
import unittest
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QueryActivationModuleTest(unittest.TestCase):
    def setUp(self):
        self.dino_tool = importlib.import_module("models.dino.dino")

    def test_apply_activation_gating_is_identity_when_disabled(self):
        logits = torch.tensor([[[0.2, 0.3, 0.5]]], dtype=torch.float32)
        activation_logits = torch.tensor([[[0.7]]], dtype=torch.float32)
        gated = self.dino_tool.apply_activation_gating(
            logits,
            activation_logits,
            use_activation_gating=False,
            activation_gate_blank_coef=0.3,
            activation_gate_nonblank_coef=0.4,
        )
        self.assertTrue(torch.equal(gated, logits))

    def test_apply_activation_gating_boosts_nonblank_and_suppresses_blank(self):
        logits = torch.tensor([[[0.0, 0.0, 0.0]]], dtype=torch.float32)
        activation_logits = torch.tensor([[[2.0]]], dtype=torch.float32)
        gated = self.dino_tool.apply_activation_gating(
            logits,
            activation_logits,
            use_activation_gating=True,
            activation_gate_blank_coef=0.5,
            activation_gate_nonblank_coef=0.25,
        )
        activation = torch.sigmoid(torch.tensor(2.0))
        self.assertAlmostEqual(gated[0, 0, 0].item(), float((1.0 - activation) * 0.5), places=6)
        self.assertAlmostEqual(gated[0, 0, 1].item(), float(activation * 0.25), places=6)
        self.assertAlmostEqual(gated[0, 0, 2].item(), float(activation * 0.25), places=6)

    def test_query_count_loss_matches_transcript_length(self):
        activation_logits = torch.tensor([[0.0, 0.0]], dtype=torch.float32)
        target_lengths = torch.tensor([1.0], dtype=torch.float32)
        loss, expected = self.dino_tool.compute_query_count_loss(
            activation_logits,
            target_lengths,
            short_weight=1.0,
        )
        self.assertAlmostEqual(expected.item(), 1.0, places=6)
        self.assertAlmostEqual(loss.item(), 0.0, places=6)

    def test_query_count_loss_applies_short_weight(self):
        activation_logits = torch.tensor([[-2.0, -2.0], [0.0, 0.0]], dtype=torch.float32)
        target_lengths = torch.tensor([1.0, 4.0], dtype=torch.float32)
        loss_unweighted, _ = self.dino_tool.compute_query_count_loss(
            activation_logits,
            target_lengths,
            short_weight=1.0,
        )
        loss_weighted, _ = self.dino_tool.compute_query_count_loss(
            activation_logits,
            target_lengths,
            short_weight=2.0,
        )
        self.assertGreater(loss_weighted.item(), loss_unweighted.item())


class QueryActivationConfigSmokeTest(unittest.TestCase):
    def test_new_configs_define_expected_query_activation_flags(self):
        count_only = load_module(ROOT / "config" / "MTH1000_dtlr_csaq_count_only.py")
        gating_only = load_module(ROOT / "config" / "MTH1000_dtlr_csaq_gating_only.py")
        count_gating = load_module(ROOT / "config" / "MTH1000_dtlr_csaq_count_gating.py")

        self.assertTrue(count_only.use_query_activation_head)
        self.assertTrue(count_only.use_query_count_loss)
        self.assertFalse(count_only.use_activation_gating)

        self.assertTrue(gating_only.use_query_activation_head)
        self.assertFalse(gating_only.use_query_count_loss)
        self.assertTrue(gating_only.use_activation_gating)

        self.assertTrue(count_gating.use_query_activation_head)
        self.assertTrue(count_gating.use_query_count_loss)
        self.assertTrue(count_gating.use_activation_gating)


if __name__ == "__main__":
    unittest.main()
