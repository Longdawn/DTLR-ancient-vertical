# Vertical Ancient OCR Research Plan

## Current Best Result

Current best checkpoint:

```text
logs/mth1200pre_mth1000ft_full_0511-1717/checkpoint_best_regular.pth
```

Current best inference recipe:

```text
config/MTH1000_dtlr_msr_v2.py
nonblank_bias=0.2
ratio_nonblank_bias=0.2
ratio_min=1.5
ratio_max=2.0
```

Best strict test result:

```text
CER_micro = 5.90%
AR_macro = 89.63%
CR_macro = 89.92%
Exact match = 66.82%
```

Best conservative variant-normalized test result:

```text
CER_micro = 5.74%
AR_macro = 89.78%
CR_macro = 90.07%
Exact match = 67.63%
```

## Method Modules To Develop Later

These ideas should remain in the research plan, but are not the immediate next step.

### 1. Adaptive CTC Candidate Reranker

Generate multiple CTC candidates with different blank/nonblank calibration settings, then select the final sequence using image geometry, blank ratio, prediction length, and confidence statistics.

Target failure modes:

```text
short-column empty prediction
deletion-heavy predictions
sample-dependent best decoding bias
```

Paper framing:

```text
Geometry-aware CTC candidate reranking for vertical ancient text.
```

### 2. Short-Column Expert

Add a lightweight recognition branch for short vertical crops, especially likely one-character and two-character samples.

Target failure modes:

```text
len=1 / len=2 instability
blank collapse on short crops
single-character classification ambiguity
```

Paper framing:

```text
Short-column recognition expert for sparse vertical text.
```

### 3. Error-Guided Character Reweighting

Use validation/test diagnostic statistics to identify hard or rare characters. In training, oversample samples containing those characters or increase their loss weight.

Target failure modes:

```text
rare extended CJK characters
near-shape confusions
low-frequency character classes
```

Paper framing:

```text
Error-guided hard character reweighting.
```

### 4. Variant-Aware Auxiliary Supervision

Keep strict Unicode classification as the main task, but add an auxiliary group-level target for known variant families.

Example groups:

```text
真 / 眞
為 / 爲
敎 / 教
着 / 著
舎 / 舍
```

Target failure modes:

```text
variant-form instability
visually equivalent historical glyph forms
```

Paper framing:

```text
Variant-aware auxiliary supervision for historical Chinese glyphs.
```

## Pretraining Direction

The earlier stage-1 pretraining used only MTH1200:

```text
train lines = 35,965
batch size = 2
epochs = 13
iterations per epoch ~= 17,982
total iterations ~= 233,766
```

So the previous stage-1 was not obviously under-trained in iteration count. Its main limitation is data diversity: it used only one subset.

Available prepared datasets:

```text
MTH1000 train = 29,423 lines, avg len 11.06
MTH1200 train = 35,965 lines, avg len 7.53
TKH train     = 18,788 lines, avg len 13.77
Total train   = 84,176 lines
```

Recommended next pretraining experiment:

```text
Stage-1 mixed real-character-box pretraining on TKH + MTH1000 + MTH1200.
```

Reasoning:

```text
More diverse page sources.
More long vertical columns.
More character-form variation.
Still uses real character-level boxes, so it matches DTLR stage-1 detection supervision.
```

Proposed budget:

```text
batch size = 2
iterations per mixed epoch ~= 42,088
epochs = 6
total iterations ~= 252,528
```

This is close to the previous 233k run and close enough to the paper-scale first-stage budget, but with more diverse samples.

Expected time:

```text
~0.36-0.40 sec / iteration from the previous run
~4.2-4.7 hours / mixed epoch
~25-28 hours for 6 epochs on one 24GB GPU
```

If runtime is too long, run a pilot first:

```text
epochs = 2
total iterations ~= 84k
```

Then diagnose boxes before committing to the full run.

## Recommended Experimental Order

### Phase A: Mixed Stage-1 Pretraining

1. Build a mixed TKHMTH dataset wrapper or combined labels file.
2. Train stage-1 detection with real char boxes.
3. Run box diagnostics on MTH1000, MTH1200, and TKH validation splits.
4. Compare with the old MTH1200-only stage-1 checkpoint.

Decision rule:

```text
If mixed stage-1 produces tighter per-character boxes and fewer long-column boxes, keep it.
If not, do not spend more time on CTC finetuning from that checkpoint.
```

### Phase B: Finetuning And Transfer

Use the mixed stage-1 checkpoint for:

```text
MTH1000 finetune
MTH1200 finetune
TKH finetune
external vertical ancient datasets when available
```

Report both within-dataset and cross-dataset transfer.

### Phase C: Performance Modules

After the stronger pretraining baseline is established, add:

```text
adaptive candidate reranker
short-column expert
hard-character reweighting
variant-aware auxiliary supervision
```

This makes the final paper story cleaner:

```text
1. vertical character-box pretraining gives robust localization
2. vertical-aware finetuning gives recognition adaptation
3. adaptive decoding / short-column modules fix the remaining vertical-specific errors
```

