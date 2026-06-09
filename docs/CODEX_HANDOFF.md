# Codex Handoff

Last updated: 2026-06-09

## Project Goal

This repository is used for SAQT vertical ancient Chinese text recognition experiments. The practical target is single-column / line-level recognition for vertical ancient text images. It is not a page-level layout-analysis project and should not be framed as detecting page regions, reading order, or full-document layout.

The paper story currently being shaped is: SAQT uses structure-aware query/localization pretraining, then adapts the query representation for vertical ancient text recognition with CTC finetuning, development-set-fixed decode calibration, and cross-dataset evaluation on MTHv2-combo and HDRC. Historical MTH1000, MTH1200, and TKH runs remain useful for provenance. The writing should present SAQT as the paper-facing method while acknowledging query-based detection/localization influences where appropriate.

## Current Code Structure

- `main_synthetic.py`: stage-1 detection / localization pretraining.
- `finetuning.py`: CTC head reconstruction and full recognition finetuning.
- `evaluation.py`: standalone evaluation entry point.
- `engine.py`: shared training and evaluation loops.
- `models/saqt/`: paper-facing SAQT model registration layer.
- `models/dino/`: compatibility implementation layer for the query transformer, criterion, and deformable attention modules used by existing checkpoints.
- `datasets/`: dataset builders and transforms.
- `datasets/MTH1000.py`: MTH1000-style processed single-column line dataset.
- `datasets/MTHCombo.py`: combined MTH1000/MTH1200/TKH dataset.
- `util/ctc_decoding.py`: CTC greedy decode and decode-time calibration.
- `tools/analyze_ctc_errors.py`: CER/AR/CR, empty prediction, length-bucket analysis.
- `tools/eval_ctc_micro_batch.py`: batch CTC micro CER/AR/CR evaluator for valid/test clean or fixed bias.
- `tools/sweep_ctc_decode_bias.py`: blank / nonblank decode calibration sweeps.
- `tools/format_ctc_result_row.py`: formats completed CTC JSON results into Markdown/CSV paper table rows.
- `tools/diagnose_boxes.py`: stage-1 query/box diagnostic.
- `tools/export_mmocr_recog_dataset.py`: export processed SAQT-compatible datasets to MMOCR text-recognition format.
- `experiments/configs/mmocr/`: MMOCR comparison configs.
- `PROJECT_MAP.md`: concise repository map.

Important configs:

- `config/SAQT_MTHV2.py`: paper-facing MTHv2-combo CTC finetuning config.
- `config/SAQT_HDRC.py`: paper-facing HDRC CTC finetuning config.
- `config/MTH1000_dtlr.py`: legacy MTH1000/TKH/HDRC-style CTC finetuning config.
- `config/MTHV2_dtlr.py`: legacy MTHv2-combo CTC finetuning config.
- `config/MTHV2_stage1.py`: full MTHv2 stage-1 detection pretraining config.
- `config/MTH1000_MTH1200_stage1.py`: trusted real stage-1 baseline.
- `config/MTHV2_dtlr_sgq_short_ce.py`: SGQ short-query CE experiment.
- `config/HDRC_dtlr_sgq_short_ce.py`: HDRC SGQ short-query CE experiment.

Important data/log locations:

- `data/tkhmth2200_mth1000_dtlr/`
- `data/tkhmth2200_mth1200_dtlr/`
- `data/tkhmth2200_tkh_dtlr/`
- `data/hdrc_dtlr/`
- `data/mmocr_exports/`
- `logs/`
- `debug_vis/`
- `experiments/notes/goal_status.md`
- `experiments/notes/paper_draft_v1.md`
- `logs/paper_results_summary.md`
- `docs/EXPERIMENT_POSTPROCESS.md`: canonical workflow after a finetuning experiment finishes.

## Completed Changes

- Added project map:
  - `PROJECT_MAP.md`
- Added / updated paper draft:
  - `experiments/notes/paper_draft_v1.md`
- Added SGQ short-query CE experiment path:
  - `config/MTHV2_dtlr_sgq_short_ce.py`
  - `config/HDRC_dtlr_sgq_short_ce.py`
  - `tests/test_sgq_short_query_loss.py`
- Added adaptive decode calibration support:
  - `util/ctc_decoding.py`
  - `tools/sweep_ctc_decode_bias.py`
  - `tests/test_ctc_eval_utils.py`
- Added MMOCR export and comparison workflow files under `data/mmocr_exports/` and `experiments/configs/mmocr/`.
- Created full-MTHv2 stage-1 candidate and downstream head/full finetune runs.

## Key Experiment Results

