# Method-Code Consistency Review

Last updated: 2026-06-08

This note records whether the current Method and Results sections match the implementation and experiment artifacts. It is not paper body text.

## Scope

Checked draft files:

- `docs/paper-drafts/03_method.md`
- `docs/paper-drafts/05_results_analysis.md`
- `docs/paper-drafts/97_experiment_evidence_inventory.md`
- `logs/paper_results_summary.md`

Checked code/config files:

- `models/dino/dino.py`
- `finetuning.py`
- `engine.py`
- `util/ctc_decoding.py`
- `tools/eval_ctc_micro_batch.py`
- `tools/sweep_ctc_decode_bias.py`
- `datasets/MTHCombo.py`
- `config/MTHV2_stage1_query_budget.py`
- `config/MTHV2_dtlr_ctc_count001.py`
- `config/HDRC_dtlr_ctc_count001.py`
- `config/MTHV2_dtlr_length_balance_probe.py`

## Overall Verdict

Status: mostly consistent, with scoped claims required.

The current method story is code-backed if SAQT is described as a localization-supervised query-to-CTC recognition framework for cropped vertical single-column text. The paper should keep the following boundaries:

- Query activation budget is a stage-1 localization/query-learning regularizer, not the later LGQ/query-count adapter.
- Expected-count is a lightweight optional CTC auxiliary with MTHv2-positive evidence only.
- HDRC qbudget-localization-query is variant-level evidence, not a pure query-budget ablation.
- Decode calibration is an evaluation/postprocess protocol selected on development data and fixed for test; it is not a language model and should not be framed as a main architecture contribution.
- Length-balanced sampling is an experiment-ready candidate, not a paper result.

## Character Localization Learning

Paper claim:

- Character boxes supervise detection-style queries during localization/query learning.
- The character-box branch is used as training supervision, not as a test-time input or final output interface.

Code evidence:

- `models/dino/dino.py::loss_labels` implements query-level character classification with matched targets.
- `models/dino/dino.py` retains standard box losses through the DINO/DTLR criterion path and constructs `weight_dict` for detection losses.
- `config/MTHV2_stage1_query_budget.py` sets `mode_chr = False`, so stage-1 uses detection/localization losses on character boxes rather than the CTC recognition loss.
- `config/MTHV2_stage1_query_budget.py` sets `mth1000_use_char_boxes = True`, `forced_direction = "vertical"`, and `mth1000_filter_direction = "vertical"`.

Result/evidence status:

- MTHv2 no-localization control in `logs/mthv2_no_structure_ctc_full_0605` collapses to clean AR/CR `0.00/0.00` and calibrated AR/CR `0.11/0.16`.
- This supports a lower-bound claim that the current query-to-CTC architecture does not train effectively from line-level CTC alone under the tested budget.

Paper handling:

- Safe wording: character localization learning provides the structural query representation needed by the current query-to-CTC pipeline.
- Unsafe wording: character boxes alone causally explain the full performance gap, or the same conclusion is proven across all ancient-text datasets.

## Query Activation Budget

Paper claim:

- The localization/query learning stage includes a length-aware one-sided query activation budget.
- It penalizes excessive nonblank query activations but does not force a fixed number of active queries.
- Transcript length is used only during training to construct the budget.

Code evidence:

- `models/dino/dino.py::compute_query_budget_loss` computes nonblank activation as `pred_logits.sigmoid().amax(dim=-1)`, sums over queries, sets the target budget to `budget_scale * target_length + budget_margin`, and penalizes only `clamp(expected_count - target_count, min=0)`.
- `models/dino/dino.py::loss_labels` adds `loss_query_budget` only when it is present in `weight_dict`.
- `models/dino/dino.py::build_dino` adds `loss_query_budget` only when `use_query_budget_loss=True` and `query_budget_loss_coef > 0`.
- `config/MTHV2_stage1_query_budget.py` enables this branch with `query_budget_loss_coef = 0.01`, `query_budget_scale = 2.0`, and `query_budget_margin = 8.0`.

Result/evidence status:

- MTHv2 single-factor ablation in `logs/paper_results_summary.md` supports this module:
  - w/o query budget calibrated AR/CR `96.10/96.37`
  - w/ query budget calibrated AR/CR `96.69/96.90`
- HDRC qbudget-localization-query reaches calibrated AR/CR `93.44/94.36`, but this checkpoint includes additional localization-query differences and is not a pure query-budget-only ablation.

