# CCF-B Submission Risk Matrix

Date: 2026-06-08

This note answers a narrow question: given the current DTLR code, experiment
artifacts, and paper draft, what is strong enough for a CCF-B submission, what
is still risky, and which model changes are still worth testing?

## Bottom Line

SAQT is currently a plausible CCF-B submission candidate if framed as a
conservative method paper for vertical ancient single-column recognition. The
submission should not claim SOTA, universal robustness, or a broadly validated
architecture family. The current strongest contribution is not a backbone swap;
it is the conversion of localization-supervised detection-style queries into a
line-level CTC recognizer with charset-aware classifier adaptation.

The paper-facing model should be:

1. character-localization information learning for detection-style queries;
2. vertical sorting and query-to-CTC conversion;
3. charset-aware classifier adaptation;
4. classifier-head reconstruction followed by full-model recognition training;
5. optional MTHv2-positive expected-count auxiliary regularization;
6. fixed development-set blank/nonblank calibration as protocol, not as model
   novelty.

## Evidence Strength by Claim

| Claim | Current evidence | Strength | Paper handling |
| --- | --- | --- | --- |
| SAQT is competitive with adapted STR baselines on MTHv2 and HDRC | MTHv2 qbudget-count001 AR/CR `96.75/97.00`; HDRC qbudget-localization-query AR/CR `93.44/94.36`; CRNN/SVTR/ABINet/SAR baselines in `logs/paper_results_summary.md` | strong within current protocol | Main result, but avoid SOTA wording. |
| Character-localization learning is important for query-to-CTC | MTHv2 no-localization CTC collapses to `0.11/0.16` AR/CR after calibration | medium | Use as lower-bound control, not pure causal estimate. |
| Query activation budget helps | MTHv2 single-factor improvement `96.10/96.37 -> 96.69/96.90`; HDRC qbudget-localization-query variant reaches `93.44/94.36` | medium | MTHv2 ablation plus HDRC variant evidence. Do not call HDRC a single-factor ablation. |
| Charset-aware classifier adaptation helps target charset mismatch | HDRC random-head `82.72/83.97` vs charset-aware `90.70/91.80` | strong for HDRC | Present as target-domain evidence. |
| Full-model recognition training is needed after head reconstruction | MTHv2 `93.83/95.03 -> 96.69/96.90`; HDRC `85.97/89.72 -> 90.70/91.80` | strong for current datasets | Keep as pipeline evidence. |
| Expected-count auxiliary is useful | MTHv2 qbudget clean `96.17/96.29 -> 96.33/96.50`, calibrated `96.69/96.90 -> 96.75/97.00`; HDRC count001 regressed | weak-to-medium | Optional MTHv2 ablation only. |
| Decode calibration solves under-decoding | Improves main branches, selected on validation and fixed on test | medium | Experimental protocol, not a method contribution. |

## Reviewer Risk Matrix

| Reviewer concern | Risk level | Why it matters | Mitigation in current draft |
| --- | --- | --- | --- |
| "This is just DTLR applied to ancient text." | high | DTLR already supplies query-based localization. | Emphasize query-to-CTC conversion, charset-aware adaptation, vertical single-column protocol, and ancient-text charset/domain shift. |
| "The gains may come from calibration." | medium | Blank/nonblank bias improves results. | Always report direct and calibrated results; state calibration is fixed from validation and uses no LM or external text. |
| "The HDRC qbudget result is not a pure ablation." | medium | It includes localization-query differences. | Label it qbudget-localization-query variant, not single-factor query-budget proof. |
| "Only two main datasets are used." | medium | MTHv2 and HDRC are enough for a focused paper, but not broad robustness. | Keep claims dataset-scoped; mention CHDAC as not paper-ready internal evidence if needed, not in main claims. |
| "No random-seed variance." | medium | Single-run evidence limits statistical claims. | Avoid "significant", "stable", "robust", and "generalizes". |
| "No-localization control is too weak." | medium | Collapse is informative but not a strong tuned baseline. | Call it a conservative lower-bound control. |
| "Expected-count is not cross-dataset positive." | low if written carefully | HDRC failed. | Keep it optional and MTHv2-specific. |
| "Baselines are adapted scene-text models, not historical OCR specialists." | medium | Reviewers may ask for domain baselines. | Explain unified recognition-only protocol; add any available historical OCR citation/baseline only if reproducible. |

## Experiments Worth Running Next

| Priority | Experiment | Why | Minimum keep criterion | Current status |
| --- | --- | --- | --- | --- |
| 1 | MTHv2 length-balanced sampling probe | Tests short-column failure without changing model architecture. | Valid CER better than `logs/mthv2_base_resume_1000_0607` (`0.118792`) and no clear long-column regression. | Technically ready; smoke verified; real tmux launch blocked by execution environment. |
| 2 | HDRC no-localization control | Strengthens structure-learning evidence across datasets. | Does not need to be good; should show whether localization-supervised queries are also necessary on HDRC. | Not run. Expensive and lower priority than submission QA. |
| 3 | Weaker expected-count coefficient on HDRC | Tests whether expected-count can become safer cross-dataset regularization. | Preserve MTHv2 gain and avoid HDRC count collapse. | Optional; do only one coefficient such as `0.003`, not a sweep. |
| 4 | Rare-character or warmup-only glyph prototype auxiliary | Closest to discriminative character modeling. | Must beat base for 1000 and 2000 steps without regressing when combined or extended. | Current evidence unstable; do not include yet. |

## Architecture or Module Changes to Avoid

| Candidate | Current evidence or reason | Decision |
| --- | --- | --- |
| Generic backbone replacement | Expensive and weakly tied to SAQT's novelty. | Avoid for this paper. |
| SQR / sorted query sequence refiner | Valid CER `0.1465` / `0.1427`, worse than matched base `0.1188`. | Stop. |
| DCTC-lite / Viterbi alignment regularization | Valid CER `0.1202`, worse than base and computationally awkward. | Stop. |
| Blank probability cap | Valid CER `0.1226`, worse than base. | Stop. |
| MSR-v2 resize policy | Valid CER `0.1304`, worse than base. | Stop. |
| First LGQ activation-gated query-to-CTC adapter | Smoke valid CER `14.8588%`, worse than head-only starting point. | Stop this setting; redesign only if there is a specific mechanism change. |
| Decode adaptive pred-short | Tiny MTHv2 gain, slight HDRC validation regression. | Keep internal. |

## Minimum Path to Submission

The fastest credible submission path is not another architecture branch. It is:

1. keep the current SAQT method story and claim strength;
2. finish reference metadata verification;
3. run LaTeX/figure QA;
4. ensure all main tables use MTHv2 qbudget-count001 and HDRC qbudget-localization-query as current paper-facing results;
5. optionally run length-balanced sampling only if tmux execution becomes
   available.

If one more positive experiment is needed for confidence, run length-balanced
sampling first. If it fails, the paper can still proceed as a conservative
method paper; do not replace it with a generic network change.