Primary paper table is in `logs/paper_results_summary.md`.

Best SAQT-style results currently summarized there:

| Dataset | Decode | Test CER | Test AR | Test CR | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| MTH1000 | bias `-1.2/1.0` | 4.88 | 95.12 | 95.50 | better than clean 5.29 CER |
| MTH1200 | bias `-1.2/1.0` | 5.18 | 94.82 | 95.00 | clean 5.95 CER |
| TKH | bias `-1.6/1.0` | 1.04 | 98.96 | 99.02 | strongest dataset result |
| MTHv2-combo-qbudget | bias `-2.0/0.8` | 3.31 | 96.69 | 96.90 | current best combined-data result |
| HDRC | bias `-2.0/0.4` | 9.30 | 90.70 | 91.80 | harder domain, long-column weakness |

Important current MTHv2 qbudget result:

- Run: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- Checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth`
- Clean test: CER `3.83`, AR `96.17`, CR `96.29`
- Validation-selected bias: `blank=-2.0`, `nonblank=0.8`
- Bias test: CER `3.31`, AR `96.69`, CR `96.90`, empty `0.89`, Pred/GT `0.997`
- Result files:
  - `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_clean_0603.json`
  - `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/decode_bias_sweep_valid_0603.json`
  - `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_bias_b-20_nb08_0603.json`

Important baseline run paths:

- Trusted real stage-1:
  - `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`
- Trusted MTH1000 full finetune:
  - `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth`
- MTHv2-combo head baseline:
  - `logs/mthv2_mth1000mth1200tkh_head_0528-0003/`
- MTHv2-combo full baseline:
  - `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`

MMOCR MTHv2-combo baselines:

| Model | Orientation | Test CER | Test AR | Test CR |
| --- | --- | ---: | ---: | ---: |
| CRNN | `Rot90(k=3)` | 4.49 | 95.51 | 95.63 |
| SVTR-tiny | `Rot90(k=3)` | 4.44 | 95.56 | 95.68 |
| SVTR-small | `Rot90(k=3)` | 4.66 | 95.34 | 95.44 |
| SVTR-L | `Rot90(k=3), 48x160` | 4.84 | 95.16 | 95.26 |
| CRNN | `Rot90(k=1)` | 27.26 | 72.74 | 73.81 |
| SVTR-tiny | `Rot90(k=1)` | 6.58 | 93.42 | 93.52 |

Full-MTHv2 stage-1 candidate:

- Stage-1 run: `logs/mthv2_full_stage1_det_0531-1258`
- Stage-1 final train loss: about `3.6403`
- Box diagnostic on MTH1000 valid:
  - `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601`
  - avg blank ratio about `0.8416`
  - avg predicted nonblank count about `142.6`
  - avg GT length about `7.49`
- Interpretation: usable enough to try, but over-activated compared with trusted real stage-1 baseline.

Full-MTHv2 stage-1 -> MTHv2 head reconstruction:

- Run: `logs/mthv2_fullstage1pre_mthv2_head_0601`
- Best head checkpoint exists.
- CER by epoch:
  - epoch 0: `0.1687470099455089`
  - epoch 1: `0.1578794820103037`
  - epoch 2: `0.15283326830434354`
- Old MTHv2 head baseline epoch-2 CER: `0.14526833428705468`.
- Interpretation: new head is worse than old head but close enough that the user chose to try full finetuning.

Current active DTLR full finetune:

- tmux session: `dtlr_mthv2_full_ft_0601`
- Log dir: `logs/mthv2_fullstage1pre_mthv2_full_tmux_0601`
- Source checkpoint: `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth`
- Command uses `cuda:0`, `dataset_file=mth_combo`, `config/MTHV2_dtlr.py`, `num_classes=6727`, `batch_size=2`, `lr=1e-5`, `epochs=12`, `eval_epoch=1`, `max_iterations=10000`.
- As of the latest check, the run had reached epoch 8 training.
- `log.txt` contains validation rows through epoch 7:
  - epoch 0 CER `0.14209875725049612`
  - epoch 1 CER `0.14348676074442737`
  - epoch 2 CER `0.13439168210258723`
  - epoch 3 CER `0.13650454108627846`
  - epoch 4 CER `0.13991440891643625`
  - epoch 5 CER `0.14382442905243265`
  - epoch 6 CER `0.1522016002257195`
  - epoch 7 CER `0.23396587828711218`
- Best so far appears to be epoch 2 by validation CER.
- `checkpoint_best_regular.pth` exists in the active log dir.
- Do not judge final usefulness until full run finishes and clean/bias test summaries with length buckets are generated.

## Failed Attempts / Known Bad Runs

- `logs/mthv2_full_stage1_0531-1248` and early bad full-MTHv2 stage-1 attempts had incorrect/loss-exploding behavior and should not be reused.
- `logs/mthv2_fullstage1pre_mthv2_full_0601` was started through the Codex tool session and stopped at epoch 0 step `3160/42088` before validation; it saved no checkpoint. Do not use it as a result.
- SGQ short-query CE MTHv2 full run (`logs/mthv2_sgq_short_ce_full_0528-2240`) encountered stdout pipe blocking after the managing session was interrupted. Its epoch 0 validation completed with CER about `0.1270`, but the process management was fragile.
- MMOCR SAR runs repeatedly hung in this environment, including during training with workers enabled. A safer resume with all dataloader workers set to 0 was attempted; treat SAR as unstable until fully verified.

## Current Main Problems

- The strongest narrative is not "vertical text alone", because rotated MMOCR baselines can perform well. The paper should emphasize structured localization pretraining, unified single-column recognition, low annotation/transfer framing, and calibrated decoding rather than simply "vertical recognition".
- MTHv2 short columns remain weak, especially `len=1` and `len=2` buckets.
- HDRC remains harder, especially long columns.
- Decode-time bias/calibration improves metrics but must be described carefully as validation-selected post-processing, not as a learned model module unless using the adaptive calibration code path.
- Full-MTHv2 stage-1 over-activates nonblank queries in box diagnostics.
- Long SAQT training should not be launched in a Codex foreground exec session; use `tmux`.

## Next Recommended Steps

1. Let `dtlr_mthv2_full_ft_0601` finish or stop only if validation clearly degrades for multiple epochs and a best checkpoint is already saved.
2. After completion, run clean CTC error analysis on valid/test for `logs/mthv2_fullstage1pre_mthv2_full_tmux_0601/checkpoint_best_regular.pth`.
3. Run decode-bias sweep on validation, then apply selected calibration to test.
4. Report CER/AR/CR and length buckets for clean and bias.
5. Compare against:
   - `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
   - MMOCR CRNN/SVTR baselines in `logs/paper_results_summary.md`
