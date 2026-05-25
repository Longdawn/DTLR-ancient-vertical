# CTC Evaluation Modularization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract shared CTC decoding and metric utilities, then migrate the non-visual CTC analysis tools to that shared implementation without changing training behavior or trusted baseline configs.

**Architecture:** Add pure utility modules under `util/` for decode and metric logic, with no dependency on model construction, datasets, CUDA, or matplotlib. Existing CLI tools keep their arguments and output shapes, but call the shared utilities so future reranker experiments use one metric definition.

**Tech Stack:** Python 3.11, PyTorch tensors for decode inputs, `unittest` for CPU tests, existing DTLR CLI tools for GPU sanity checks.

---

## File Structure

- Create: `util/ctc_decoding.py`
  - Owns CTC collapse, greedy label decoding, target ratio extraction, and decode-time blank/nonblank calibration.
- Create: `util/ctc_metrics.py`
  - Owns length buckets, Levenshtein edit op counts, aggregate CTC totals, and bucket summary construction.
- Create: `tests/test_ctc_eval_utils.py`
  - CPU-only tests for the shared modules.
- Modify: `tools/analyze_ctc_errors.py`
  - Replace local `remove_duplicates`, `length_bin`, `levenshtein_ops`, `Totals`, and calibration logic with shared utilities.
- Modify: `tools/sweep_ctc_decode_bias.py`
  - Replace local ratio/calibration/decode/summary logic with shared utilities.
- Modify: `tools/evaluate_short_rescue.py`
  - Replace local ratio/decode/metric imports with shared utilities.
- Modify: `tools/analyze_short_blank_margin.py`
  - Replace local greedy decode and edit op imports with shared utilities.

Do not modify these files in this plan:

- `config/MTH1000_dtlr.py`
- `config/MTH1000_MTH1200_stage1.py`
- `models/dino/dino.py`
- `engine.py`

## Task 1: Add CPU Tests For Shared CTC Utilities

**Files:**
- Create: `tests/test_ctc_eval_utils.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ctc_eval_utils.py` with:

