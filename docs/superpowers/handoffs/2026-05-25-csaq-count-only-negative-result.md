# CSAQ Count-Only Negative Result

Date: 2026-05-25

## Experiment

- Run directory: `logs/mth1000_csaq_count_only_initbias_0525`
- Config: `config/MTH1000_dtlr_csaq_count_only.py`
- Pretrain checkpoint: `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`
- Best checkpoint:
  - `logs/mth1000_csaq_count_only_initbias_0525/checkpoint_best_regular.pth`
  - same-epoch checkpoint: `logs/mth1000_csaq_count_only_initbias_0525/checkpoint.pth`

## Training Summary

- Best epoch: `0`
- Best valid CER from training log: `0.8646675234781909`
- Training log:
  - `logs/mth1000_csaq_count_only_initbias_0525/log.txt`
  - `logs/mth1000_csaq_count_only_initbias_0525/info.txt`

The run was manually interrupted during `epoch 1` validation. This does not affect the main conclusion because the saved `epoch 0` best checkpoint is already catastrophically worse than the trusted baseline.

## Count Branch Behavior

The `query_activation_init_bias = -4.0` fix solved the original activation prior problem:

- before fix: initial `query_expected_count` was `500+`
- after fix: validation average `query_expected_count` was close to target length

Epoch-0 validation log:

- `test_query_expected_count_unscaled = 9.5061`
- `test_query_target_count_unscaled = 9.7220`
- `test_loss_query_count_unscaled = 6.4058`

Observed during interrupted epoch-1 validation:

- `query_expected_count_unscaled` stayed roughly in `9.4 ~ 9.8`
- no collapse to `0`
- no drift to very large values

Conclusion on this subproblem:

- the count branch became numerically stable
- the count loss became meaningful as a supervised signal
- but that did **not** translate into usable CTC recognition

## Unified Evaluation

### Result files

- Greedy:
  - `logs/mth1000_csaq_count_only_initbias_0525/ctc_error_summary_valid.json`
  - `logs/mth1000_csaq_count_only_initbias_0525/ctc_error_cases_valid.jsonl`
- Fixed bias (`blank=-0.3`, `nonblank=0.3`):
  - `logs/mth1000_csaq_count_only_initbias_0525/ctc_error_summary_valid_bias_b-03_nb03.json`
  - `logs/mth1000_csaq_count_only_initbias_0525/ctc_error_cases_valid_bias_b-03_nb03.jsonl`

### Metrics

| Setting | overall CER | len=1 CER | len=2 CER | len>=11 CER | empty rate | del | sub | ins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean baseline | 0.0784 | 0.2902 | 0.2826 | 0.0583 | 0.0486 | 0.0387 | 0.0373 | 0.0024 |
| fixed bias baseline | 0.0749 | 0.2757 | 0.2707 | 0.0556 | 0.0432 | 0.0320 | 0.0401 | 0.0028 |
| count-only greedy | 0.8166 | 0.9831 | 0.9674 | 0.7960 | 0.4103 | 0.7580 | 0.0576 | 0.0010 |
| count-only fixed bias | 0.8059 | 0.9819 | 0.9642 | 0.7841 | 0.4034 | 0.7421 | 0.0625 | 0.0013 |

## Main Phenomenon

This run exhibits a strong mismatch:

- `query_expected_count` is stable and near `query_target_count`
- but CTC decoding is still severely blank-collapsed / under-decoded

Concrete symptoms:

- greedy `pred_gt_len_ratio = 0.2431`
- greedy `empty_pred_rate = 0.4103`
- greedy `del_rate = 0.7580`
- fixed bias does not recover the model:
  - `overall CER 0.8166 -> 0.8059`
  - still far from the baseline `0.0749`

## Conclusion

**Global count consistency is decoupled from the actual CTC recognition objective in this first CSAQ count-only form.**

What the model learned:

- how many queries should be active in aggregate

What it did not learn:

- which specific queries should carry characters
- how those active queries should produce correct nonblank character logits

So this module can satisfy the global count constraint while still producing blank-heavy or nearly useless character sequences.

## Decision

This experiment should be treated as a **clear negative result**.

Do not continue directly with:

- `gating-only`
- `count+gating`
- more tuning of `query_count_loss_coef`
- more tuning of `query_activation_init_bias`

## Recommended Next Step

Shift focus from:

- "how many characters should be active"

to:

- "which character should each query classify to"

That means the next experiment should target **query-level character classification quality**, not query-count regulation. The most direct next module is a minimal glyph/prototype-guided classification branch.