6. Update `logs/paper_results_summary.md` only after clean/bias test summaries exist.
7. For the paper, keep the method framing around query-based localization pretraining + CTC recognition + validation-selected calibration; do not overclaim page-level detection.

## Common Commands

Attach to the active DTLR training:

```bash
tmux attach -t dtlr_mthv2_full_ft_0601
```

Detach without stopping:

```text
Ctrl-b, then d
```

Check current DTLR full-finetune log lightly:

```bash
tail -n 40 logs/mthv2_fullstage1pre_mthv2_full_tmux_0601/info.txt
tail -n 20 logs/mthv2_fullstage1pre_mthv2_full_tmux_0601/log.txt
```

Launch current DTLR full finetune in tmux:

```bash
tmux new-session -d -s dtlr_mthv2_full_ft_0601 'cd /home/ubuntu/DTLR && /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_full_tmux_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000'
```

Trusted MTHv2 full baseline path:

```bash
logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth
```

Stage-1 box diagnostic pattern:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/diagnose_boxes.py -c config/MTHV2_stage1.py --dataset_file mth1000 --checkpoint logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth --split valid --device cuda:0 --num_workers 0 --num_samples 100 --viz_topk 40 --show_gt_boxes --output_dir debug_vis/NEW_DEBUG_DIR
```

## Pitfalls To Avoid

- Do not run long training in a foreground Codex exec session; use `tmux`.
- Do not keep polling logs every 30 seconds; it wastes token/context. Only inspect at key points.
- Do not update `experiments/notes/goal_status.md` on every minor progress check. Update only for launches, validation results, completion, errors, or major file/result changes.
- Do not judge experiments by training loss alone. Use validation CER and final CER/AR/CR plus length buckets.
- Do not treat `max_iterations` in `finetuning.py` as a global optimizer-step limit. It is a per-epoch sample cap; with `batch_size=2` and `max_iterations=10000`, each epoch is about 5000 optimizer steps.
- Do not assume `max_iterations` stops `main_synthetic.py` stage-1 runs. Stage-1 budget is effectively `len(train_loader) * epochs`.
- Do not silently edit shared baseline configs. Prefer new config files or explicit `--options`.
- Do not reuse interrupted/no-checkpoint runs as results.
- Do not delete logs/checkpoints/datasets unless explicitly asked.
- Do not present SAQT stage-1 character boxes as page-level detection. It is query/localization pretraining for line-level recognition.
- Do not claim a module is valid for the paper without clean/bias test results and length-bucket analysis.
