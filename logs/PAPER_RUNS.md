# Paper-Ready Run Manifest

This file separates paper-facing SAQT evidence from exploratory or failed runs.
Historical log directory names are kept unchanged so result tables and
checkpoints remain reproducible.

## Primary Results

| Role | Dataset | Log dir | Checkpoint | Notes |
| --- | --- | --- | --- | --- |
| Main MTHv2 result | MTHv2-combo | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608` | `checkpoint_best_regular.pth` | Query-budget branch with expected-count auxiliary loss. |
| Original MTHv2 qbudget result | MTHv2-combo | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603` | `checkpoint_best_regular.pth` | Strong baseline without expected-count auxiliary loss. |
| Main HDRC result | HDRC | `logs/hdrc_qbudget_full_0607` | `checkpoint_best_regular.pth` | qbudget-localization-query variant used for current strongest HDRC result. |
| HDRC charset-aware mainline | HDRC | `logs/mth1000mth1200pre_hdrcft_full_0527-1732` | `checkpoint_best_regular.pth` | Used for charset adaptation comparison. |
| HDRC random-head control | HDRC | `logs/hdrc_charset_random_full_visible1_0605` | `checkpoint_best_regular.pth` | Random target classifier control. |

## Ablation Evidence

| Ablation | Dataset | Positive / Reference Run | Control Run | Handling |
| --- | --- | --- | --- | --- |
| Query activation budget | MTHv2-combo | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603` | `logs/mthv2_mth1000mth1200tkh_full_0528-0957` | Main single-factor MTHv2 ablation. |
| Expected-count auxiliary loss | MTHv2-combo | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608` | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603` | Small but consistent MTHv2 gain; optional module. |
| Charset-aware classifier adaptation | HDRC | `logs/mth1000mth1200pre_hdrcft_full_0527-1732` | `logs/hdrc_charset_random_full_visible1_0605` | Target-domain evidence for charset-aware initialization. |
| Head reconstruction vs full recognition training | MTHv2/HDRC | Full recognition checkpoints listed above | Head-only checkpoints in `logs/mthv2_qbudgetstage1pre_mthv2_head_0603` and `logs/mth1000mth1200pre_hdrcft_head_0527-1530` | Shows classifier-only adaptation is insufficient. |

## External Baselines

MMOCR and PaddleOCR baseline outputs are summarized in `logs/paper_results_summary.md`.
Keep their original external work directories in the result table for auditability.

## Archive Policy

- Do not delete or rename historical log directories that appear in `logs/paper_results_summary.md`.
- Exploratory logs may remain under `logs/` but should not be cited unless they have CER/AR/CR and length-bucket metrics.
- Failed or diagnostic runs should be described as such in notes rather than removed silently.
- If disk cleanup is required, first create a deletion manifest listing exact paths, sizes, and whether each path is referenced by a paper table.