```python
import unittest

import torch

from util.ctc_decoding import (
    apply_ctc_calibration,
    collapse_ctc,
    decode_greedy,
    ratio_from_target,
)
from util.ctc_metrics import CtcTotals, length_bin, levenshtein_ops, summarize_by_length


class CtcDecodingTest(unittest.TestCase):
    def test_collapse_ctc_removes_repeats_and_blanks(self):
        self.assertEqual(collapse_ctc([0, 2, 2, 0, 3, 3, 0, 2]), [2, 3, 2])

    def test_decode_greedy_maps_tokens_to_label_ids(self):
        pred_probs = torch.tensor(
            [
                [
                    [0.90, 0.05, 0.05, 0.00],
                    [0.10, 0.80, 0.05, 0.05],
                    [0.20, 0.70, 0.05, 0.05],
                    [0.10, 0.05, 0.80, 0.05],
                    [0.80, 0.10, 0.05, 0.05],
                    [0.10, 0.05, 0.05, 0.80],
                ]
            ],
            dtype=torch.float32,
        )
        self.assertEqual(decode_greedy(pred_probs, charset_size=3), [0, 1, 2])

    def test_ratio_from_target_accepts_tensor_and_missing_orig_size(self):
        self.assertAlmostEqual(
            ratio_from_target({"orig_size": torch.tensor([120.0, 40.0])}),
            3.0,
        )
        self.assertAlmostEqual(ratio_from_target({}), 1.0)

    def test_apply_ctc_calibration_adds_ratio_bias_only_inside_range(self):
        pred_probs = torch.tensor([[[0.51, 0.49], [0.60, 0.40]]], dtype=torch.float32)
        outside = apply_ctc_calibration(
            pred_probs,
            target={"orig_size": torch.tensor([300.0, 100.0])},
            ratio_nonblank_bias=1.0,
            ratio_min=1.5,
            ratio_max=2.0,
        )
        inside = apply_ctc_calibration(
            pred_probs,
            target={"orig_size": torch.tensor([180.0, 100.0])},
            ratio_nonblank_bias=1.0,
            ratio_min=1.5,
            ratio_max=2.0,
        )
        self.assertEqual(outside.argmax(-1)[0].tolist(), [0, 0])
        self.assertEqual(inside.argmax(-1)[0].tolist(), [1, 1])


class CtcMetricsTest(unittest.TestCase):
    def test_length_bin_boundaries(self):
        self.assertEqual([length_bin(x) for x in [1, 2, 3, 5, 6, 10, 11]], ["1", "2", "3-5", "3-5", "6-10", "6-10", "11+"])

    def test_levenshtein_ops_counts_insertions_deletions_and_substitutions(self):
        self.assertEqual(levenshtein_ops([1, 2, 3], [1, 4, 3, 5]), (2, 1, 0, 1))
        self.assertEqual(levenshtein_ops([1, 2, 3], [1]), (2, 0, 2, 0))

    def test_ctc_totals_summary_matches_existing_metric_names(self):
        totals = CtcTotals()
        totals.add(gt_len=2, pred_len=1, dist=1, ins=0, dels=1, subs=0)
        totals.add(gt_len=1, pred_len=0, dist=1, ins=0, dels=1, subs=0)
        summary = totals.to_summary()
        self.assertEqual(summary["samples"], 2)
        self.assertAlmostEqual(summary["cer_micro"], 2 / 3)
        self.assertAlmostEqual(summary["empty_pred_rate"], 0.5)
        self.assertAlmostEqual(summary["pred_gt_len_ratio"], 1 / 3)

    def test_summarize_by_length_uses_paper_bucket_order(self):
        rows = [
            {"gt_len": 1, "pred_len": 0, "dist": 1, "ins": 0, "dels": 1, "subs": 0},
            {"gt_len": 2, "pred_len": 2, "dist": 0, "ins": 0, "dels": 0, "subs": 0},
            {"gt_len": 12, "pred_len": 11, "dist": 1, "ins": 0, "dels": 1, "subs": 0},
        ]
        summary = summarize_by_length(rows)
        self.assertEqual(list(summary.keys()), ["1", "2", "11+"])
        self.assertEqual(summary["1"]["samples"], 1)
        self.assertEqual(summary["2"]["samples"], 1)
        self.assertEqual(summary["11+"]["samples"], 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail before modules exist**

Run:

```bash
python -m unittest tests.test_ctc_eval_utils -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'util.ctc_decoding'`.

- [ ] **Step 3: Keep the failing tests uncommitted until implementation passes**

Run:

```bash
git status --short tests/test_ctc_eval_utils.py
```

Expected: `?? tests/test_ctc_eval_utils.py`. The next task commits the tests
with the implementation after the test suite passes.

## Task 2: Implement Shared CTC Utility Modules

**Files:**
- Create: `util/ctc_decoding.py`
- Create: `util/ctc_metrics.py`
- Test: `tests/test_ctc_eval_utils.py`

- [ ] **Step 1: Implement `util/ctc_decoding.py`**

Create `util/ctc_decoding.py` with:

```python
from __future__ import annotations

from typing import Iterable

import torch


def collapse_ctc(tokens: Iterable[int], blank: int = 0) -> list[int]:
    collapsed: list[int] = []
    prev_token = None
    for token in tokens:
        token = int(token)
        if token != prev_token and token != blank:
            collapsed.append(token)
        prev_token = token
    return collapsed


def decode_greedy(pred_probs: torch.Tensor, charset_size: int, blank: int = 0) -> list[int]:
    if pred_probs.ndim == 3:
        token_ids = pred_probs.argmax(-1)[0].tolist()
    elif pred_probs.ndim == 2:
        token_ids = pred_probs.argmax(-1).tolist()
    else:
        raise ValueError(f"expected 2D or 3D CTC tensor, got shape {tuple(pred_probs.shape)}")

    collapsed = collapse_ctc(token_ids, blank=blank)
    return [token - 1 for token in collapsed if 1 <= token <= int(charset_size)]


