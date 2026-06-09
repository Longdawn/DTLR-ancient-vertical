# Cross-Section Consistency Review

Date: 2026-06-05

## Scope Consistency

Status: pass with guardrails.

The current draft consistently frames SAQT as a single-column / line-level recognition method for vertical ancient Chinese text. The newly added historical-document citations mention page-level reading order and character segmentation only as related background. The draft explicitly separates SAQT from those tasks in `02_related_work.md`: SAQT uses character boxes as structure-learning supervision and keeps the final system as line-level sequence recognition.

Scope guardrails for future revisions:

- Do not add page-level layout-analysis claims to the abstract or contributions.
- Do not describe SAQT as a full-page detector, column detector, reading-order predictor, or layout parser.
- When citing page-level Chinese historical document work, use it only to motivate spatial-structure difficulty, not to redefine the task.

## Claim Strength

Status: mostly controlled.

Acceptable bounded claims:

- SAQT reports higher AR/CR than the current adapted scene-text baselines under the paper's unified protocol.
- Query activation budget has MTHv2-only ablation evidence.
- Blank/nonblank calibration is a lightweight inference-time adjustment, not a language model.

Claims that must remain downgraded until new evidence exists:

- Structure-aware query learning as an independent contribution requires a no-structure-learning / CTC-only ablation.
- Query activation budget should not be described as cross-dataset validated until HDRC evidence exists.

Closed but scoped claim:

- Charset-aware classifier adaptation is supported by the HDRC random-head control. The claim should remain scoped to target-charset mismatch on HDRC, not generalized to all datasets.

## Evidence Consistency

Status: partial.

Paper-facing result numbers in the abstract, experiments, and readiness audit match `logs/paper_results_summary.md`:

- MTHv2 bias AR/CR: `96.69/96.90`
- HDRC bias AR/CR: `90.70/91.80`

Missing evidence remains unchanged:

- Gate C: structure-learning ablation.
- Gate F: head reconstruction vs full finetuning under final AR/CR protocol.

Newly closed evidence:

- Gate D: HDRC charset-adaptation ablation now compares random target classifier initialization against charset-aware initialization under matched full-model recognition training and validation-protocol test decoding.

## Citation Consistency

Status: partial pass.

Current inline citations now cover:

- Scene text recognition baselines and model families.
- DETR/DINO query-based detection background.
- Detection-based text line recognition / DTLR.
- CTC.
- Historical document analysis and Chinese historical document structure challenges.
- MTHv2/HRCenterNet and HDRC dataset/protocol sources.

Remaining citation work:

- Verify page ranges and metadata for the historical document citations.
- Keep `references_seed.bib`, `references.bib`, and `latex/references.bib` synchronized after any citation change.

## Current Review Verdict

The draft is internally more consistent than earlier versions and is closer to ICDAR/CCF-B writing expectations. It is still not regular-paper ready because the core structure-learning ablation is not closed. Further prose polishing should not replace Gate C evidence.
