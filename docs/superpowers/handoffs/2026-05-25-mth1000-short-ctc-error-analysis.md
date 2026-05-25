# MTH1000 Short CTC Error Analysis

Date: 2026-05-25

## Scope

This note freezes a read-only analysis of the MTH1000 short-text CTC failure mode in the current DTLR ancient vertical pipeline.

Inputs inspected:

- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/ctc_error_summary_valid.json`
- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/ctc_error_cases_valid_allcases.jsonl`
- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/ctc_error_summary_valid_bias_b-03_nb03.json`
- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/ctc_error_cases_valid_bias_b-03_nb03.jsonl`
- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/short_blank_margin_len2_valid.json`
- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/short_blank_margin_len2_cases_valid.jsonl`
- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/decode_bias_sweep_short_valid.json`
- `logs/mth1000_realmain_shortboost_presence_0524-2307/ctc_error_summary_valid.json`
- `logs/mth1000_realmain_shortboost_presence_0524-2307/ctc_error_cases_valid.jsonl`
- `logs/paper_experiment_mainline_compare_0525.md`
- decode/evaluation code under `util/ctc_decoding.py`, `tools/analyze_ctc_errors.py`, `tools/evaluate_short_rescue.py`, and `tools/analyze_short_blank_margin.py`

No code, config, model, dataset, checkpoint, or log file was modified for this analysis.

## 1. Core Conclusion

The short-text problem is mainly an under-decoding problem, not an over-decoding problem.

- `len=1` fails mostly by predicting blank and collapsing to the empty string.
- `len=2` fails mostly by predicting only one character, or by predicting one character and getting it wrong.
- Pure insertion is rare in both buckets.

This is why decode-time blank suppression on a fixed checkpoint can outperform shortboost training changes:

- it directly corrects the dominant blank-vs-nonblank calibration issue
- it improves borderline short-text cases with small global side effects
- shortboost reduces some empty cases, but introduces more instability in substitutions and long-text behavior

## 2. len=1 / len=2 Error Type Statistics

Derived from baseline all-cases JSON:

- source: `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/ctc_error_cases_valid_allcases.jsonl`

### len=1

- total samples: `827`
- total errors: `240`
- CER: `0.29020556227327693`
- empty prediction rate: `0.22974607013301088`

Error breakdown:

- `190` empty-string deletions
- `48` single-character substitutions
- `2` single-character over-decodes / insertions

Interpretation:

- about `79.2%` of `len=1` errors are empty predictions
- substitution exists, but it is secondary to blank collapse

### len=2

- total samples: `628`
- total errors: `290`
- CER: `0.28264331210191085`
- empty prediction rate: `0.044585987261146494`

Error breakdown:

- `137` drop-one-character cases
- `88` one-correct-one-wrong substitutions
- `28` empty-string predictions
- `21` deletion-plus-substitution cases
- `11` two-substitution cases
- `5` over-decodes / repeat-like cases

Interpretation:

- the dominant `len=2` failure is not full blank collapse
- the model often preserves only one character query
- a second common mode is keeping two positions but confusing one of them

### Short-Margin Diagnostic

From `short_blank_margin_len2_valid.json` on the baseline checkpoint:

- all short samples (`len<=2`):
  - `samples = 1455`
  - `empty_pred_rate = 0.14982817869415807`
  - `error_rate = 0.3642611683848797`
- empty cases:
  - `samples = 218`
  - `blank_beats_top_nonblank_rate = 1.0`
  - `avg_top1_margin_blank_minus_nonblank = 0.520930788043989`
- by exact length:
  - `len=1`: `empty_pred_rate = 0.22974607013301088`
  - `len=2`: `empty_pred_rate = 0.044585987261146494`

Interpretation:

- when the model outputs empty on short text, blank almost always beats the best nonblank candidate
- `len=1` is a stronger blank-collapse regime than `len=2`
- `len=2` has many nonempty errors, so internal nonblank ranking also matters there

## 3. Baseline vs Decode Bias vs Shortboost

### Key Metric Table

| Run | CTC summary CER | Empty rate | len=1 CER | len=1 empty | len=2 CER | len=2 empty | len>=11 CER |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline `mth1000mth1200pre_mth1000ft_full_0513-2257` | `0.0784` | `0.0486` | `0.2902` | `0.2297` | `0.2826` | `0.0446` | `0.0583` |
| fixed decode bias `blank=-0.3, nonblank=+0.3` | `0.0749` | `0.0432` | `0.2757` | `0.2031` | `0.2707` | `0.0414` | `0.0556` |
| shortboost presence `mth1000_realmain_shortboost_presence_0524-2307` | `0.0796` | `0.0417` | `0.2769` | `0.2007` | `0.2795` | `0.0303` | `0.0594` |

### Immediate Takeaways

- decode-time bias is best on overall fixed-valid CER
- decode-time bias improves both short buckets and long-text CER
- shortboost improves some short empty-rate metrics, but loses on overall fixed-valid CER and on `len>=11`

### Case-Level Transition Summary

Comparing baseline all-cases against decode-bias all-cases:

- `len=1`: `12` improved, `0` regressed, `815` unchanged
- `len=2`: `15` improved, `0` regressed, `613` unchanged

Typical improvements:

- `四: "" -> "四"`
- `形: "" -> "形"`
- `懈怠: "" -> "怠"`

Comparing baseline all-cases against shortboost:

- `len=1`: `26` improved, `15` regressed, `786` unchanged
- `len=2`: `33` improved, `30` regressed, `565` unchanged

Typical shortboost regressions from previously correct baseline outputs:

- `遏: "遏" -> ""`
- `擊: "擊" -> ""`
- `周帀: "周帀" -> "周"`

Interpretation:

- decode bias acts like a low-risk calibration correction
- shortboost trades some gains for noticeable new regressions

## 4. Why Decode-Time Bias Is More Stable Than Shortboost

### 4.1 The dominant baseline pathology is blank overconfidence

`util/ctc_decoding.py` applies decode-time calibration by shifting blank and nonblank log-probabilities before greedy decode.

That directly targets the observed failure mode:

- baseline short empties are common
- short empty cases show blank beating top nonblank with large positive margin
- deletion and low predicted-length ratio dominate the short buckets

### 4.2 Greedy CTC collapse amplifies blank wins on short samples

`decode_greedy()` in `util/ctc_decoding.py` does:

- per-step argmax
- CTC collapse
- blank removal

For `len=1`, a small blank advantage often becomes a final empty string after collapse.
For `len=2`, the same bias often becomes a one-character output.

### 4.3 Decode bias changes the decision boundary without retraining the representation

The fixed-bias variant raises:

- `pred_gt_len_ratio`: `0.9636 -> 0.9708`
- lowers `del_rate`: `0.0387 -> 0.0320`
- lowers `empty_pred_rate`: `0.0486 -> 0.0432`

This matches a calibration fix:

- more characters survive decode
- fewer short samples collapse away
- already-correct long samples are mostly preserved

### 4.4 Shortboost changes training distribution, not just decode calibration

`config/MTH1000_dtlr_shortboost_presence_v1.py` inherits from `config/MTH1000_dtlr_shortboost_v2.py` and adds:

- length-balanced sampling
- train-only length-aware MSR policy from the shortboost chain
- `short_gt_presence_loss_coef = 0.02` for `len<=2`

Relevant training-side behavior:

- `finetuning.py` uses `WeightedRandomSampler` for short buckets
- `models/dino/dino.py` presence loss encourages each short GT character to beat blank for at least one query

This can reduce some short blank failures, but it does not directly solve global decode calibration. The observed result is:

- fewer empty predictions in some short buckets
- but more substitution and long-text tradeoff
- more cases where previously-correct baseline predictions regress

### 4.5 Practical summary

Decode-time bias is more stable because it is:

- closer to the measured failure mode
- cheaper than retraining
- easier to sweep and verify
- lower risk for long-text regression

Shortboost is less stable because it bundles:

- sampler changes
- resize-policy changes
- auxiliary short loss

Those interact with representation learning and can shift the whole error surface, not only the blank threshold.

## 5. Next 3 Experiment Options

1. **Margin-gated blank suppression**
   - only apply blank/nonblank bias when blank beats top nonblank by a small margin
   - aim: rescue borderline short cases without globally increasing nonblank outputs

2. **Conditional short rescue**
   - trigger only when greedy decode gives:
     - empty output, or
     - output shorter than expected short length regime
   - reuse top nonblank candidates from `tools/evaluate_short_rescue.py`
   - keep the policy restricted to short columns / ratio-qualified cases

3. **Training ablation under fixed decode-bias evaluation**
   - if training-side work resumes later, separate:
     - sampler-only
     - sampler + MSR
     - sampler + presence loss
   - evaluate every run under the same decode-bias protocol
   - goal: stop conflating training changes with decode calibration effects

## 6. What Can Be Used In Paper Motivation / Error Analysis

These points are defensible for a paper motivation or error-analysis section:

- The hardest short-text regime is not generic OCR confusion, but CTC under-decoding.
- For `len=1`, the dominant failure is blank collapse to empty.
- For `len=2`, the dominant failure is missing one character rather than fully blanking both.
- Short-text failures are deletion-heavy, while insertion-heavy behavior is rare.
- Decode-time calibration can outperform short-sample training heuristics because it directly addresses blank-vs-nonblank decision bias.
- Training-side short-text interventions can reduce some empties but may introduce new substitution and long-text regressions.

These paper-facing claims should be kept qualified:

- avoid claiming decode bias is a final method result unless it is rerun under the exact intended paper protocol
- avoid claiming shortboost is harmful in general; the evidence here is specifically for the current MTH1000 fixed-valid evaluation setup

## Bottom Line

For the current repository state, the short-text problem is best framed as:

- `len=1`: blank-collapse / empty prediction problem
- `len=2`: one-character retention plus confusion problem

This framing explains why fixed decode-time bias already beats the current shortboost mainline on fixed-valid CER and why future work should separate decode calibration from training-side short-sample interventions.
