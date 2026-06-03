# Query Activation Budget Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a config-gated stage-1 query activation budget loss that preserves all existing baselines by default.

**Architecture:** Implement a small helper in `models/dino/dino.py` that computes expected nonblank query count from class logits and penalizes only over-budget samples. Wire it into `SetCriterion.loss_labels`, add the loss coefficient to `weight_dict` only when enabled, and create an experiment-only config for MTHv2 query-budget stage-1.

**Tech Stack:** PyTorch, `unittest`, DTLR DINO/SetCriterion, experiment configs.

---

### Task 1: Add Query Budget Helper Tests

**Files:**
- Create: `tests/test_query_activation_budget.py`
- Modify: none

- [ ] **Step 1: Write failing tests for the helper**

```python
import importlib
import unittest

import torch


class QueryActivationBudgetTest(unittest.TestCase):
    def setUp(self):
        self.dino = importlib.import_module("models.dino.dino")

    def test_query_budget_loss_penalizes_over_activation(self):
        pred_logits = torch.tensor(
            [
                [
                    [0.0, 4.0],
                    [0.0, 4.0],
                    [4.0, 0.0],
                ]
            ],
            dtype=torch.float32,
        )
        targets = [{"labels": torch.tensor([1], dtype=torch.long)}]

        loss, stats = self.dino.compute_query_budget_loss(
            pred_logits,
            targets,
            budget_scale=1.0,
            budget_margin=0.0,
        )

        self.assertGreater(loss.item(), 0.0)
        self.assertGreater(stats["expected_count_mean"], 1.0)
        self.assertEqual(stats["target_count_mean"], 1.0)

    def test_query_budget_loss_zero_when_under_budget(self):
        pred_logits = torch.tensor(
            [
                [
                    [4.0, 0.0],
                    [4.0, 0.0],
                    [0.0, 4.0],
                ]
            ],
            dtype=torch.float32,
        )
        targets = [{"labels": torch.tensor([1, 1, 1], dtype=torch.long)}]

        loss, stats = self.dino.compute_query_budget_loss(
            pred_logits,
            targets,
            budget_scale=2.0,
            budget_margin=1.0,
        )

        self.assertEqual(loss.item(), 0.0)
        self.assertLess(stats["expected_count_mean"], stats["target_count_mean"])

    def test_query_budget_loss_handles_empty_target(self):
        pred_logits = torch.tensor(
            [[[0.0, 4.0], [0.0, 4.0]]],
            dtype=torch.float32,
        )
        targets = [{"labels": torch.empty(0, dtype=torch.long)}]

        loss, stats = self.dino.compute_query_budget_loss(
            pred_logits,
            targets,
            budget_scale=2.0,
            budget_margin=1.0,
        )

        self.assertTrue(torch.isfinite(loss))
        self.assertGreaterEqual(loss.item(), 0.0)
        self.assertEqual(stats["target_count_mean"], 1.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_budget.py`

Expected: FAIL with `AttributeError` because `compute_query_budget_loss` does not exist.

### Task 2: Implement Helper

**Files:**
- Modify: `models/dino/dino.py`
- Test: `tests/test_query_activation_budget.py`

- [ ] **Step 1: Add helper implementation**

Add near existing query helper functions:

```python
def compute_query_budget_loss(
    pred_logits,
    targets,
    budget_scale=2.0,
    budget_margin=8.0,
):
    probs = pred_logits.softmax(dim=-1)
    nonblank_probs = 1.0 - probs[..., 0]
    expected_count = nonblank_probs.sum(dim=-1)
    target_lengths = torch.tensor(
        [float(target["labels"].numel()) for target in targets],
        dtype=pred_logits.dtype,
        device=pred_logits.device,
    )
    target_count = float(budget_scale) * target_lengths + float(budget_margin)
    normalizer = target_lengths.clamp(min=1.0)
    over_budget = (expected_count - target_count).clamp(min=0.0)
    loss = ((over_budget ** 2) / normalizer).mean()
    return loss, {
        "expected_count_mean": float(expected_count.detach().mean().item()),
        "target_count_mean": float(target_count.detach().mean().item()),
    }
```

- [ ] **Step 2: Run helper tests**