Paper handling:

- Safe wording: MTHv2 provides a controlled ablation for query activation budget; HDRC provides variant-level target-domain evidence for the qbudget-localization-query branch.
- Unsafe wording: query budget is independently proven on HDRC, or query budget is universally effective.

Important separation:

- Do not conflate this module with `use_query_count_loss`, `use_query_activation_head`, or `use_activation_gating`. Those belong to later adapter experiments, including LGQ, and are not part of the current paper-facing SAQT core.

## Query Sorting and CTC Conversion

Paper claim:

- Query outputs are sorted by vertical position for vertical text and converted into a CTC sequence.
- Low-confidence queries allocate remaining probability mass to blank; high-confidence nonblank queries keep a small blank floor and are renormalized.
- Blank-only positions are inserted between query positions.

Code evidence:

- `models/dino/dino.py::loss_CTC` sorts each sample by target direction. When `_get_direction(target) == "vertical"`, it sets `sort_axis = 1`, i.e. predicted box center-y sorting.
- The sorted class logits are passed through sigmoid and converted into a CTC probability tensor with explicit blank at index `0`.
- If summed nonblank probability is below `1 - eps`, blank receives the remaining mass.
- Otherwise blank receives `eps = 0.003`, and nonblank probabilities are renormalized to `1 - eps`.
- A `blank_tensor` is interleaved between query positions, doubling the CTC time dimension and supporting repeated characters.
- `engine.py` contains direction-aware CTC decoding utilities for evaluation paths.

Status: consistent with `03_method.md`.

## CTC Expected-Count Auxiliary

Paper claim:

- The recognition stage may include a lightweight expected-count auxiliary that aligns expected nonblank count with transcript length.
- The auxiliary does not change model architecture or inference.
- It should be treated as optional rather than SAQT's core mechanism.

Code evidence:

- `models/dino/dino.py::loss_CTC` enables this only when `loss_ctc_count` is present in `weight_dict`.
- The implementation computes `expected_nonblank_count = new_pred_logits[:, :, 1:].sum(-1).sum(-1)`, divides by target length, and applies `smooth_l1_loss` toward `1`.
- `ctc_count_loss_short_weight` upweights targets of length `<= 2` when configured.
- `models/dino/dino.py::build_dino` adds `loss_ctc_count` only when `ctc_count_loss_coef > 0`.
- `config/MTHV2_dtlr_ctc_count001.py` enables `ctc_count_loss_coef = 0.01` and `ctc_count_loss_short_weight = 3.0`.

Result/evidence status:

- MTHv2 evidence is positive but small:
  - direct AR/CR `96.17/96.29 -> 96.33/96.50`
  - calibrated AR/CR `96.69/96.90 -> 96.75/97.00`
- HDRC `count001` did not produce stable positive evidence according to the experiment inventory and risk matrix.

Paper handling:

- Safe wording: expected-count is a lightweight optional auxiliary that gives a small MTHv2 gain.
- Unsafe wording: expected-count is a core contribution or a cross-dataset robust module.

## Charset-Aware Classifier Adaptation

Paper claim:

- For shared characters between source and target charsets, classifier rows are inherited.
- For target characters not found in the source charset, rows are initialized from unused source rows when possible and random source rows otherwise.
- Adaptation applies to decoder classifier and encoder output classifier.
- The module is a training initialization/adaptation strategy, not an inference-time module.

Code evidence:

- `finetuning.py` has two `--new_class_embedding` branches covering resume-finetuning and head-reconstruction paths.
- When `--smart_mapping` is enabled, it loads `old_charset`, normalizes charset representation, builds `mapping`, and maps shared target characters to their source index.
- Target characters absent from the source charset are mapped to unused source rows when available; if not enough unused rows exist, random source indices are appended.
- The mapped weights and biases are copied into:
  - `model.class_embed`
  - `model.transformer.decoder.class_embed`
  - `model.transformer.enc_out_class_embed`
- When `--smart_mapping` is disabled, the new classifier heads are initialized from random source rows via `_init_modulelist_from_random_rows` and `_init_linear_from_random_rows`, matching the random-head ablation.

Result/evidence status:

- HDRC random-head vs charset-aware comparison supports the module under target-charset mismatch:
  - random-head calibrated AR/CR `82.72/83.97`
  - charset-aware calibrated AR/CR `90.70/91.80`

Paper handling:

