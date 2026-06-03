# Project Map

Concise map of the DTLR vertical ancient text recognition repository.

## Core Entry Points

- `main_synthetic.py` - stage-1 detection / localization pretraining.
- `finetuning.py` - CTC head reconstruction and full recognition finetuning.
- `evaluation.py` - standalone evaluation entry point.
- `engine.py` - shared train/eval loops.

## Important Evaluation And Analysis Tools

- `tools/diagnose_boxes.py` - stage-1 box / query diagnostic with visualizations.
- `tools/analyze_ctc_errors.py` - CTC CER, AR, CR, length buckets, empty prediction analysis.
- `tools/sweep_ctc_decode_bias.py` - blank / nonblank decode calibration sweeps.
- `tools/eval_chinese_micro.py` - Chinese micro-metric evaluation.
- `tools/eval_mmocr_textrecog_predictions.py` - convert/evaluate MMOCR text recognition outputs.
- `tools/compare_paper_runs.py` - compare paper-oriented experiment runs.
- `tools/report_mth1000_paper_metrics.py` - MTH1000 paper metric reporting.

## Data Preparation Tools

- `tools/prepare_tkhmth2200_single_column.py` - build processed TKH/MTH vertical-line data.
- `tools/prepare_hdrc_dtlr.py` - build processed HDRC data.
- `tools/prepare_mth1000_rot90.py` - rotated MTH1000 preparation.
- `tools/export_mmocr_recog_dataset.py` - export DTLR datasets for MMOCR recognition.
- `tools/generate_vertical_ancient_synth.py` - synthetic vertical ancient text generation.
- `tools/generate_vertical_synth_mth.py` - MTH-style vertical synthetic generation.

## Key Config Locations

- `config/Chinese.py` - base Chinese DTLR config.
- `config/MTH1000_dtlr.py` - main MTH1000/TKH/HDRC-style CTC finetuning config.
- `config/MTHV2_dtlr.py` - MTHv2 combo CTC finetuning config.
- `config/MTHV2_stage1.py` - full MTHv2 stage-1 detection pretraining config.
- `config/MTH1000_MTH1200_stage1.py` - trusted real stage-1 baseline config.
- `config/MTH1000_MTH1200_stage1_vmsr_safe.py` - VMSR stage-1 variant.
- `config/MTHV2_dtlr_sgq_short_ce.py` - MTHv2 SGQ short-query CE experiment config.
- `config/HDRC_dtlr_sgq_short_ce.py` - HDRC SGQ short-query CE experiment config.
- `experiments/configs/mmocr/` - MMOCR comparison configs.

## Model And Dataset Code

- `models/dino/` - DINO/DTLR model, transformer, CTC criterion, deformable attention.
- `models/dino/dino.py` - main model and CTC criterion implementation.
- `datasets/` - dataset builders and transforms.
- `datasets/MTH1000.py` - MTH1000-style processed line dataset.
- `datasets/MTHCombo.py` - combined MTH1000/MTH1200/TKH dataset.
- `datasets/synthetic_lines_general.py` - synthetic vertical line dataset support.
- `util/ctc_decoding.py` - CTC greedy decoding and decode-time calibration.

## Data Locations

- `data/tkhmth2200_mth1000_dtlr/` - processed MTH1000 vertical-line data.
- `data/tkhmth2200_mth1200_dtlr/` - processed MTH1200 vertical-line data.
- `data/tkhmth2200_tkh_dtlr/` - processed TKH vertical-line data.
- `data/hdrc_dtlr/` - processed HDRC data.
- `data/TKHMTH2200/` - raw TKHMTH2200 source data.
- `data/HDRC/` - raw HDRC source data.
- `data/mmocr_exports/` - exported MMOCR recognition datasets.

## Log And Result Locations

- `logs/` - main DTLR training/evaluation logs, checkpoints, summaries.
- `debug_vis/` - box diagnostics and visualization outputs.
- `experiments/notes/goal_status.md` - current resumable experiment status.
- `experiments/notes/goal_plan_mthv2_hdrc.md` - MTHv2/HDRC experiment plan.
- `experiments/notes/paper_draft_v1.md` - current paper draft.
- `logs/paper_results_summary.md` - consolidated paper result table.

## Trusted Baselines

- `logs/mth1000_mth1200_stage1_0512-1755/` - trusted real stage-1 baseline.
- `logs/mth1000mth1200pre_mth1000ft_head_0513-2057/` - trusted MTH1000 head reconstruction.
- `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/` - trusted MTH1000 full finetuning.
- `logs/mthv2_mth1000mth1200tkh_head_0528-0003/` - MTHv2 combo head reconstruction baseline.
- `logs/mthv2_mth1000mth1200tkh_full_0528-0957/` - MTHv2 combo full finetuning baseline.
- `logs/mthv2_full_stage1_det_0531-1258/` - full MTHv2 stage-1 detection pretraining candidate.

## Tests

- `tests/test_ctc_eval_utils.py` - CTC evaluation/calibration tests.
- `tests/test_sgq_short_query_loss.py` - SGQ short-query CE tests.
- `tests/test_paper_workflow_tools.py` - paper workflow utility tests.
- `tests/test_query_activation_module.py` - query activation module tests.
- `tests/test_glyph_prototype_branch.py` - glyph prototype branch tests.
