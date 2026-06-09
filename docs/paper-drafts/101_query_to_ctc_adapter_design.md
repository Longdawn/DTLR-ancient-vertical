# Localization-Guided Query-to-CTC Adapter Design

Date: 2026-06-07

## Why This Module

Changing the backbone is not the most defensible way to turn DTLR into a distinct vertical ancient-text recognizer. The most distinctive part of this repository is the bridge from localization queries to CTC recognition:

1. sort queries by predicted vertical coordinate;
2. convert query character logits into a probability sequence with explicit blank;
3. insert blank-only positions;
4. train with line-level CTC.

This bridge is where the method stops being a detector and becomes a recognizer. A focused adapter here is more paper-relevant than replacing ResNet or adding a generic Transformer block.

## Existing Code Hooks

File: `models/dino/dino.py`

- `loss_CTC`: current query sorting and CTC conversion path.
- `apply_activation_gating`: already supports activation-conditioned blank/nonblank logit shifts.
- `compute_query_count_loss`: predicts aggregate active query count.
- model flags:
  - `use_query_activation_head`
  - `use_activation_gating`
  - `query_count_loss_coef`
  - `activation_gate_blank_coef`
  - `activation_gate_nonblank_coef`

Existing negative evidence:

- `docs/superpowers/handoffs/2026-05-25-csaq-count-only-negative-result.md`
- Count-only activation supervision made the expected active-query count numerically reasonable, but recognition remained blank-collapsed.
- Therefore the new module should not be framed as a count-loss contribution.

## Proposed Module

Name:

- Localization-Guided Query-to-CTC Adapter

Core idea:

- use localization-aware query order as the sequence scaffold;
- learn a query activation signal for whether each sorted query should contribute nonblank evidence;
- use the activation signal to adapt blank/nonblank logits before CTC;
- keep CTC as the sequence objective, so inference still outputs only text.

## Minimal Implementation

### Adapter Inputs

For each sorted query \(q\):

- decoder query feature \(h_q\);
- predicted box center \(b_q=(x_q,y_q,w_q,h_q)\);
- character logits \(s_q\);
- optional local spacing features:
  - \(\Delta y^-_q = y_q-y_{q-1}\)
  - \(\Delta y^+_q = y_{q+1}-y_q\)

### Adapter Output

Predict an activation logit \(g_q\). Convert it to a gate:

```text
a_q = sigmoid(g_q)
```

Use it to adjust CTC logits:

```text
z_blank'    = z_blank    + lambda_blank * (1 - a_q)
z_nonblank' = z_nonblank + lambda_char  * a_q
```

The current `apply_activation_gating` already implements this simple version.

### Safer Revision Over Existing CSAQ

Do not rely on global count loss alone. The adapter should be trained with:

- CTC loss as the main objective;
- optional weak query-count regularization with a small coefficient;
- no claim that count matching alone solves recognition.

Recommended first config:

```python
use_query_activation_head = True
query_activation_init_bias = -4.0
use_activation_gating = True
activation_gate_blank_coef = 0.10
activation_gate_nonblank_coef = 0.10
use_query_count_loss = True
query_count_loss_coef = 0.001
query_count_short_weight = 1.0
```

This is intentionally weaker than the old count-gating settings to reduce the risk of overpowering CTC.

Implemented experiment config:

- `config/MTHV2_dtlr_lgq_adapter.py`
- 2026-06-07 CPU-side verification: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_query_activation_module.py` passed 7 tests, and `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m py_compile config/MTHV2_dtlr_lgq_adapter.py` succeeded. This verifies hook/config availability, not recognition quality.
- 2026-06-07 GPU smoke completed on physical GPU0: `logs/mthv2_lgq_adapter_smoke_0607`.
- Smoke result: the run starts, writes checkpoints, includes `loss_query_count`, and does not crash from missing keys or tensor shape mismatch. However, epoch-0 validation CER is `14.8588%` (`test_cer_oracle_direction=0.148588`) with `test_blank_pred_ratio_unscaled=0.989749`, which is clearly weaker than the MTHv2 qbudget head-only reference validation CER of about `8.56%`.
- Interpretation: this is an internal negative result. The current LGQ adapter setting should not be included in the paper body.

## Minimum Credible Experiment

### Smoke Test

Use MTHv2 qbudget head checkpoint:

- `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth`

Run 1 epoch or `max_optimizer_steps` smoke on GPU0 after current evaluations complete. Do not launch while `logs/hdrc_qbudget_full_0607` is still training on GPU0.

Smoke command:

```bash
tmux new-session -d -s mthv2_lgq_adapter_smoke_0607 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl --save_log --output_dir logs/mthv2_lgq_adapter_smoke_0607 -c config/MTHV2_dtlr_lgq_adapter.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=1 eval_epoch=1 max_iterations=10000 max_optimizer_steps=1000'
```

Required pass criteria:

- training starts without missing-key or shape mismatch errors;
- validation does not collapse to near-empty prediction;
- validation CER is not catastrophically worse than the starting head-only checkpoint.

Smoke outcome on 2026-06-07:

- pass: no fatal shape/key error; GPU0-only execution completed; `checkpoint.pth`, `checkpoint_best_regular.pth`, and `log.txt` were written.
- weak pass: not all-blank, but blank ratio remains high (`0.989749`).
- fail: validation CER regresses to `14.8588%`, clearly worse than the starting head-only checkpoint. Do not continue to a full LGQ run under this configuration.

### Full Experiment

If smoke passes:

- full finetune from the same qbudget head checkpoint;
- compare against baseline full qbudget run:
  - `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth`
- evaluate clean valid/test, validation bias sweep, and fixed-bias test using `docs/EXPERIMENT_POSTPROCESS.md`.

Paper table should only include the adapter if it improves or at least gives a meaningful diagnostic. If it hurts, keep it as an internal negative result.

## Failure Modes

Evidence against the module:

- blank-collapse or strong under-decoding after validation calibration;
- worse MTHv2 AR/CR than baseline qbudget full finetuning;
- improved aggregate active count but no recognition improvement, repeating the count-only failure.

## Paper Interpretation

If successful, this becomes the clearest "our own model" component:

- localization-supervised query learning gives spatially meaningful queries;
- query activation budget controls excessive nonblank query responses during localization learning;
- localization-guided query-to-CTC adapter controls which sorted queries enter the recognition sequence.

If unsuccessful, the current SAQT paper should not include it. The safer paper remains:

- character-localization information learning;
- query activation budget;
- charset-aware classifier adaptation;
- CTC recognition and validation-fixed calibration.
