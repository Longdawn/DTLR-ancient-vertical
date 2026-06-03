# MTHv2/HDRC Short-Text Recognition Goal Plan

Date: 2026-05-28

## Objective

Run recognition-only experiments on MTHv2 and HDRC. Do not process CHDAC. Do not run detection or stage-1 box experiments.

The target is to improve short-text `len=1/2` empty/deletion behavior while keeping overall AR/CR/CER from regressing. Every method change must be a single switchable module; default baselines stay unchanged.

## Current Constraints

- Target datasets only:
  - MTHv2 via `dataset_file=mth_combo` and `config/MTHV2_dtlr.py`.
  - HDRC via `dataset_file=mth1000` plus `mth1000_root=hdrc_dtlr`, `mth1000_raw_root=HDRC`, `mth1000_image_ext=jpg`.
- Excluded:
  - CHDAC.
  - detection/stage-1 training.
  - data deletion or mutation of original data.
  - simultaneous full training runs.
- Logs must be under a unique `logs/` directory.
- Each module flow:
  1. implement one switchable module,
  2. smoke test,
  3. launch at most one full training run,
  4. summarize overall AR/CR/CER, `len=1/2` empty rate, length-bucket CER, and error cases,
  5. stop after two consecutive modules without improvement or after three modules total.

## Code/Log State Read

Relevant existing code:

- `finetuning.py`: CTC recognition finetuning entry point.
- `models/dino/dino.py`: owns CTC loss path and current experimental short-query/prototype hooks.
- `tools/analyze_ctc_errors.py`: produces CER, insertion/deletion/substitution rates, empty prediction rate, length-bucket CER, and error JSONL.
- `tools/sweep_ctc_decode_bias.py`: evaluates decode-time blank/nonblank bias sweeps.
- `tools/eval_chinese_micro.py`: computes overall micro/macro AR/CR/CER, but it does not yet share the CTC calibration path.

Relevant existing uncommitted modules:

- Short Query CE helper in `models/dino/dino.py`, controlled by config values:
  - `short_gt_ce_loss_coef`
  - `short_gt_ce_max_len`
  - `short_gt_ce_gamma`
- Prototype direct-fusion branch in `models/dino/dino.py`, controlled by:
  - `use_glyph_prototype_head`
  - `glyph_proto_fuse_coef`
  - `glyph_proto_temperature`
  - `glyph_proto_trainable`
- Prototype direct-fusion already has a negative MTH1000 result in `docs/superpowers/handoffs/2026-05-26-learnable-prototype-fusion-negative.md`; do not spend an MTHv2/HDRC module slot on that formulation.

## Recognition Baselines

### MTHv2

Head reconstruction:

- `logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth`

Full finetuning:

- run: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- checkpoint: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`
- best validation CER from `log.txt`: `0.11397798822246911` at epoch `9`

Clean valid CTC error summary:

- file: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_valid_clean_0528.json`
- overall CER: `0.051956146066460804`
- overall empty rate: `0.03379612714651078`
- deletion rate: `0.0272434535444819`
- `len=1`: CER `0.26737967914438504`, empty `0.1948900772430184`, deletion `0.1948900772430184`
- `len=2`: CER `0.22151898734177214`, empty `0.030854430379746837`, deletion `0.13765822784810128`
- `11+`: CER `0.03324255392729002`

Best available valid decode-bias sweep row:

- file: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/decode_bias_sweep_valid_0528.json`
- setting: `blank_bias=-2.0`, `nonblank_bias=1.0`, `ratio_nonblank_bias=0.0`
- overall CER: `0.04561980037205964`
- overall empty rate: `0.007124588966021191`
- deletion rate: `0.007677271310802006`
- `len=1`: CER `0.22281639928698752`, empty `0.0451574569221628`, deletion `0.0451574569221628`
- `len=2`: CER `0.19026898734177214`, empty `0.0015822784810126582`, deletion `0.028085443037974684`
- `11+`: CER `0.02970864133488955`

### HDRC

Head reconstruction:

- `logs/mth1000mth1200pre_hdrcft_head_0527-1530/checkpoint_best_regular.pth`

Full finetuning:

- run: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`
- checkpoint: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth`
- best validation CER from `log.txt`: `0.10746200736109689` at epoch `1`

Clean valid CTC error summary:

- file: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_clean_0527.json`
- overall CER: `0.13437839369186458`
- overall empty rate: `0.017869656622284513`
- deletion rate: `0.0863119127437556`
- `len=1`: CER `0.1392156862745098`, empty `0.09607843137254903`, deletion `0.09607843137254903`
- `len=2`: CER `0.09745762711864407`, empty `0.003389830508474576`, deletion `0.06610169491525424`
- `11+`: CER `0.15805491233873636`

## Module Queue

### Module 1: SGQ Short Query CE

Status: MTHv2 completed and summarized; do not repeat this MTHv2 run.

MTHv2 result:

