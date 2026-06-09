# SAQT Project Map

Concise map of the SAQT vertical ancient Chinese text recognition repository.

## Core Entry Points

- `main_synthetic.py` - character-localization / structure-query pretraining.
- `finetuning.py` - CTC classifier-head reconstruction and full recognition finetuning.
- `evaluation.py` - standalone evaluation entry point.
- `engine.py` - shared train/eval loops.

## Paper-Facing Model And Configs

- `models/saqt/` - SAQT registration layer and public model entry point.
- `models/dino/` - compatibility implementation layer for existing query-transformer code and checkpoints.
- `config/SAQT_MTHV2.py` - MTHv2 paper-facing recognition config.
- `config/SAQT_HDRC.py` - HDRC paper-facing recognition config.
- `config/MTHV2_stage1_query_budget.py` - query-budget localization pretraining config.

Legacy `*_dtlr.py` config names remain available for historical reproducibility. New paper-facing documentation should use the SAQT config names unless it is describing an old run exactly.

## Important Evaluation And Analysis Tools

- `tools/diagnose_boxes.py` - stage-1 query/box diagnostic with visualizations.
- `tools/analyze_ctc_errors.py` - CTC CER, AR, CR, length buckets, empty prediction analysis.
- `tools/sweep_ctc_decode_bias.py` - development-set CTC decode calibration sweeps.
- `tools/eval_ctc_micro_batch.py` - batch valid/test micro CER/AR/CR evaluator.
- `tools/eval_mmocr_textrecog_predictions.py` - convert/evaluate MMOCR text-recognition outputs.
- `tools/format_ctc_result_row.py` - format result JSON files for paper tables.

## Data Preparation Tools

- `tools/prepare_tkhmth2200_single_column.py` - build processed TKH/MTH vertical-line data.
- `tools/prepare_hdrc_dtlr.py` - build processed HDRC line-level data.
- `tools/export_mmocr_recog_dataset.py` - export processed datasets for MMOCR recognition baselines.
- `tools/generate_vertical_ancient_synth.py` - synthetic vertical ancient text generation.

## Dataset Code

- `datasets/MTH1000.py` - MTH1000-style processed single-column dataset loader.
- `datasets/MTHCombo.py` - combined MTH1000/MTH1200/TKH dataset loader.
- `datasets/synthetic_lines_general.py` - synthetic vertical line dataset support.

## Utility Code

- `util/ctc_decoding.py` - CTC greedy decoding and fixed decode calibration.
- `util/ctc_metrics.py` - edit-distance metrics and length-bucket summaries.
- `util/slconfig.py` - config loading.
- `util/misc.py` - distributed/runtime helpers.

The broader `util/` directory still contains compatibility utilities inherited from the upstream codebase. Do not remove it wholesale; several current entry points import from it.

## Data Locations

- `data/tkhmth2200_mth1000_dtlr/` - processed MTH1000 vertical-line data.
- `data/tkhmth2200_mth1200_dtlr/` - processed MTH1200 vertical-line data.
- `data/tkhmth2200_tkh_dtlr/` - processed TKH vertical-line data.
- `data/hdrc_dtlr/` - processed HDRC line-level data.
- `data/TKHMTH2200/` - raw TKHMTH2200 source data.
- `data/HDRC/` - raw HDRC source data.
- `data/mmocr_exports/` - exported MMOCR recognition datasets.

The `_dtlr` suffix in processed data directories is retained for path compatibility with existing logs and configs.

## Log And Result Locations

- `logs/paper_results_summary.md` - consolidated paper result table.
- `logs/PAPER_RUNS.md` - paper-ready run manifest and archived-run policy.
- `logs/` - full training/evaluation logs and checkpoints.
- `debug_vis/` - box diagnostics and visualization outputs.
- `experiments/notes/goal_status.md` - sparse resumable experiment status.
- `docs/paper-drafts/` - current manuscript drafts and figures.

## Trusted Paper Runs

- `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/` - current strongest MTHv2 result with expected-count auxiliary loss.
- `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/` - original MTHv2 query-budget result.
- `logs/hdrc_qbudget_full_0607/` - HDRC qbudget-localization-query result.
- `logs/mth1000mth1200pre_hdrcft_full_0527-1732/` - HDRC charset-aware mainline.
- `logs/hdrc_charset_random_full_visible1_0605/` - HDRC random-head control.

Older MTH1000/MTH1200/TKH logs remain useful for provenance but are not the primary MTHv2/HDRC paper evidence.

## Tests

- `tests/test_ctc_eval_utils.py` - CTC evaluation/calibration tests.
- `tests/test_query_activation_budget.py` - query-budget loss tests.
- `tests/test_query_activation_module.py` - query activation module tests.
- `tests/test_glyph_prototype_branch.py` - glyph prototype branch tests.
- `tests/test_query_sequence_refiner.py` - query sequence refiner tests.
- `tests/test_sgq_short_query_loss.py` - short-query CE tests.
