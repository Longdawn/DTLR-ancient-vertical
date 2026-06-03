# Query Activation Budget Experiment Design

Date: 2026-06-02

## Objective

Test whether a small query-activation budget regularizer can stabilize DTLR stage-1 localization pretraining when adding TKH-style long-column data, without replacing the verified MTH1000+MTH1200 mainline.

This experiment is motivated by the current full-MTHv2 negative signal:

- Trusted MTH1000+MTH1200 stage-1 on MTH1000 valid:
  - `debug_vis/mth1000_mth1200_stage1_on_mth1000_valid_0513`
  - avg predicted nonblank count: `40.79`
  - avg GT length: `7.49`
- Full-MTHv2 stage-1 on MTH1000 valid:
  - `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601`
  - avg predicted nonblank count: `142.6`
  - avg GT length: `7.49`
- Downstream head reconstruction:
  - old MTHv2 head baseline epoch-2 CER: `0.14526833428705468`
  - full-MTHv2 stage-1 head epoch-2 CER: `0.15283326830434354`
- Downstream full finetune:
  - old MTHv2 full baseline best valid CER: `0.11397798822246911`
  - full-MTHv2 stage-1 full finetune best valid CER so far: `0.13439168210258723`

The working hypothesis is that directly adding TKH to stage-1 changes the query activation distribution. TKH is mostly long-column, low-character-set, low-short-text-risk data. It may encourage many nonblank queries, which then harms downstream CTC adaptation.

## Non-Goals

- Do not replace the trusted mainline result with full-MTHv2 pretraining unless it beats the old baseline after clean and calibrated evaluation.
- Do not frame this as page-level layout analysis or reading-order prediction.
- Do not add a generic plug-and-play attention, Mamba, or frequency module unless this query-budget experiment fails and the next design explicitly justifies the change.
- Do not judge success from stage-1 training loss alone.

## Proposed Module

Add an optional stage-1 regularizer that penalizes excessive nonblank query activation.

The model already produces per-query class logits during stage-1 detection/localization pretraining. For each sample:

1. Convert class logits to a soft nonblank probability per query.
2. Sum nonblank probabilities across queries to estimate expected active query count.
3. Compare the expected active count against a target budget derived from GT text length.
4. Penalize only over-activation by default, so the model is not forced to hallucinate nonblank queries for ambiguous or damaged samples.

Suggested formula:

```text
p_nonblank[q] = 1 - p_blank[q]
expected_count = sum_q p_nonblank[q]
target_count = budget_scale * gt_len + budget_margin
loss_query_budget = mean(relu(expected_count - target_count)^2 / max(gt_len, 1))
```

Recommended initial defaults:

- `use_query_budget_loss=False`
- `query_budget_loss_coef=0.01`
- `query_budget_scale=2.0`
- `query_budget_margin=8.0`
- `query_budget_short_weight=1.0`
- `query_budget_long_weight=1.0`

Rationale:

- With MTH1000 valid avg GT length `7.49`, `2.0 * len + 8` gives a typical budget around `23`, still below the old diagnostic count `40.79`.
- The coefficient should start small because the stage-1 detector already has CE, bbox, and GIoU losses.
- The first goal is to reduce the pathological `142.6` active-query behavior, not to match GT length exactly.

## Insertion Point

Implement inside the stage-1 criterion path in `models/dino/dino.py`, near existing optional query activation / count utilities if present.

The module should be config-gated:

- Existing configs must behave identically by default.
- New experiment configs should be added instead of editing trusted baseline configs.
- A unit test should verify that default loss dictionaries are unchanged when disabled and that the budget loss is positive when expected active count exceeds target.

## Experiment Plan

### Phase 0: Verification-Only Baseline

Before training, preserve the current negative evidence:

- Full-MTHv2 stage-1 diagnostic:
  - `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601/summary.json`
- Trusted stage-1 diagnostic:
  - `debug_vis/mth1000_mth1200_stage1_on_mth1000_valid_0513/summary.json`
- Old MTHv2 head/full baselines:
  - `logs/mthv2_mth1000mth1200tkh_head_0528-0003`
  - `logs/mthv2_mth1000mth1200tkh_full_0528-0957`

### Phase 1: Unit And Smoke

Add tests for:

- Budget loss is disabled by default.
- Over-budget predictions produce positive loss.
- Under-budget predictions produce zero or near-zero loss.
- Loss remains finite for empty or very short targets.