- summary: `experiments/notes/mthv2_sgq_short_ce_summary_0529.md`
- run: `logs/mthv2_sgq_short_ce_full_0528-2240`
- best checkpoint: `logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth`
- best validation CER from `log.txt`: `0.11552016232612522` at epoch `5`
- baseline validation CER: `0.11397798822246911`
- clean CTC:
  - overall CER worsened from `0.051956146066460804` to `0.052277212763345515`
  - `len=1` empty improved from `0.1948900772430184` to `0.1711229946524064`
  - `len=2` empty improved from `0.030854430379746837` to `0.022151898734177215`
  - `len=1/2` CER worsened
- calibrated CTC:
  - best SGQ setting: `blank_bias=-1.6`, `nonblank_bias=1.0`, `ratio_nonblank_bias=0.0`
  - overall CER improved from calibrated baseline `0.04561980037205964` to `0.04455272576182517`
  - `len=1/2` CER remained worse than calibrated baseline
- decision: counts as one no-improvement module for the original short-text objective on MTHv2.

HDRC status:

- HDRC SGQ config exists, but the MTHv2 result does not justify spending a full HDRC SGQ training run unless the objective is broadened to overall calibrated CER.

Rationale:

- Directly targets short sample query-to-character supervision.
- Training-only; inference path remains unchanged unless evaluated with explicit decode calibration.
- Smaller and safer than prototype-logit fusion.

Implementation requirements:

- Add target-dataset configs, not shared baseline edits:
  - `config/MTHV2_dtlr_sgq_short_ce.py`
  - `config/HDRC_dtlr_sgq_short_ce.py`
- Keep the module switchable with `short_gt_ce_loss_coef=0.0` equivalent to baseline behavior.
- Smoke-test the helper and config loading before full training.

Planned full-training order:

1. MTHv2 SGQ full finetune from `logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth`.
2. HDRC SGQ full finetune from `logs/mth1000mth1200pre_hdrcft_head_0527-1530/checkpoint_best_regular.pth`, only after the MTHv2 run completes or is stopped.

### Module 2: Short-Bucket Decode Calibration

Status: completed and summarized.

Summary:

- `experiments/notes/module2_decode_calibration_summary_0529.md`

MTHv2 result:

- baseline checkpoint: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`
- best setting: `blank_bias=-2.0`, `nonblank_bias=1.0`, `ratio_nonblank_bias=0.0`
- overall AR improved from `0.9480438539335392` to `0.9543801996279404`
- overall CR improved from `0.9502724345354708` to `0.9582141137142696`
- overall CER improved from `0.051956146066460804` to `0.04561980037205964`
- `len=1` empty improved from `0.1948900772430184` to `0.0451574569221628`
- `len=2` empty improved from `0.030854430379746837` to `0.0015822784810126582`
- `len=1` CER improved from `0.26737967914438504` to `0.22281639928698752`
- `len=2` CER improved from `0.22151898734177214` to `0.19026898734177214`

HDRC result:

- baseline checkpoint: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth`
- best setting: `blank_bias=-2.0`, `nonblank_bias=0.4`, `ratio_nonblank_bias=0.0`
- overall AR improved from `0.8656216063081354` to `0.8768119363520468`
- overall CR improved from `0.8694461494877001` to `0.8871051513291468`
- overall CER improved from `0.13437839369186458` to `0.12318806364795316`
- `len=1` empty improved from `0.09607843137254903` to `0.047058823529411764`
- `len=2` empty improved from `0.003389830508474576` to `0.0`
- `len=1` CER improved from `0.1392156862745098` to `0.12352941176470589`
- `len=2` CER improved from `0.09745762711864407` to `0.08728813559322034`

Decision:

- useful; satisfies the current goal on both target datasets.
- no additional full training is needed for the current goal unless a stricter target is set for remaining substitution/over-activation errors.

Rationale:

- It is a switchable decode-time module, no training-data mutation.
- MTHv2 sweep already improves overall CER and sharply reduces `len=1/2` empty/deletion.

Implementation requirement:

- Make the chosen calibration setting explicit in experiment summaries.
- If converting from evaluation-only to reusable module, keep default decode behavior unchanged.

### Module 3: Short Query Selector/Rerank Diagnostic

Status: not implemented for this goal.

Rationale:

- Use only if SGQ and calibration do not exhaust the short deletion/empty gains.
- Must start as a diagnostic or evaluation-time switch before any training module.

## Summary Template Per Full Run

For every completed training run, write an experiment summary under `experiments/notes/` with:

- module name and switch values,
- dataset and exact launch command,
- log directory and checkpoint paths,
- smoke-test command and result,
- best validation epoch and overall CER from `log.txt`,
- overall AR/CR/CER from `tools/eval_chinese_micro.py` or equivalent,
- clean and calibrated CTC summaries:
  - overall CER,
  - `len=1/2` empty rate,
  - length-bucket CER,
  - insertion/deletion/substitution rates,
- representative error cases from the JSONL output,
- decision: useful, neutral, or harmful,
- whether it counts as a no-improvement module.

## Current Next Step

Finish Module 1 setup for MTHv2/HDRC:

1. Add MTHv2 and HDRC SGQ configs.
2. Run unit/config smoke tests for SGQ.
3. If smoke passes and no training is already running, launch one full MTHv2 SGQ run with a unique `logs/` directory.
