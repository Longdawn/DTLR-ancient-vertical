# SGQ Module Roadmap

Date: 2026-05-28

## Context

Current MTH1000 short-text analysis shows that blank/nonblank calibration has already reduced a large part of empty prediction and deletion errors. After calibration with `blank_bias=-1.2` and `nonblank_bias=+1.0`, the remaining short-text bottleneck shifts toward character classification errors:

- `len=1`: empty errors decrease, but wrong-character errors become more prominent.
- `len=2`: short-output errors decrease, but one-correct-one-wrong substitutions become more prominent.

The next method module should therefore focus on short-text glyph discrimination instead of global count control or direct prototype-logit fusion.

## Tentative Module Name

**SGQ: Short Glyph-aware Query Module**

Chinese name: **短文本字形感知查询模块**

SGQ is intended as an add-on module for the current VQ-CTC direction:

```text
VQ-CTC =
  Vertical Query CTC Recognition
  + Blank-aware CTC Calibration
  + Short Glyph-aware Query Supervision
```

Calibration handles `empty/deletion/under-decoding`; SGQ should handle `wrong_char/substitution` on short samples.

## Planned Changes

| Submodule | Target problem | Core idea | Reference direction | Code area | Stage | Risk | Validation metrics |
|---|---|---|---|---|---|---|---|
| Short Query Selector | Unclear query-to-character assignment for `len=1/2` | Select top nonblank or CTC-aligned query as short-text supervision target | SegCTC; PR 2024 segmentation+recognition | `models/dino/dino.py`, criterion | Stage 1 | Wrong query selection adds noisy labels | selector hit rate, len=1/2 CER |
| Short Query CE Loss | `len=1 wrong_char`, `len=2 one-correct-one-wrong` | Add auxiliary CE on selected short-text queries | explicit segmentation supervision | `SetCriterion` loss path | Stage 1 | May overfit short samples or hurt long text | len=1 CER, len=2 CER, sub rate |
| Short-only Loss Weighting | Short samples are underrepresented | Apply auxiliary loss only or mainly to `gt_len<=2` or `gt_len<=5` | short-text focused training | config + criterion | Stage 1 | Too much weight can regress long text | len buckets, len>=11 CER |
| Blank-aware Calibration | empty/deletion/under-decoding | Decode-time blank/nonblank prior calibration | CTC calibration | `util/ctc_decoding.py`, eval tools | Existing | sub/ins increase | CER, AR, CR, empty, del/sub/ins |
| Glyph Auxiliary Head | shape-similar and low-frequency confusion | Project query feature into glyph-aware space; auxiliary loss only | Image-IDS Aligning, Glyce, RAN | `models/dino/dino.py` | Stage 2 | Weak or noisy supervision may not help | sub rate, shape-similar subset |
| IDS/Radical Multi-label Loss | glyph structure discrimination | Predict IDS/radical tags for selected query features | RAN, IDS aligning | glyph metadata + loss | Stage 2 | Requires reliable IDS/radical table | shape-similar CER, low-freq CER |
| Exemplar Short Rerank | short-text wrong-character correction | Rerank short-text candidates by glyph/exemplar similarity | AAAI 2025 exemplar CTR | separate eval/rerank tool | Stage 3 | More engineering and may remain post-processing | len=1/2 CER, wrong_char repair rate |
| Shape-similar Eval Subset | prove glyph module effect | Build low-frequency and shape-similar subsets | glyph-aware CTR analysis | `tools/` analysis script | Stage 2 prerequisite | subset definition must be defensible | subset CER, subset sub rate |

## Stage 1 Scope

Only implement the minimum credible SGQ module:

1. Short Query Selector
2. Short Query CE Loss
3. Short-only Loss Weighting

Stage 1 should not include:

- direct prototype logits fused into CTC
- global count consistency
- rendered glyph bank
- IDS/radical supervision
- exemplar retrieval or reranking

## Stage 1 Data Flow

```text
decoder query features + CTC logits + GT transcript
  -> select short-text character-bearing query or queries
  -> apply auxiliary CE on selected query logits/features
  -> add SGQ loss during training only

inference:
  unchanged CTC decoding
  + blank-aware calibration
```

The first version should not directly modify inference logits. This is important because direct prototype-logit fusion previously caused blank collapse.

## Initial Experiment Matrix

| Experiment | Description |
|---|---|
| clean baseline | original model, no calibration |
| calibrated baseline | current `blank=-1.2`, `nonblank=+1.0` |
| SGQ CE only | train with short query CE, infer without calibration |
| SGQ CE + calibration | train with SGQ, infer with calibration |
| SGQ `len<=1` / `len<=2` / `len<=5` | compare target scope |
| SGQ loss weight sweep | conservative weights such as `0.05`, `0.1`, `0.2` |

## Success Criteria

A useful SGQ run should satisfy most of the following:

- `len=1 CER` decreases.
- `len=2 CER` decreases.
- `sub_rate` decreases or at least does not increase sharply.
- `empty_rate` and `del_rate` do not regress after calibration.
- `len>=11 CER` does not regress meaningfully.
- calibrated overall CER improves over the current calibrated baseline:
  - valid calibrated baseline: `0.069783`
  - test calibrated baseline: `0.048828`

## Negative Signals

Stop or redesign if any of these happen:

- `blank_pred_ratio` increases sharply.
- `len>=11 CER` regresses while short buckets only improve marginally.
- `sub_rate` rises more than the short-text gain justifies.
- selected query supervision is unstable or mostly targets the wrong query.
- SGQ only helps clean decoding but loses the gain after blank-aware calibration.

## Current Recommendation

The next implementation should start with **Short Query CE Loss** rather than glyph prototype or IDS. It is the smallest module that directly attacks the current post-calibration failure mode:

```text
len=1 wrong_char
len=2 one-correct-one-wrong
```

If Stage 1 improves short-text substitution without hurting long text, Stage 2 can add glyph/radical supervision to make the module more structurally meaningful.