Run a debug smoke with `main_synthetic.py --debug` and verify:

- Detection losses still appear: `loss_ce`, `loss_bbox`, `loss_giou`.
- New metric appears only when enabled: `loss_query_budget`.
- No `loss_CTC` appears in stage-1 smoke.

### Phase 2: Short Stage-1 Continue-Pretrain

Do not start from scratch. Start from the trusted real stage-1 checkpoint:

```text
logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth
```

Run a short continue-pretrain on MTH1000+MTH1200+downsampled TKH, or full MTHv2 with a short budget if downsampling is not yet implemented.

Preferred data strategy:

- Keep all MTH1000 and MTH1200.
- Add TKH at a low sampling ratio or low epoch exposure.
- If dataset-level sampling is too invasive, create an experiment config that uses only MTH1000+MTH1200 first, then test query budget in a controlled setting before mixing TKH.

Training must run in `tmux`.

### Phase 3: Box Diagnostic Gate

Run MTH1000 valid box diagnostics before any head reconstruction.

Continue only if:

- The diagnostic is at least competitive with the trusted MTH1000+MTH1200 baseline.
- `avg_pred_nonblank_count` is not merely lower than `142.6`; it should be near or better than the old baseline range around `40.79`.
- A practical target band is `35-55`, with the final decision made from both the number and visual samples.
- Visual samples do not show obvious blank collapse or missing character regions.

Stop if:

- The model remains near `60+` predicted nonblank count without clearly better visual alignment than the trusted baseline.
- The model collapses to too few nonblank queries.
- Box alignment visually degrades compared with the trusted baseline.

### Phase 4: Head Reconstruction Gate

Only after a good box diagnostic, run MTHv2 head reconstruction.

Continue only if epoch-2 head CER beats the old head baseline:

```text
old baseline epoch-2: 0.14526833428705468
failed full-MTHv2 epoch-2: 0.15283326830434354
required target: < 0.14526833428705468
```

Stop if head CER does not beat the old MTH1000+MTH1200-pretrained head baseline.

### Phase 5: Full Finetune And Reporting

Only if head reconstruction passes, run full finetune and report:

- valid best CER
- clean valid/test CER, AR, CR
- validation-selected decode-bias sweep
- calibrated test CER, AR, CR
- empty prediction rate
- pred/GT length ratio
- length buckets:
  - `len=1`
  - `len=2`
  - `len=3-5`
  - `len=6-10`
  - `len>=11`

Compare against:

- `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- MMOCR MTHv2-combo baselines in `logs/paper_results_summary.md`

## Success Criteria

Count as useful only if all are true:

- MTH1000 valid box diagnostic is better than the trusted MTH1000+MTH1200 stage-1 baseline, not just better than the failed full-MTHv2 stage-1.
- MTHv2 head reconstruction beats the old MTH1000+MTH1200-pretrained head baseline.
- Full finetune clean or calibrated CER improves over the old MTHv2 full baseline.
- Short-text buckets do not regress in a way that undercuts the overall gain.
- Final reporting includes CER/AR/CR and length buckets.

Count as weakly useful if:

- Box diagnostic improves over failed full-MTHv2 but does not beat the trusted baseline.
- The result provides a clear negative/ablation story about controlling query activation, but should not be used as a paper main result.

Count as harmful if:

- Box diagnostic improves numerically but downstream CER regresses.
- Short-text buckets regress while overall CER only moves marginally.
- The module makes training fragile or requires extensive hyperparameter search.

## Paper Framing

If successful, frame this as:

```text
Directly scaling structure-aware pretraining to heterogeneous long-column data can over-activate localization queries. We therefore introduce a length-aware query activation budget that constrains the expected number of nonblank queries during localization pretraining.
```

If unsuccessful, still useful as an ablation:

```text
Full-MTHv2 pretraining and explicit query-count regularization were tested but did not outperform the trusted MTH1000+MTH1200 pretraining baseline, suggesting that data quality and activation calibration matter more than raw pretraining scale.
```

## Open Decisions

- Whether to implement TKH downsampling in the dataset builder or use separate short continue-pretrain configs.
- Whether the first implementation should reuse the existing query activation head or compute nonblank probability directly from class logits.
- Whether to penalize over-activation only, or also penalize under-activation with a much smaller coefficient.

Recommended first choice:

- Use class logits directly.
- Penalize over-activation only.
- Validate on MTH1000 valid box diagnostic before any downstream CTC training.
