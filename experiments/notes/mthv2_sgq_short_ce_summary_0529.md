# MTHv2 SGQ Short Query CE Summary

Date: 2026-05-29

## Module

Module 1: SGQ Short Query CE

Switches:

- `short_gt_ce_loss_coef=0.02`
- `short_gt_ce_max_len=2`
- `short_gt_ce_gamma=1.0`

Config:

- `config/MTHV2_dtlr_sgq_short_ce.py`

Dataset:

- `dataset_file=mth_combo`
- validation split total: `10948`

## Training

Launch command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Checkpoints:

- best: `logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth`
- final: `logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint.pth`

Smoke tests:

- unit/config: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_sgq_short_query_loss.py`
- result: `Ran 5 tests ... OK`
- runtime smoke: `logs/mthv2_sgq_short_ce_train_smoke_0528-2238`, exited with `Reached max_optimizer_steps=1 at epoch 1`

Best validation epoch from `log.txt`:

- SGQ best epoch: `5`
- SGQ best `test_cer_oracle_direction`: `0.11552016232612522`
- MTHv2 baseline best `test_cer_oracle_direction`: `0.11397798822246911`
- final epoch `11` regressed to `0.49223755104084943`

## Overall AR/CR/CER

File:

- `logs/mthv2_sgq_short_ce_full_0528-2240/chinese_micro_valid_0529.json`

Metrics:

- macro AR: `0.8844746886079347`
- macro CR: `0.886798645751378`
- macro CER: `0.11552531139206534`
- micro AR: `0.9476850146840798`
- micro CR: `0.9490353834386244`
- micro CER: `0.05231498531592019`

Edit totals:

- chars: `105897`
- insertions: `143`
- deletions: `2742`
- substitutions: `2655`

## Clean CTC Summary

Files:

- `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_clean_0529.json`
- `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_clean_0529.jsonl`

Clean valid comparison:

| Metric | Baseline | SGQ |
| --- | ---: | ---: |
| overall CER | `0.051956146066460804` | `0.052277212763345515` |
| empty rate | `0.03379612714651078` | `0.029046401169163318` |
| deletion rate | `0.0272434535444819` | `0.026610763288856153` |
| substitution rate | `0.02248411192007328` | `0.023947798332341803` |
| len=1 CER | `0.26737967914438504` | `0.2697563874034462` |
| len=1 empty | `0.1948900772430184` | `0.1711229946524064` |
| len=2 CER | `0.22151898734177214` | `0.23022151898734178` |
| len=2 empty | `0.030854430379746837` | `0.022151898734177215` |
| 3-5 CER | `0.18427569129178703` | `0.18572018159306644` |
| 6-10 CER | `0.1214020427112349` | `0.12163416898792943` |
| 11+ CER | `0.03324255392729002` | `0.03324255392729002` |

Interpretation:

- SGQ reduces clean empty/deletion rates for len=1/2.
- The gain is offset by more substitutions, so clean overall CER and len=1/2 CER do not improve.

## Calibrated CTC Summary

Best SGQ decode-bias setting:

- `blank_bias=-1.6`
- `nonblank_bias=1.0`
- `ratio_nonblank_bias=0.0`

Files:

- `logs/mthv2_sgq_short_ce_full_0528-2240/decode_bias_sweep_valid_0529.json`
- `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_bias_b-16_nb10_0529.json`
- `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_bias_b-16_nb10_0529.jsonl`

Calibrated valid comparison:

| Metric | Baseline Best Sweep | SGQ Best Sweep |
| --- | ---: | ---: |
| blank bias | `-2.0` | `-1.6` |
| nonblank bias | `1.0` | `1.0` |
| overall CER | `0.04561980037205964` | `0.04455272576182517` |
| empty rate | `0.007124588966021191` | `0.008677383997077091` |
| deletion rate | `0.007677271310802006` | `0.006836832016015562` |
| substitution rate | `0.03410861497492847` | `0.03490183857899657` |
| len=1 CER | `0.22281639928698752` | `0.23529411764705882` |
| len=1 empty | `0.0451574569221628` | `0.055852644087938205` |
| len=2 CER | `0.19026898734177214` | `0.20292721518987342` |
| len=2 empty | `0.0015822784810126582` | `0.0` |
| 3-5 CER | `0.15889393314073463` | `0.158687577383409` |
| 6-10 CER | `0.10584958217270195` | `0.10515320334261838` |
| 11+ CER | `0.02970864133488955` | `0.02795789564691134` |

Interpretation:

- SGQ combines well with decode calibration for overall valid CER.
- The overall calibrated gain mostly comes from length `3+`, especially `11+`, not from len=1/2.
- The original goal targeted len=1/2 empty/deletion without overall regression. SGQ alone reduces short empty/deletion but regresses short CER and overall CER; SGQ plus calibration improves overall CER but still regresses len=1/2 CER against calibrated baseline.

## Representative Errors

Worst calibrated cases:

| idx | gt_len | pred_len | CER | gt | pred | error |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| `1384` | 2 | 7 | `2.5` | `##` | `#####燈#` | insertion over-activation |
| `63` | 1 | 2 | `2.0` | `兹` | `#慈` | insertion + substitution |
| `835` | 1 | 3 | `2.0` | `音` | `立音曰` | insertion |
| `847` | 1 | 2 | `2.0` | `羡` | `生次` | insertion + substitution |
| `1394` | 1 | 2 | `2.0` | `光` | `一五` | insertion + substitution |
| `1378` | 3 | 6 | `1.3333333333333333` | `名名界` | `名#名#名迅` | insertion + substitution |

Clean short empty/deletion examples:

| idx | gt_len | gt | pred |
| ---: | ---: | --- | --- |
| `36` | 1 | `匝` | empty |
| `48` | 2 | `鈴|` | empty |
| `67` | 1 | `炙` | empty |
| `82` | 1 | `篾` | empty |
| `83` | 1 | `#` | empty |
| `189` | 1 | `虔` | empty |
| `193` | 1 | `鄧` | empty |
| `582` | 1 | `蘖` | empty |

## Decision

Decision for Module 1 on MTHv2: mixed but not a clean success.

- Clean inference: harmful for the goal because overall CER and len=1/2 CER regress, despite lower short empty/deletion.
- Calibrated inference: useful for overall CER but not for the short-text len=1/2 CER target.
- Count as a no-improvement module for the original short-text objective on MTHv2.

Recommended next step:

- Do not launch HDRC SGQ as a full training run unless the goal is broadened to overall calibrated CER.
- Move to Module 2, Short-Bucket Decode Calibration, because it already targets empty/deletion directly without another full training run and preserved/improved overall CER on the MTHv2 baseline.