def ratio_from_target(target: dict, default: float = 1.0) -> float:
    orig_size = target.get("orig_size") if isinstance(target, dict) else None
    if orig_size is None:
        return float(default)
    if torch.is_tensor(orig_size):
        values = orig_size.detach().cpu().reshape(-1).tolist()
    else:
        values = list(orig_size)
    if len(values) < 2:
        return float(default)
    height, width = float(values[0]), float(values[1])
    return height / max(width, 1.0)


def apply_ctc_calibration(
    pred_probs: torch.Tensor,
    *,
    target: dict | None = None,
    blank_bias: float = 0.0,
    nonblank_bias: float = 0.0,
    ratio_nonblank_bias: float = 0.0,
    ratio_min: float = 1.5,
    ratio_max: float = 2.0,
) -> torch.Tensor:
    if blank_bias == 0.0 and nonblank_bias == 0.0 and ratio_nonblank_bias == 0.0:
        return pred_probs

    scores = torch.log(pred_probs.clamp(min=1e-12))
    scores[..., 0] += float(blank_bias)
    scores[..., 1:] += float(nonblank_bias)

    if ratio_nonblank_bias != 0.0 and target is not None:
        ratio = ratio_from_target(target)
        if float(ratio_min) < ratio <= float(ratio_max):
            scores[..., 1:] += float(ratio_nonblank_bias)

    return scores
```

- [ ] **Step 2: Implement `util/ctc_metrics.py`**

Create `util/ctc_metrics.py` with:

```python
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


LENGTH_BIN_KEYS = ["1", "2", "3-5", "6-10", "11+"]


def length_bin(gt_len: int) -> str:
    gt_len = int(gt_len)
    if gt_len == 1:
        return "1"
    if gt_len == 2:
        return "2"
    if gt_len <= 5:
        return "3-5"
    if gt_len <= 10:
        return "6-10"
    return "11+"