Run: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_budget.py`

Expected: PASS.

### Task 3: Wire Into SetCriterion

**Files:**
- Modify: `models/dino/dino.py`
- Test: `tests/test_query_activation_budget.py`

- [ ] **Step 1: Add criterion tests**

Extend `tests/test_query_activation_budget.py` with a minimal `SetCriterion` test that constructs a criterion with `loss_query_budget` in `weight_dict`, calls `loss_labels`, and asserts `loss_query_budget` and diagnostic tensors exist. Also test that omitting the weight leaves labels loss output unchanged.

- [ ] **Step 2: Verify criterion tests fail**

Run: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_budget.py`

Expected: FAIL because `SetCriterion` does not yet accept or emit query budget loss.

- [ ] **Step 3: Add criterion wiring**

In `SetCriterion.__init__`, add config values:

```python
self.query_budget_loss_enabled = "loss_query_budget" in self.weight_dict
self.query_budget_scale = float(query_budget_scale)
self.query_budget_margin = float(query_budget_margin)
```

In `loss_labels`, after base `loss_ce`, add:

```python
if self.query_budget_loss_enabled:
    loss_query_budget, query_budget_stats = compute_query_budget_loss(
        outputs["pred_logits"],
        targets,
        budget_scale=self.query_budget_scale,
        budget_margin=self.query_budget_margin,
    )
    losses["loss_query_budget"] = loss_query_budget
    losses["query_budget_expected_count"] = torch.tensor(
        query_budget_stats["expected_count_mean"], device=outputs["pred_logits"].device
    )
    losses["query_budget_target_count"] = torch.tensor(
        query_budget_stats["target_count_mean"], device=outputs["pred_logits"].device
    )
```

- [ ] **Step 4: Run criterion tests**

Run: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_budget.py`

Expected: PASS.

### Task 4: Add Build Args And Experiment Config

**Files:**
- Modify: `models/dino/dino.py`
- Create: `config/MTHV2_stage1_query_budget.py`
- Test: `tests/test_query_activation_budget.py`

- [ ] **Step 1: Write config test**

Add a test that loads `config/MTHV2_stage1_query_budget.py` and checks:

- It uses MTH1000, MTH1200, TKH roots.
- `mode_chr=False`.
- `use_query_budget_loss=True`.
- `query_budget_loss_coef=0.01`.
- `query_budget_scale=2.0`.
- `query_budget_margin=8.0`.

- [ ] **Step 2: Verify config test fails**

Run: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_budget.py`

Expected: FAIL because config file does not exist.

- [ ] **Step 3: Add build wiring**

In `build_dino`, add to `weight_dict`:

```python
query_budget_loss_coef = getattr(args, "query_budget_loss_coef", 0.0)
if getattr(args, "use_query_budget_loss", False) and query_budget_loss_coef > 0:
    weight_dict["loss_query_budget"] = query_budget_loss_coef
```

Pass `query_budget_scale` and `query_budget_margin` into `SetCriterion`.

- [ ] **Step 4: Add experiment config**

Create `config/MTHV2_stage1_query_budget.py` by importing all settings from `config.MTHV2_stage1` and overriding only query-budget flags:

```python
from config.MTHV2_stage1 import *  # noqa: F401,F403

use_query_budget_loss = True
query_budget_loss_coef = 0.01
query_budget_scale = 2.0
query_budget_margin = 8.0
```

- [ ] **Step 5: Run tests**

Run: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_budget.py`

Expected: PASS.

### Task 5: Verification

**Files:**
- Test: `tests/test_query_activation_budget.py`, `tests/test_sgq_short_query_loss.py`, `tests/test_glyph_prototype_branch.py`

- [ ] **Step 1: Run focused tests**

Run: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_budget.py tests/test_sgq_short_query_loss.py tests/test_glyph_prototype_branch.py`

Expected: PASS.

- [ ] **Step 2: Report next smoke command without launching long training**

Provide this smoke command for later execution:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --output_dir logs/mthv2_stage1_query_budget_smoke_0602 -c config/MTHV2_stage1_query_budget.py --debug --save_log --options epochs=1 save_checkpoint_interval=999
```
