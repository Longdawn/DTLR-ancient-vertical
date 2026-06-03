# Learnable Prototype Fusion Negative Result

Date: 2026-05-26

## Scope

This handoff records the negative result for the first learnable prototype-logit fusion direction in DTLR finetuning.

It covers:

- the zero-fuse regression repair status
- the first-valid canary with `glyph_proto_fuse_coef = 0.01`
- the decision to stop this direction

## Regression Status

The earlier zero-fuse regression bug has been fixed.

Confirmed properties after the RNG-isolation fix:

- enabling `use_glyph_prototype_head=True` no longer changes the baseline-sensitive random initialization used by `--new_class_embedding`
- `class_embed`, `transformer.decoder.class_embed`, `transformer.enc_out_class_embed`, and `label_enc` are identical to baseline under the same seed
- with `glyph_proto_fuse_coef = 0.0`:
  - `pred_logits` are identical to baseline
  - sorted logits entering the CTC path are identical to baseline

So the engineering regression is resolved.

## Zero-Fuse Result

Zero-fuse tensor-level regression passed after the RNG fix.

This means:

- the prototype branch can now be enabled without perturbing the baseline path when fusion strength is zero
- any later degradation with nonzero fusion should be attributed to the fusion behavior itself, not RNG contamination

## fuse=0.01 Canary

### Run

- Run directory: `logs/mth1000_proto_learnable_fuse001_rngfix_0526`
- Config: `config/MTH1000_dtlr_proto_learnable_fuse_001.py`
- Pretrain checkpoint: `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`

### Checkpoints

- `logs/mth1000_proto_learnable_fuse001_rngfix_0526/checkpoint.pth`
- `logs/mth1000_proto_learnable_fuse001_rngfix_0526/checkpoint_best_regular.pth`

### First-valid result

- `epoch 0 valid CER = 0.945653`
- `loss_CTC = 5.4260`
- `blank_pred_ratio = 0.9983`

### Baseline reference

- clean baseline overall CER: `0.0784`
- fixed bias baseline overall CER: `0.0749`
- clean baseline epoch-0 valid CER reference:
  - `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/log.txt`
  - `epoch 0 test_cer_oracle_direction = 0.16186604190589077`

## Main Phenomenon

The run does not show a mild degradation. It collapses almost immediately:

- first-valid CER is near `0.95`
- validation `blank_pred_ratio` is pinned near `1.0`

This indicates that even a very small learnable prototype-logit fusion factor (`0.01`) is enough to push the CTC path into strong blank collapse.

## Conclusion

**Directly adding learnable prototype similarity logits into the CTC classification logits causes severe blank collapse in the current DTLR finetuning setup.**

This remains true even after the zero-fuse engineering regression is fixed.

So the negative result is now attributable to the method direction itself, not to initialization contamination.

## Decision

Do not continue:

- `glyph_proto_fuse_coef = 0.02`
- `glyph_proto_fuse_coef = 0.1`
- rendered glyph bank on top of this same direct-fusion formulation

## Final Recommendation

Stop the current **prototype direct-fusion** line.

Do not continue this formulation as the next experiment path.
