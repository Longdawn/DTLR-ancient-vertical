# CTC Evaluation Modularization Handoff

Date: 2026-05-25

## Scope

This handoff freezes the final state of the CTC evaluation modularization work from `docs/superpowers/plans/2026-05-25-ctc-eval-modularization.md`.

The work covered shared CTC decode/metric utilities plus migration of the non-visual CTC analysis tools. It did not change trusted baseline configs, model training code, datasets, logs, or checkpoints.

## Task Status

- Task 1: completed
- Task 2: completed
- Task 3: completed
- Task 4: completed
- Task 5: completed
- Task 6: completed
- Task 7: completed by this handoff

## Commit Map

- `7da2198` `Add CTC evaluation modularization design`
- `52f5722` `Add CTC evaluation modularization plan`
- `b812bf5` `feat: add shared CTC eval utilities`
- `96a2a8d` `fix: make CTC greedy decode single-sample explicit`
- `ac2c302` `refactor: use shared CTC utilities in error analysis`
- `62d883e` `refactor: share CTC decode logic in sweep tools`
- `df41a68` `fix: restore CTC tool validation behavior`
- `db453b9` `fix: tighten ratio target validation`
- `1f31a33` `fix: accept array-like ratio targets`
- `35693fa` `fix: restore CTC calibration compatibility`

## Core Files Changed

- `util/ctc_decoding.py`
- `util/ctc_metrics.py`
- `tests/test_ctc_eval_utils.py`
- `tests/test_paper_workflow_tools.py`
- `tools/analyze_ctc_errors.py`
- `tools/sweep_ctc_decode_bias.py`
- `tools/evaluate_short_rescue.py`
- `tools/analyze_short_blank_margin.py`

## What Landed

- Added shared CTC decoding utilities for:
  - collapse
  - greedy decode
  - ratio extraction from target metadata
  - decode-time blank/nonblank calibration
- Added shared CTC metric utilities for:
  - length buckets
  - Levenshtein op counts
  - aggregated totals
  - by-length summaries
- Migrated the following tools onto the shared utilities:
  - `tools/analyze_ctc_errors.py`
  - `tools/sweep_ctc_decode_bias.py`
  - `tools/evaluate_short_rescue.py`
  - `tools/analyze_short_blank_margin.py`
- Restored compatibility behaviors found during verification:
  - explicit single-sample decode guard
  - ratio target validation in sweep tooling
  - array-like `orig_size` acceptance
  - `analyze_ctc_errors.py` compatibility when `target["orig_size"]` is missing

## Verification Evidence

Recorded test and smoke coverage for this slice:

- CPU tests:
  - `python -m unittest tests.test_ctc_eval_utils tests.test_paper_workflow_tools -v`
  - recorded result: `Ran 15 tests ... OK`
- Trusted-baseline smoke:
  - `tools/analyze_ctc_errors.py` on `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth`
  - output: `logs/ctc_modularization_sanity_baseline_25.json`
  - headline fields:
    - `samples = 25`
    - `cer_micro = 0.011764705882352941`
    - `empty_pred_rate = 0.0`
    - `pred_gt_len_ratio = 1.0`
- Decode-bias smoke:
  - `tools/sweep_ctc_decode_bias.py`
  - output: `logs/ctc_modularization_sweep_smoke_10.json`
  - recorded result: exactly one row, `cer_micro = 0.0`
- Short-rescue smoke:
  - `tools/evaluate_short_rescue.py`
  - output: `logs/ctc_modularization_short_rescue_smoke_10.json`
  - recorded result: includes baseline row with `"policy": "baseline"`

## Baselines Preserved

The modularization slice did not modify these protected files:

- `config/MTH1000_dtlr.py`
- `config/MTH1000_MTH1200_stage1.py`
- `models/dino/dino.py`
- `engine.py`

## Current Worktree State

Known pre-existing dirty files remain outside this change:

- `models/dino/ops/MultiScaleDeformableAttention.egg-info/PKG-INFO`
- `models/dino/ops/MultiScaleDeformableAttention.egg-info/SOURCES.txt`

This handoff does not clean, revert, or otherwise touch them.

## Remaining Risks

- The implementation plan checklist file itself was not rewritten with checked boxes; status is frozen here instead.
- `tools/analyze_short_blank_margin.py` landed as part of the shared-tool refactor/fix commits rather than as its own dedicated commit from the original plan.
- Verification proves behavioral continuity for the touched evaluation tools, not paper-level performance superiority.
- The active thread goal was later marked `blocked` while waiting for a new method-direction approval; that blocked state is separate from this completed modularization slice.

## Next-Stage Recommendation

For future paper work, the most natural next method step remains:

- implement adaptive CTC candidate reranking on top of `util/ctc_decoding.py` and `util/ctc_metrics.py`
- require short-text gains without fixed-valid overall CER regression versus `logs/mth1000mth1200pre_mth1000ft_full_0513-2257`

This recommendation is recorded only as handoff context. It is not started by this document.