def levenshtein_ops(a: Iterable[int], b: Iterable[int]) -> tuple[int, int, int, int]:
    a = [int(x) for x in a]
    b = [int(x) for x in b]
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    op = [[None] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = i
        op[i][0] = "del"
    for j in range(1, m + 1):
        dp[0][j] = j
        op[0][j] = "ins"

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                op[i][j] = "eq"
            else:
                candidates = [
                    (dp[i - 1][j] + 1, "del"),
                    (dp[i][j - 1] + 1, "ins"),
                    (dp[i - 1][j - 1] + 1, "sub"),
                ]
                dp[i][j], op[i][j] = min(candidates, key=lambda item: item[0])

    i, j = n, m
    insertions = deletions = substitutions = 0
    while i > 0 or j > 0:
        step = op[i][j]
        if step == "eq":
            i -= 1
            j -= 1
        elif step == "sub":
            substitutions += 1
            i -= 1
            j -= 1
        elif step == "del":
            deletions += 1
            i -= 1
        elif step == "ins":
            insertions += 1
            j -= 1
        else:
            break

    return dp[n][m], insertions, deletions, substitutions


@dataclass
class CtcTotals:
    n: int = 0
    gt_chars: int = 0
    pred_chars: int = 0
    dist: int = 0
    ins: int = 0
    dels: int = 0
    subs: int = 0
    empty_pred: int = 0

    def add(self, gt_len: int, pred_len: int, dist: int, ins: int, dels: int, subs: int) -> None:
        self.n += 1
        self.gt_chars += int(gt_len)
        self.pred_chars += int(pred_len)
        self.dist += int(dist)
        self.ins += int(ins)
        self.dels += int(dels)
        self.subs += int(subs)
        self.empty_pred += int(int(pred_len) == 0)

    def to_summary(self) -> dict:
        return {
            "samples": self.n,
            "cer_micro": self.dist / max(self.gt_chars, 1),
            "avg_gt_len": self.gt_chars / max(self.n, 1),
            "avg_pred_len": self.pred_chars / max(self.n, 1),
            "pred_gt_len_ratio": self.pred_chars / max(self.gt_chars, 1),
            "empty_pred_rate": self.empty_pred / max(self.n, 1),
            "ins_rate": self.ins / max(self.gt_chars, 1),
            "del_rate": self.dels / max(self.gt_chars, 1),
            "sub_rate": self.subs / max(self.gt_chars, 1),
        }


def summarize_by_length(rows: Iterable[dict]) -> dict[str, dict]:
    by_bin: dict[str, CtcTotals] = defaultdict(CtcTotals)
    for row in rows:
        bucket = length_bin(int(row["gt_len"]))
        by_bin[bucket].add(
            gt_len=int(row["gt_len"]),
            pred_len=int(row["pred_len"]),
            dist=int(row["dist"]),
            ins=int(row["ins"]),
            dels=int(row["dels"]),
            subs=int(row["subs"]),
        )
    return {
        key: by_bin[key].to_summary()
        for key in LENGTH_BIN_KEYS
        if by_bin[key].n > 0
    }
```

- [ ] **Step 3: Run tests to verify modules pass**

Run:

```bash
python -m unittest tests.test_ctc_eval_utils -v
```

Expected: PASS all 8 tests.

- [ ] **Step 4: Run existing paper workflow tests**

Run:

```bash
python -m unittest tests.test_paper_workflow_tools -v
```

Expected: PASS all existing tests.

- [ ] **Step 5: Commit shared modules**

Run:

```bash
git add util/ctc_decoding.py util/ctc_metrics.py tests/test_ctc_eval_utils.py
git commit -m "feat: add shared CTC eval utilities"
```

## Task 3: Refactor `tools/analyze_ctc_errors.py`

**Files:**
- Modify: `tools/analyze_ctc_errors.py`
- Test: `tests/test_ctc_eval_utils.py`

- [ ] **Step 1: Update imports**

Replace the local dataclass/type imports at the top with this import set:

```python
import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import List
import os
import sys
```

Add shared utility imports after `import util.misc as utils`:

```python
from util.ctc_decoding import apply_ctc_calibration, decode_greedy
from util.ctc_metrics import CtcTotals as Totals
from util.ctc_metrics import LENGTH_BIN_KEYS, length_bin, levenshtein_ops
```

- [ ] **Step 2: Remove local duplicate functions and class**

Delete these local definitions from `tools/analyze_ctc_errors.py`:

```python
def remove_duplicates(sequence: List[int]) -> List[int]:
    output = []
    prev = None
    for token in sequence:
        if token != prev and token != 0:
            output.append(token)
        prev = token
    return output
```

Delete the local `levenshtein_ops`, `Totals`, `length_bin`, and `apply_decode_calibration` definitions.

- [ ] **Step 3: Keep the existing `labels_to_text` helper**

Confirm `labels_to_text` remains in `tools/analyze_ctc_errors.py`:

```python
def labels_to_text(labels: List[int], charset) -> str:
    if not labels:
        return ""
    values = [charset[x] for x in labels]
    if values and isinstance(values[0], int):
        return " ".join(str(v) for v in values)
    return "".join(str(v) for v in values)
```

- [ ] **Step 4: Replace decode logic in `main()`**

Replace:

```python
decode_scores = apply_decode_calibration(pred_probs, targets[0], cli)

pred_tokens = decode_scores.argmax(-1)[0].tolist()
pred_tokens = remove_duplicates(pred_tokens)
pred_labels = [t - 1 for t in pred_tokens if 1 <= t <= len(dataset.charset)]
```

with:

```python
decode_scores = apply_ctc_calibration(
    pred_probs,
    target=targets[0],
    blank_bias=cli.blank_bias,
    nonblank_bias=cli.nonblank_bias,
    ratio_nonblank_bias=cli.ratio_nonblank_bias,
    ratio_min=cli.ratio_min,
    ratio_max=cli.ratio_max,
)
pred_labels = decode_greedy(decode_scores, len(dataset.charset))
```

- [ ] **Step 5: Replace hard-coded length bucket order**

Replace:

```python
for key in ["1", "2", "3-5", "6-10", "11+"]
```

with:

```python
for key in LENGTH_BIN_KEYS
```

in the `by_gt_len_bin` summary construction.

- [ ] **Step 6: Run import and unit tests**

Run:

```bash
python -m unittest tests.test_ctc_eval_utils -v
python -m unittest tests.test_paper_workflow_tools -v
python -c "import tools.analyze_ctc_errors as t; print(t.length_bin(11)); print(t.levenshtein_ops([1, 2], [1]))"
```

Expected:

```text
11+
(1, 0, 1, 0)
```

- [ ] **Step 7: Commit analyze script refactor**

Run:

```bash
git add tools/analyze_ctc_errors.py
git commit -m "refactor: use shared CTC utilities in error analysis"
```

## Task 4: Refactor Decode Sweep And Short-Rescue Tools

**Files:**
- Modify: `tools/sweep_ctc_decode_bias.py`
- Modify: `tools/evaluate_short_rescue.py`

- [ ] **Step 1: Refactor `tools/sweep_ctc_decode_bias.py` imports**

Replace imports from `tools.analyze_ctc_errors`:

```python
from tools.analyze_ctc_errors import (
    _adapt_class_head,
    _load_compatible_state,
    load_cfg_to_args,
)
from util.ctc_decoding import apply_ctc_calibration, decode_greedy
from util.ctc_metrics import CtcTotals as Totals
from util.ctc_metrics import LENGTH_BIN_KEYS, length_bin, levenshtein_ops
```

- [ ] **Step 2: Remove local sweep helpers superseded by shared utilities**

Delete local `ratio_from_target` and `calibrated_argmax` from `tools/sweep_ctc_decode_bias.py`.

Keep `build_settings(cli)` because it is sweep-specific.

- [ ] **Step 3: Update `make_summary` in `tools/sweep_ctc_decode_bias.py`**

Use:

```python
def make_summary(total, by_len_bin):
    summary = total.to_summary()
    summary["by_gt_len_bin"] = {
        key: by_len_bin[key].to_summary()
        for key in LENGTH_BIN_KEYS
        if by_len_bin[key].n > 0
    }
    return summary
```

- [ ] **Step 4: Replace sweep decode loop**

Replace the inner decode block:

```python
pred_tokens = calibrated_argmax(pred_probs, targets[0], setting, cli)
pred_tokens = remove_duplicates(pred_tokens)
pred_labels = [t - 1 for t in pred_tokens if 1 <= t <= len(dataset.charset)]
```

with:

```python
decode_scores = apply_ctc_calibration(
    pred_probs,
    target=targets[0],
    blank_bias=setting["blank_bias"],
    nonblank_bias=setting["nonblank_bias"],
    ratio_nonblank_bias=setting["ratio_nonblank_bias"],
    ratio_min=cli.ratio_min,
    ratio_max=cli.ratio_max,
)
pred_labels = decode_greedy(decode_scores, len(dataset.charset))
```

- [ ] **Step 5: Refactor `tools/evaluate_short_rescue.py` imports**

Replace imports from `tools.analyze_ctc_errors`:

```python
from tools.analyze_ctc_errors import (
    _adapt_class_head,
    _load_compatible_state,
    load_cfg_to_args,
)
from util.ctc_decoding import decode_greedy, ratio_from_target
from util.ctc_metrics import CtcTotals as Totals
from util.ctc_metrics import LENGTH_BIN_KEYS, length_bin, levenshtein_ops
```

- [ ] **Step 6: Replace `decode_baseline` in `tools/evaluate_short_rescue.py`**

Use:

```python
def decode_baseline(pred_probs, charset_size):
    return decode_greedy(pred_probs, charset_size)
```

- [ ] **Step 7: Update `summarize` in `tools/evaluate_short_rescue.py`**

Use:

```python
def summarize(total, by_len_bin):
    summary = total.to_summary()
    summary["by_gt_len_bin"] = {
        key: by_len_bin[key].to_summary()
        for key in LENGTH_BIN_KEYS
        if by_len_bin[key].n > 0
    }
    return summary
```

- [ ] **Step 8: Run import and CPU tests**

Run:

```bash
python -m unittest tests.test_ctc_eval_utils -v
python -c "import tools.sweep_ctc_decode_bias as s; print(len(s.build_settings(type('C', (), {'blank_biases':[0.0], 'nonblank_biases':[0.0], 'ratio_nonblank_biases':[0.0]})())))"
python -c "import tools.evaluate_short_rescue as r; print(r.make_policies([1.5])[0]['name'])"
```

Expected:

```text
1
baseline
```

- [ ] **Step 9: Commit sweep and rescue refactor**

Run:

```bash
git add tools/sweep_ctc_decode_bias.py tools/evaluate_short_rescue.py
git commit -m "refactor: share CTC decode logic in sweep tools"
```

## Task 5: Refactor Short Blank Margin Tool

**Files:**
- Modify: `tools/analyze_short_blank_margin.py`

- [ ] **Step 1: Update imports**

Replace imports from `tools.analyze_ctc_errors`:

```python
from tools.analyze_ctc_errors import (
    _adapt_class_head,
    _load_compatible_state,
    load_cfg_to_args,
)
from util.ctc_decoding import decode_greedy
from util.ctc_metrics import levenshtein_ops
```

- [ ] **Step 2: Replace local greedy decoder**

Replace:

```python
def decode_greedy(pred_probs, charset_size):
    pred_tokens = pred_probs.argmax(-1)[0].tolist()
    pred_tokens = remove_duplicates(pred_tokens)
    return [t - 1 for t in pred_tokens if 1 <= t <= charset_size]
```

with no local function. Calls already using `decode_greedy(pred_probs, len(dataset.charset))` should resolve to `util.ctc_decoding.decode_greedy`.

- [ ] **Step 3: Run import and CPU tests**

Run:

```bash
python -m unittest tests.test_ctc_eval_utils -v
python -c "import tools.analyze_short_blank_margin as m; print(m.levenshtein_ops([1], []))"
```

Expected:

```text
(1, 0, 1, 0)
```

- [ ] **Step 4: Commit short margin refactor**

Run:

```bash
git add tools/analyze_short_blank_margin.py
git commit -m "refactor: share CTC utilities in short margin analysis"
```

## Task 6: Run Behavioral Verification Commands

**Files:**
- Read/execute only unless an output path under `logs/` is specified.

- [ ] **Step 1: Run full CPU test suite for touched pure-code tests**

Run:

```bash
python -m unittest tests.test_ctc_eval_utils tests.test_paper_workflow_tools -v
```

Expected: all tests pass.

- [ ] **Step 2: Run a small trusted-checkpoint GPU sanity check**

Run:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/analyze_ctc_errors.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 25 --new_class_embedding --output_json logs/ctc_modularization_sanity_baseline_25.json --output_cases logs/ctc_modularization_sanity_baseline_25.jsonl --options mth1000_root=tkhmth2200_mth1000_dtlr mth1000_raw_root=TKHMTH2200/MTH1000
```

Expected:

- command exits `0`
- printed summary contains `"samples": 25`
- output file `logs/ctc_modularization_sanity_baseline_25.json` exists

- [ ] **Step 3: Inspect sanity summary headline fields**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
path = Path("logs/ctc_modularization_sanity_baseline_25.json")
data = json.loads(path.read_text(encoding="utf-8"))
for key in ["samples", "cer_micro", "empty_pred_rate", "pred_gt_len_ratio", "by_gt_len_bin"]:
    print(key, data[key])
PY
```

Expected:

- `samples 25`
- `by_gt_len_bin` is present and non-empty
- numeric headline fields are finite floats

- [ ] **Step 4: Run a one-setting decode-bias smoke check**

Run:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 10 --new_class_embedding --blank_biases 0.0 --nonblank_biases 0.0 --ratio_nonblank_biases 0.0 --output_json logs/ctc_modularization_sweep_smoke_10.json --options mth1000_root=tkhmth2200_mth1000_dtlr mth1000_raw_root=TKHMTH2200/MTH1000
```

Expected:

- command exits `0`
- output JSON contains exactly one result row
- printed output begins with `Top decode-bias settings by CER:`

- [ ] **Step 5: Run a short-rescue smoke check**

Run:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/evaluate_short_rescue.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 10 --new_class_embedding --ratio_thresholds 1.5 --topk 4 --output_json logs/ctc_modularization_short_rescue_smoke_10.json --options mth1000_root=tkhmth2200_mth1000_dtlr mth1000_raw_root=TKHMTH2200/MTH1000
```

Expected:

- command exits `0`
- printed output begins with `Top rescue policies by micro CER:`
- output JSON contains a row with `"policy": "baseline"`

- [ ] **Step 6: Commit verification-related code if smoke checks reveal required fixes**

If Step 2, 4, or 5 exposes an implementation issue, fix only the touched utility or tool file, rerun the failed command, then run:

```bash
git add util/ctc_decoding.py util/ctc_metrics.py tools/analyze_ctc_errors.py tools/sweep_ctc_decode_bias.py tools/evaluate_short_rescue.py tools/analyze_short_blank_margin.py tests/test_ctc_eval_utils.py
git commit -m "fix: preserve CTC tool behavior after modularization"
```

If no fixes are needed, do not create an empty commit.

## Task 7: Final Review And Handoff

**Files:**
- Read: `git status --short`
- Read: recent commit history

- [ ] **Step 1: Confirm trusted baseline configs were not modified**

Run:

```bash
git diff --name-only HEAD~5..HEAD -- config/MTH1000_dtlr.py config/MTH1000_MTH1200_stage1.py models/dino/dino.py engine.py
```

Expected: no output.

- [ ] **Step 2: Confirm current worktree only has known unrelated changes**

Run:

```bash
git status --short
```

Expected: only pre-existing `models/dino/ops/MultiScaleDeformableAttention.egg-info/*` changes may remain, plus generated smoke output files under `logs/` if they were intentionally kept untracked.

- [ ] **Step 3: Summarize verification evidence**

Prepare a final note with:

```text
Changed:
- util/ctc_decoding.py
- util/ctc_metrics.py
- tests/test_ctc_eval_utils.py
- tools/analyze_ctc_errors.py
- tools/sweep_ctc_decode_bias.py
- tools/evaluate_short_rescue.py
- tools/analyze_short_blank_margin.py

Baselines preserved:
- config/MTH1000_dtlr.py unchanged
- config/MTH1000_MTH1200_stage1.py unchanged
- models/dino/dino.py unchanged
- engine.py unchanged

Verification:
- python -m unittest tests.test_ctc_eval_utils tests.test_paper_workflow_tools -v
- analyze_ctc_errors.py max_samples=25 trusted baseline smoke
- sweep_ctc_decode_bias.py max_samples=10 one-setting smoke
- evaluate_short_rescue.py max_samples=10 smoke
```

- [ ] **Step 4: Identify next paper-facing implementation**

End the handoff by recommending the next task:

```text
Next method step: implement adaptive CTC candidate reranking on top of util/ctc_decoding.py and util/ctc_metrics.py, with acceptance requiring short-text gains and no fixed-valid overall CER regression versus logs/mth1000mth1200pre_mth1000ft_full_0513-2257.
```