- Safe wording: the module is supported on HDRC, where target charset mismatch is present.
- Unsafe wording: the module has been fully validated across all target datasets.

## Head Reconstruction and Full Recognition Training

Paper claim:

- SAQT first adapts or reconstructs classifier heads, then performs full-model CTC recognition training.
- Full-model recognition training is needed beyond head-only reconstruction.

Code evidence:

- `finetuning.py` rebuilds classifier modules under `--new_class_embedding`.
- In head-reconstruction mode, `parameters_to_optimize` is restricted to classifier-related parameters.
- In resume-finetuning/full recognition mode, the optimizer is rebuilt for the broader model parameter set.
- The same CTC loss path in `models/dino/dino.py::loss_CTC` is used for recognition-stage training.

Result/evidence status:

- MTHv2 head-only vs full:
  - calibrated AR/CR `93.83/95.03 -> 96.69/96.90`
- HDRC head-only vs full:
  - calibrated AR/CR `85.97/89.72 -> 90.70/91.80`

Status: consistent and well supported for the current two datasets.

## Decode Calibration

Paper claim:

- Blank/nonblank logit bias is a fixed inference calibration selected on the development set and then applied to test.
- It is not a language model and does not use external text.

Code evidence:

- `util/ctc_decoding.py::apply_ctc_calibration` adds `blank_bias` to blank scores and `nonblank_bias` to nonblank scores before decoding.
- `tools/sweep_ctc_decode_bias.py` enumerates bias settings on a validation/development split.
- `tools/eval_ctc_micro_batch.py` applies fixed `--blank_bias` and `--nonblank_bias` for evaluation.
- `logs/paper_results_summary.md` separates clean decoding from bias decoding for every paper-facing result.

Paper handling:

- Safe wording: validation-protocol fixed blank/nonblank calibration is used to report calibrated results alongside direct decoding.
- Unsafe wording: calibration is learned from the test set, or calibration is an SAQT architecture module.

## Length-Balanced Sampling Probe

Paper claim status:

- Not part of the current paper body.
- It can be discussed only as a queued internal experiment if needed, not as evidence.

Code evidence:

- `finetuning.py::_build_length_balanced_sampler` constructs a `WeightedRandomSampler` from `dataset.samples` when `mth1000_length_balance=True`.
- `datasets/MTHCombo.py` now exposes flattened `samples` by concatenating child dataset samples, enabling length-balanced sampling for MTHv2-combo.
- `config/MTHV2_dtlr_length_balance_probe.py` sets length-bin weights for `1`, `2`, `3-5`, `6-10`, and `11+`.
- `tests/test_mth_combo_dataset.py` verifies that flattened samples are exposed without changing index routing.

Experiment status:

- Smoke evidence only: the sampler path was verified to activate.
- Full training did not run because `tmux` launch was blocked by the execution environment.
- No validation CER or AR/CR result exists; it must not enter paper tables.

Paper handling:

- Do not include length-balanced sampling as a method contribution or result unless a full run produces valid/test evidence.

## Negative or Internal Modules

The following implemented modules or configs should remain outside the paper-facing method unless future evidence changes:

- `use_query_activation_head`, `use_query_count_loss`, and `use_activation_gating` in LGQ-style adapters: current smoke result is negative.
- `use_sorted_ctc_refiner`: current result is negative.
- `ctc_viterbi_loss_coef` / DCTC-lite: current result is negative.
- `ctc_blank_max`: current blank-cap result is negative.
- glyph prototype auxiliary: current evidence is unstable.
- adaptive pred-short decode: current evidence is mixed and should remain internal.

## Remaining Method Risks

1. The strongest current story is a conservative two-dataset method paper, not a broad universal OCR framework.
2. Query activation budget has MTHv2 single-factor evidence; HDRC evidence is variant-level.
3. Expected-count is optional and MTHv2-positive only.
4. The no-localization control is useful but weak; it supports a lower-bound claim rather than a full causal decomposition.
5. Decode calibration improves results, so every main table should keep both direct and calibrated results visible.

## Verification Status

- `03_method.md` matches the current implementation if the wording remains scoped as above.
- `05_results_analysis.md` matches `logs/paper_results_summary.md` for the current MTHv2 qbudget-count001 and HDRC qbudget-localization-query paper-facing results.
- `97_experiment_evidence_inventory.md` correctly separates usable evidence, optional evidence, and not-paper-ready evidence.
- No code or config change was made by this review.
