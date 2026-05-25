# CTC Evaluation Modularization Design

## Context

The paper goal needs both stronger recognition results and cleaner experiment
infrastructure. The latest MTH1000 comparison is:

- `logs/paper_experiment_mainline_compare_0525.md`
- trusted full finetune baseline: `logs/mth1000mth1200pre_mth1000ft_full_0513-2257`
- strongest short-text rescue candidate: `logs/mth1000_realmain_shortboost_presence_0524-2307`

The new shortboost-presence run improves short columns but does not improve the
fixed valid-set overall CER:

- best log CER improves from `0.1510` to `0.1492`
- fixed valid CTC summary CER regresses from `0.0784` to `0.0796`
- len=1 CER improves from `0.2902` to `0.2769`
- len>=11 CER regresses from `0.0583` to `0.0594`

This means the next useful step is not another loosely measured config variant.
We need a stable CTC evaluation layer so future adaptive reranking and
short-column methods are measured with one shared definition.

## Problem

The repository currently duplicates CTC decoding and metric logic across:

- `engine.py`
- `tools/analyze_ctc_errors.py`
- `tools/sweep_ctc_decode_bias.py`
- `tools/evaluate_short_rescue.py`
- `tools/analyze_short_blank_margin.py`
- `tools/visualize_ctc_by_length.py`

Repeated local implementations make paper comparisons fragile. Small differences
in CTC collapse, blank/nonblank calibration, length buckets, or edit-distance
accounting can make two runs look comparable when they are not.

## Goals

1. Create one shared CTC decoding module for greedy decode and calibration.
2. Create one shared CTC metric module for edit operations and length buckets.
3. Keep current CLI tools available with their existing arguments and output
   formats where practical.
4. Preserve trusted baseline configs and training behavior.
5. Make adaptive CTC reranking the natural next implementation step.

## Non-Goals

This phase will not:

- change `config/MTH1000_dtlr.py`
- change `config/MTH1000_MTH1200_stage1.py`
- change trusted checkpoints or log directories
- change `models/dino/dino.py` CTC loss behavior
- introduce a new training loss
- implement the adaptive reranker itself
- delete any logs, datasets, or checkpoints

## Proposed Modules

### `util/ctc_decoding.py`

Responsibilities:

- `collapse_ctc(tokens, blank=0)`: remove repeats and blanks.
- `decode_greedy(pred_probs, charset_size, blank=0)`: convert CTC probabilities
  or scores to label ids.
- `ratio_from_target(target, default=1.0)`: read `orig_size` safely.
- `apply_ctc_calibration(pred_probs, blank_bias=0.0, nonblank_bias=0.0,
  ratio_nonblank_bias=0.0, ratio_min=1.5, ratio_max=2.0, target=None)`: apply
  decode-time log-space calibration without changing training probabilities.

Design constraints:

- Accept tensors already produced by `criterion.loss_CTC(..., return_preds=True)`.
- Preserve token convention: blank token is `0`; character token `k` maps to
  label id `k - 1`.
- Return plain Python label-id lists for script compatibility.

### `util/ctc_metrics.py`

Responsibilities:

- `LENGTH_BIN_KEYS = ["1", "2", "3-5", "6-10", "11+"]`
- `length_bin(gt_len)`: shared bucket definition.
- `levenshtein_ops(gt_labels, pred_labels)`: return distance, insertions,
  deletions, and substitutions.
- `CtcTotals`: aggregate sample count, gt chars, pred chars, edit ops, and
  empty predictions.
- `summarize_by_length(rows)`: produce the same shape currently emitted by
  `ctc_error_summary_valid.json`.

Design constraints:

- Keep metric names compatible with existing paper reports:
  `cer_micro`, `pred_gt_len_ratio`, `empty_pred_rate`, `ins_rate`, `del_rate`,
  `sub_rate`.
- Use the same length buckets as existing paper comparison tables.
- Avoid importing model, dataset, CUDA, or matplotlib code.

## Tool Integration

First-pass integrations:

- `tools/analyze_ctc_errors.py`
  - replace local `remove_duplicates`, `length_bin`, `levenshtein_ops`, and
    `Totals` with shared utilities.
- `tools/sweep_ctc_decode_bias.py`
  - replace local ratio/calibration/decode/summary logic with shared utilities.
- `tools/evaluate_short_rescue.py`
  - reuse shared greedy decode, ratio extraction, length buckets, and totals.
- `tools/analyze_short_blank_margin.py`
  - reuse shared greedy decode and edit ops.

Second-pass integration:

- `tools/visualize_ctc_by_length.py`
  - reuse shared collapse, length bucket, and edit distance after the core
    non-visual tools are verified.

`engine.py` will not be changed in the first implementation unless the shared
functions prove byte-for-byte compatible with its current decode behavior in a
small sanity check. This keeps training/evaluation risk low.

## Data Flow

The unchanged model path remains:

1. Build dataset and model from the selected config.
2. Load checkpoint.
3. Run `criterion.loss_CTC(..., return_preds=True)`.
4. Pass returned CTC probabilities to `util.ctc_decoding`.
5. Pass decoded labels and ground-truth labels to `util.ctc_metrics`.
6. Emit the same JSON/JSONL/Markdown artifacts as before.

## Error Handling

- Calibration must clamp probabilities before `log` to avoid `-inf`.
- Missing `orig_size` should fall back to a configurable default ratio.
- Empty labels and empty predictions must be valid metric inputs.
- Unknown token ids outside `[1, charset_size]` are ignored after CTC collapse,
  matching current script behavior.

## Verification

Minimum verification before implementation is considered complete:

1. Run a CPU-only unit-style check for:
   - duplicate collapse
   - blank removal
   - label id mapping
   - edit operation counts
   - length bucket assignment
2. Run a small GPU sanity command on a trusted checkpoint with `--max_samples 25`
   and confirm the refactored `tools/analyze_ctc_errors.py` summary matches the
   previous local implementation for the same sample count.
3. Run the fixed-valid command for the trusted full finetune baseline and confirm
   the headline values remain consistent with:
   - `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/paper_metrics_report.md`
4. Rebuild the paper comparison table and confirm no unexpected metric drift.

## Baseline Preservation

The trusted baselines remain unchanged:

- stage-1: `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`
- head reconstruction:
  `logs/mth1000mth1200pre_mth1000ft_head_0513-2057/checkpoint_best_regular.pth`
- full finetuning:
  `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth`

This design changes experiment tooling only. It does not change training
semantics or reported baseline checkpoints.

## Follow-Up After This Phase

After the shared CTC evaluation layer is verified, the next paper-facing method
should be adaptive CTC candidate reranking. That method should be implemented as
a small policy layer on top of `util/ctc_decoding.py` and evaluated with
`util/ctc_metrics.py`, reporting:

- overall valid CER
- len=1 CER and empty rate
- len=2 CER and empty rate
- len>=11 CER
- pred/GT length ratio

The acceptance bar for the reranker should be stricter than the current
shortboost-presence result: it should reduce short-text collapse without
increasing fixed-valid overall CER versus the trusted full baseline.
