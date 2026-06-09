# Figure Audit for SAQT Draft

This audit tracks whether the current figures support the paper claims without adding unsupported visual implications.

## Figure 1: SAQT Overview

File:

- `figures/figure1_saqt_overview.svg`
- `figures/figure1_saqt_overview.pdf`
- Source script: `figures/plot_figure1_saqt_overview.py`
- Blueprint: `figures/figure1_saqt_overview_blueprint.md`

Verdict: usable for current draft; needs final typography/layout pass before submission.

Passed checks:

- Shows cropped vertical line / single-column input, not page-level layout analysis.
- Marks character boxes as training-only supervision.
- Shows structure learning through visual backbone, Transformer queries, class/box outputs, matching loss and query budget.
- Shows charset adaptation as classifier-row inheritance/initialization, not as an inference-time module.
- Shows CTC recognition and final text-string output.
- Explicitly states that character boxes are not used at inference.
- SVG text is editable through Matplotlib `svg.fonttype=none`.
- PDF export is available for LNCS/Overleaf integration.

Remaining issues:

- Final English caption should define `A_s` and `A_t` in text or figure note.
- Current figure does not explicitly show optional blank/nonblank calibration; this is acceptable because calibration is not positioned as the core module, but the caption should mention it only if space allows.
- Before LNCS submission, check width at single-column and double-column sizes and adjust font sizes if labels become too small.

## Figure 2: Main Result Comparison

File:

- `figures/figure2_main_results.svg`
- `figures/figure2_main_results.pdf`
- Source data: `figures/figure2_main_results_data.csv`
- Source script: `figures/plot_figure2_main_results.py`

Verdict: improved and usable for current draft; needs final caption wording after final results are frozen.

Passed checks:

- Uses only verified AR/CR values from the paper-facing results table.
- Compares SAQT against the best adapted STR baseline on each dataset.
- Shows both direct and validation-calibrated SAQT decoding.
- Uses a point comparison rather than non-zero-baseline bars, avoiding visual exaggeration from a truncated score range.
- SVG text remains editable; current SVG contains 40 text tags.
- Source CSV and plotting script are saved with the figure.
- PDF export is available for LNCS/Overleaf integration.

Remaining issues:

- Caption should state that `Best adapted STR` is SVTR-tiny on MTHv2 and CRNN on HDRC.
- Gate D now appears as a table rather than Figure 2. If final Gate C results are added, consider a compact ablation table before adding a new figure.
- Final LNCS integration should confirm that the legend remains readable after scaling.
