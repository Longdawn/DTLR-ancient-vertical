# SAQT LNCS Draft

This directory contains an English LNCS-style submission skeleton converted from the Chinese paper draft.

## Files

- `main.tex`: entry point.
- `sections/*.tex`: section files.
- `references.bib`: local BibTeX copy synced from `../references.bib`.
- Figures are copied into `figures/*.pdf` so this directory can be uploaded as an Overleaf project root.

## Current Status

This is not yet a submission-ready paper. It is an Overleaf-ready skeleton for the current draft state.

Current paper-facing results are synchronized with the main draft:

- MTHv2 qbudget-count001: AR/CR `96.75/97.00` under the fixed development-set calibration protocol.
- HDRC qbudget-localization-query: AR/CR `93.44/94.36` under the fixed development-set calibration protocol.

Remaining before ICDAR / CCF-B regular-paper confidence:

- Keep HDRC qbudget-localization-query framed as variant-level evidence, not a pure query-budget ablation.
- Treat expected-count as an optional MTHv2-positive auxiliary term, not a universal module.
- Final BibTeX metadata verification in LNCS style.
- Final figure sizing against the LNCS template.

## Local Compile Note

Local compilation was not run because `pdflatex` is not installed in the current environment. On Overleaf, use Springer LNCS support with `llncs.cls` and compile `main.tex`.

Static checks on 2026-06-08:

- 19 citation keys are used and all are present in `references.bib`.
- No unused BibTeX entries remain.
- `figures/figure1_saqt_overview.pdf` is synchronized with the current overview figure.
- `figures/figure2_main_results.pdf` is synchronized with the current paper-facing result figure.
- The local and parent-directory Overleaf zip files have matching SHA-256 hashes.
