# Paper Results Summary

Last updated: 2026-06-08

This table uses dataset-level micro metrics unless otherwise noted.

- `AR = 1 - (I + D + S) / N`
- `CR = 1 - (D + S) / N`
- `CER = (I + D + S) / N`
- `clean` means greedy CTC decoding without decode-time bias.
- `bias` means decode-time calibration selected on the corresponding validation split, then applied to test.

## Main Test Table

| Dataset | Split | Decode | Bias blank/nonblank | Samples | CER micro | AR micro | CR micro | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| MTH1000 | test | clean | 0/0 | 4044 | 5.29 | 94.71 | 94.94 | 1.88 | 0.978 | 14.20 | 19.54 | 15.81 | 10.40 | 3.96 | `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/ctc_error_summary_test_clean_0526.json` |
| MTH1000 | test | bias | -1.2/1.0 | 4044 | 4.88 | 95.12 | 95.50 | 0.89 | 0.993 | 12.20 | 17.22 | 14.06 | 10.78 | 3.65 | `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/ctc_error_summary_test_bias_b-12_nb10_0526.json` |
| MTH1200 | test | clean | 0/0 | 4029 | 5.95 | 94.05 | 94.16 | 6.75 | 0.962 | 49.53 | 26.99 | 18.27 | 13.64 | 2.03 | `logs/mth1000mth1200pre_mth1200ft_full_0526-2231/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_mth1200ft_full_0526-2231/ctc_error_summary_test_clean_0527.json` |
| MTH1200 | test | bias | -1.2/1.0 | 4029 | 5.18 | 94.82 | 95.00 | 3.80 | 0.984 | 46.21 | 23.27 | 15.55 | 12.08 | 1.73 | `logs/mth1000mth1200pre_mth1200ft_full_0526-2231/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_mth1200ft_full_0526-2231/ctc_error_summary_test_bias_b-12_nb10_0527.json` |
| TKH | test | clean | 0/0 | 2382 | 1.47 | 98.53 | 98.58 | 0.00 | 0.990 | - | 0.00 | 4.55 | 7.07 | 1.45 | `logs/mth1000mth1200pre_tkhft_full_0527-1056/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_tkhft_full_0527-1056/ctc_error_summary_test_clean_0527.json` |
| TKH | test | bias | -1.6/1.0 | 2382 | 1.04 | 98.96 | 99.02 | 0.00 | 0.997 | - | 0.00 | 4.55 | 5.05 | 1.02 | `logs/mth1000mth1200pre_tkhft_full_0527-1056/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_tkhft_full_0527-1056/ctc_error_summary_test_bias_b-16_nb10_0527.json` |
| MTHv2-combo | test | clean | 0/0 | 10455 | 4.47 | 95.53 | 95.71 | 3.68 | 0.978 | 34.79 | 26.11 | 19.97 | 12.98 | 2.43 | `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth` | `logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_test_clean_0528.json` |
| MTHv2-combo | test | bias | -2.0/1.0 | 10455 | 3.90 | 96.10 | 96.37 | 1.04 | 0.996 | 29.60 | 22.53 | 17.00 | 11.82 | 2.14 | `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth` | `logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_test_bias_b-20_nb10_0528.json` |
| MTHv2-combo-qbudget | test | clean | 0/0 | 10455 | 3.83 | 96.17 | 96.29 | 2.89 | 0.982 | 31.56 | 23.16 | 17.92 | 11.62 | 1.98 | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth` | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_clean_0603.json` |
| MTHv2-combo-qbudget | test | bias | -2.0/0.8 | 10455 | 3.31 | 96.69 | 96.90 | 0.89 | 0.997 | 27.95 | 19.48 | 14.86 | 10.46 | 1.72 | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth` | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_bias_b-20_nb08_0603.json` |
| MTHv2-combo-qbudget-count001 | test | clean | 0/0 | 10455 | 3.67 | 96.33 | 96.50 | 2.83 | 0.984 | 29.98 | 21.41 | 17.39 | 11.82 | 1.87 | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/checkpoint_best_regular.pth` | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_clean_0608.json` |
| MTHv2-combo-qbudget-count001 | test | bias | -2.0/0.8 | 10455 | 3.25 | 96.75 | 97.00 | 0.77 | 0.998 | 26.07 | 18.60 | 14.99 | 10.75 | 1.68 | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/checkpoint_best_regular.pth` | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_bias_b-20_nb08_0608.json` |
| MTHv2-head-only | test | clean | 0/0 | 10455 | 7.00 | 93.00 | 93.42 | 3.11 | 0.963 | 36.66 | 28.15 | 22.52 | 17.26 | 4.90 | `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth` | `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_clean_0607.json` |
| MTHv2-head-only | test | bias | -0.8/1.0 | 10455 | 6.17 | 93.83 | 95.03 | 1.55 | 0.993 | 33.51 | 23.69 | 18.87 | 15.31 | 4.37 | `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth` | `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_bias_bm08_nb10_0607.json` |
| MTHv2-no-localization | test | clean | 0/0 | 10455 | 100.00 | 0.00 | 0.00 | 99.97 | 0.000 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | `logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth` | `logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0606.json` |
| MTHv2-no-localization | test | bias | -2.0/0.4 | 10455 | 99.89 | 0.11 | 0.16 | 98.78 | 0.005 | 100.00 | 100.00 | 100.00 | 100.00 | 99.87 | `logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth` | `logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_b-20_nb04_0606.json` |
| HDRC | test | clean | 0/0 | 3381 | 10.01 | 89.99 | 90.33 | 2.19 | 0.938 | 12.74 | 9.19 | 5.37 | 8.40 | 11.13 | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_clean_0527.json` |
| HDRC | test | bias | -2.0/0.4 | 3381 | 9.30 | 90.70 | 91.80 | 0.98 | 0.977 | 9.87 | 7.35 | 4.54 | 7.74 | 10.64 | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_bias_b-20_nb04_0527.json` |
| HDRC-qbudget-localization-query | test | clean | 0/0 | 3381 | 8.50 | 91.50 | 91.64 | 1.86 | 0.938 | 11.46 | 7.86 | 4.09 | 6.44 | 9.63 | `logs/hdrc_qbudget_full_0607/checkpoint_best_regular.pth` | `logs/hdrc_qbudget_full_0607/micro_test_clean_0607.json` |
| HDRC-qbudget-localization-query | test | bias | -2.0/1.0 | 3381 | 6.56 | 93.44 | 94.36 | 0.77 | 0.990 | 8.28 | 7.16 | 4.58 | 5.38 | 6.71 | `logs/hdrc_qbudget_full_0607/checkpoint_best_regular.pth` | `logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json` |
| HDRC-head-only | test | clean | 0/0 | 3381 | 17.72 | 82.28 | 82.68 | 3.11 | 0.864 | 17.52 | 15.08 | 12.56 | 18.60 | 18.87 | `logs/mth1000mth1200pre_hdrcft_head_0527-1530/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_clean_0607.json` |
| HDRC-head-only | test | bias | -2.0/0.4 | 3381 | 14.03 | 85.97 | 89.72 | 1.24 | 0.993 | 13.85 | 12.29 | 10.53 | 16.09 | 14.58 | `logs/mth1000mth1200pre_hdrcft_head_0527-1530/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_bias_b-20_nb04_0607.json` |
| HDRC-random-head | test | clean | 0/0 | 3381 | 18.99 | 81.01 | 81.41 | 3.73 | 0.861 | 17.04 | 14.96 | 8.50 | 14.82 | 22.17 | `logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth` | `logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.json` |
| HDRC-random-head | test | bias | -1.2/1.0 | 3381 | 17.28 | 82.72 | 83.97 | 1.80 | 0.919 | 13.54 | 11.85 | 7.95 | 14.69 | 20.22 | `logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth` | `logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_b-12_nb10_0605.json` |
| CHDAC | test | clean | 0/0 | 4755 | 46.00 | 54.00 | 55.54 | 7.93 | 0.672 | 50.74 | 41.47 | 35.80 | 34.72 | 48.76 | `logs/chdac_qbudgetpre_full_0604/checkpoint_best_regular.pth` | `logs/chdac_qbudgetpre_full_0604/micro_test_clean_0604.json` |
| CHDAC | test | bias | -1.2/1.0 | 4755 | 44.22 | 55.78 | 60.50 | 4.00 | 0.836 | 48.00 | 36.40 | 31.59 | 32.02 | 47.47 | `logs/chdac_qbudgetpre_full_0604/checkpoint_best_regular.pth` | `logs/chdac_qbudgetpre_full_0604/micro_test_bias_b-12_nb10_0604.json` |
| CHDAC-lowLR | test | clean | 0/0 | 4755 | 36.10 | 63.90 | 64.43 | 7.02 | 0.761 | 50.32 | 38.18 | 33.52 | 31.40 | 36.81 | `logs/chdac_qbudgetpre_headlong_full_lowbb_0605/checkpoint_best_regular.pth` | `logs/chdac_qbudgetpre_headlong_full_lowbb_0605/micro_test_clean_0606.json` |
| CHDAC-lowLR | test | bias | -2.0/0 | 4755 | 33.13 | 66.87 | 68.73 | 4.12 | 0.888 | 46.74 | 34.63 | 29.34 | 28.74 | 33.94 | `logs/chdac_qbudgetpre_headlong_full_lowbb_0605/checkpoint_best_regular.pth` | `logs/chdac_qbudgetpre_headlong_full_lowbb_0605/micro_test_bias_b-20_nb00_0606.json` |

## Validation / Selection Records

| Dataset | Split | Decode | Bias blank/nonblank | Samples | CER micro | AR micro | CR micro | Notes | Result file |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| MTH1200 | valid | clean | 0/0 | 4157 | 4.74 | 95.26 | 95.36 | Checkpoint-selection reference. | `logs/mth1000mth1200pre_mth1200ft_full_0526-2231/micro_metrics_val_best.json` |
| MTH1200 | valid | bias | -1.2/1.0 | 4157 | 3.98 | 96.02 | 96.16 | Best setting from validation sweep. | `logs/mth1000mth1200pre_mth1200ft_full_0526-2231/decode_bias_sweep_valid_small.json` |
| TKH | valid | clean | 0/0 | 2302 | 0.38 | 99.62 | 99.63 | Checkpoint-selection reference from decode sweep. | `logs/mth1000mth1200pre_tkhft_full_0527-1056/decode_bias_sweep_valid_small_0527.json` |
| TKH | valid | bias | -1.6/1.0 | 2302 | 0.32 | 99.68 | 99.70 | Best setting from validation sweep. | `logs/mth1000mth1200pre_tkhft_full_0527-1056/decode_bias_sweep_valid_small_0527.json` |
| MTHv2-combo | valid | clean | 0/0 | 10948 | 5.20 | 94.80 | 95.03 | Checkpoint-selection reference. | `logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_valid_clean_0528.json` |
| MTHv2-combo | valid | bias | -2.0/1.0 | 10948 | 4.56 | 95.44 | 95.82 | Best setting from validation sweep. | `logs/mthv2_mth1000mth1200tkh_full_0528-0957/decode_bias_sweep_valid_0528.json` |
| MTHv2-combo-qbudget | valid | clean | 0/0 | 10948 | 4.37 | 95.63 | 95.75 | Clean validation for qbudget bias selection; empty `2.67`, Pred/GT `0.980`, len1/len2 CER `23.89`/`20.13`. | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_valid_clean_0603.json` |
| MTHv2-combo-qbudget | valid | bias | -2.0/0.8 | 10948 | 3.76 | 96.24 | 96.45 | Best setting from qbudget validation sweep; empty `0.56`, Pred/GT `0.997`, len1/len2 CER `21.03`/`17.29`. | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/decode_bias_sweep_valid_0603.json` |
| MTHv2-combo-qbudget-count001 | valid | clean | 0/0 | 10948 | 4.22 | 95.78 | 95.95 | Clean validation for expected-count auxiliary loss; empty `2.54`, Pred/GT `0.982`, len1/len2 CER `23.35`/`19.26`. | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_valid_clean_0608.json` |
| MTHv2-combo-qbudget-count001 | valid | bias | -2.0/0.8 | 10948 | 3.72 | 96.28 | 96.54 | Best setting from validation sweep; empty `0.62`, Pred/GT `0.997`, len1/len2 CER `19.85`/`17.09`. | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/decode_bias_sweep_valid_0608.json` |
| MTHv2-head-only | valid | clean | 0/0 | 10948 | 8.56 | 91.44 | 92.10 | Clean validation for MTHv2 head-only checkpoint; empty `3.15`, Pred/GT `0.956`, len1/len2 CER `28.05`/`26.98`. | `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_valid_clean_0607.json` |
| MTHv2-head-only | valid | bias | -0.8/1.0 | 10948 | 7.59 | 92.41 | 94.10 | Best setting from MTHv2 head-only validation sweep; empty `1.42`, Pred/GT `0.994`, len1/len2 CER `25.01`/`23.14`. | `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/decode_bias_sweep_valid_0607.json` |
| MTHv2-no-localization | valid | clean | 0/0 | 10948 | 99.99 | 0.01 | 0.01 | Clean validation for no-localization control; empty `99.96`, Pred/GT `0.000057`. | `logs/mthv2_no_structure_ctc_full_0605/micro_valid_clean_0606.json` |
| MTHv2-no-localization | valid | bias | -2.0/0.4 | 10948 | 99.86 | 0.14 | 0.37 | Best setting from no-localization validation sweep; empty `97.50`, Pred/GT `0.015`. | `logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0606.json` |
| HDRC | valid | clean | 0/0 | 2854 | 13.44 | 86.56 | 86.94 | Checkpoint-selection reference. | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_clean_0527.json` |
| HDRC | valid | bias | -2.0/0.4 | 2854 | 12.32 | 87.68 | 88.71 | Best setting from validation sweep. | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/decode_bias_sweep_valid_0527.json` |
| HDRC-head-only | valid | clean | 0/0 | 2854 | 20.56 | 79.44 | 79.82 | Clean validation for head-only checkpoint. | `logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_valid_clean_0607.json` |
| HDRC-head-only | valid | bias | -2.0/0.4 | 2854 | 15.59 | 84.41 | 87.18 | Best setting from head-only validation sweep. | `logs/mth1000mth1200pre_hdrcft_head_0527-1530/decode_bias_sweep_valid_0607.json` |
| HDRC-random-head | valid | clean | 0/0 | 2854 | 23.47 | 76.53 | 76.84 | Random target classifier control; clean validation before bias selection. | `logs/hdrc_charset_random_full_visible1_0605/micro_valid_clean_0605.json` |
| HDRC-random-head | valid | bias | -1.2/1.0 | 2854 | 22.02 | 77.98 | 79.12 | Best setting from validation sweep. | `logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.json` |
| CHDAC | valid | clean | 0/0 | 5968 | 52.83 | 47.17 | 48.20 | Clean validation for CHDAC bias selection. | `logs/chdac_qbudgetpre_full_0604/micro_valid_clean_0604.json` |
| CHDAC | valid | bias | -1.2/1.0 | 5968 | 49.85 | 50.15 | 53.18 | Best setting from validation sweep. | `logs/chdac_qbudgetpre_full_0604/decode_bias_sweep_valid_0604.json` |
| CHDAC-lowLR | valid | clean | 0/0 | 5968 | 46.09 | 53.91 | 54.41 | Clean validation before bias selection. | `logs/chdac_qbudgetpre_headlong_full_lowbb_0605/micro_valid_clean_0606.json` |
| CHDAC-lowLR | valid | bias | -2.0/0 | 5968 | 42.92 | 57.08 | 58.96 | Best setting from validation sweep. | `logs/chdac_qbudgetpre_headlong_full_lowbb_0605/decode_bias_sweep_valid_0606.json` |

## Current Takeaways

| Item | Observation |
| --- | --- |
| Best MTH1000 test | `bias -1.2/1.0`, AR `95.12`, CR `95.50`, CER `4.88`. |
| Best MTH1200 test | `bias -1.2/1.0`, AR `94.82`, CR `95.00`, CER `5.18`. |
| Best TKH test | `bias -1.6/1.0`, AR `98.96`, CR `99.02`, CER `1.04`. |
| Best MTHv2-combo test | qbudget-count001 bias `-2.0/0.8`, AR `96.75`, CR `97.00`, CER `3.25`; original qbudget remains AR `96.69`, CR `96.90`, CER `3.31`. |
| Best HDRC test | qbudget-localization-query variant `bias -2.0/1.0`, AR `93.44`, CR `94.36`, CER `6.56`; original HDRC mainline remains `90.70/91.80`. |
| Best CHDAC test | low-backbone-LR `bias -2.0/0`, AR `66.87`, CR `68.73`, CER `33.13`; improved but still not paper-ready. |
| Main remaining weakness | MTH1000/MTH1200/MTHv2 short columns and HDRC long columns; qbudget MTHv2-combo `len=1` CER is still `31.56` under clean decoding. |
| Bias effect on MTH1200 | Test CER improves from `5.95` to `5.18`; empty prediction rate improves from `6.75` to `3.80`. |
| Bias effect on TKH | Test CER improves from `1.47` to `1.04`; empty prediction rate stays `0.00`. |
| Bias effect on MTHv2-combo | Test CER improves from `4.47` to `3.90`; empty prediction rate improves from `3.68` to `1.04`. |
| Bias effect on MTHv2-combo-qbudget | Test CER improves from `3.83` to `3.31`; empty prediction rate improves from `2.89` to `0.89`. |
| Expected-count auxiliary loss on MTHv2-combo-qbudget | Full ablation improves clean test CER from `3.83` to `3.67` and validation-selected bias test CER from `3.31` to `3.25`; the gain is modest but consistent across clean and bias decoding. |
| Bias effect on HDRC | Test CER improves from `10.01` to `9.30`; empty prediction rate improves from `2.19` to `0.98`, mainly by reducing deletions. |
| HDRC head-only vs full recognition | Head-only bias test reaches AR/CR `85.97/89.72`, while full-model recognition training reaches `90.70/91.80` under the same HDRC bias setting `-2.0/0.4`; this supports keeping full-model recognition training in the pipeline. |
| HDRC qbudget-localization-query variant | Early-stopped at the epoch-1 best checkpoint after epoch 2/3 validation regression. Clean test reaches AR/CR `91.50/91.64`; development-set calibrated test reaches `93.44/94.36` with bias `-2.0/1.0`. Treat this as a qbudget-localization-query variant rather than a pure query-budget ablation. |
| MTHv2 head-only vs full recognition | Head-only bias test reaches AR/CR `93.83/95.03`, while full-model recognition training reaches `96.69/96.90`; this adds MTHv2 evidence that classifier-head reconstruction alone is weaker than full-model recognition training. |
| HDRC charset adaptation ablation | Random-head bias test reaches AR/CR `82.72/83.97`, while charset-aware bias test reaches `90.70/91.80` under the matched HDRC full-model recognition protocol. |
| MTHv2 no-localization control | Without character-localization learning, the matched CTC control collapses: clean test AR/CR `0.00/0.00`, validation-protocol calibrated test AR/CR `0.11/0.16`, with empty prediction rate `98.78` under bias decoding. Treat this as a conservative lower-bound control, not a pure causal estimate of the full character-box effect. |
| Bias effect on CHDAC | Original run improves from CER `46.00` to `44.22`; lowLR run improves from `36.10` to `33.13`, with Pred/GT rising from `0.761` to `0.888`. |
| MMOCR SAR on MTHv2 | SAR-k3-768 val best reached `0.8084` 1-N.E.D, but test CER is `26.80` with Pred/GT `1.107`; main failure is insertion/repetition, so it is much weaker than CRNN/SVTR for this comparison. |

## Dataset Detail Comparison (MTHv2 / HDRC / CHDAC)

CHDAC low-backbone-LR full-model recognition training improves substantially over the earlier CHDAC run, but the result is still weak relative to the main MTHv2/HDRC evidence. The main failure mode remains long-line deletion/substitution under severe charset/domain shift.

| Dataset | Processed data | Loader / config | Train / valid / test samples | Total samples | Unique chars | Total chars | Valid length bins `1/2/3-5/6-10/11+` | Test length bins `1/2/3-5/6-10/11+` |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| MTHv2-combo | `data/tkhmth2200_mth1000_dtlr` + `data/tkhmth2200_mth1200_dtlr` + `data/tkhmth2200_tkh_dtlr` | `dataset_file=mth_combo`, `config/MTHV2_dtlr.py` | `84176 / 10948 / 10455` | `105579` | `6727` | `1067699` | `1683 / 1264 / 1339 / 575 / 6087` | `1331 / 1032 / 1272 / 579 / 6241` |
| HDRC | `data/hdrc_dtlr` | `dataset_file=mth1000`, `config/MTH1000_dtlr.py`, options `mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC` | `24285 / 2854 / 3381` | `30520` | `4017` | `220396` | `510 / 590 / 563 / 290 / 901` | `628 / 789 / 747 / 289 / 928` |
| CHDAC | `data/chdac_dtlr` | `dataset_file=mth1000`, `config/MTH1000_dtlr.py`, options `mth1000_root=chdac_dtlr mth1000_raw_root=CHDAC` | `39291 / 5968 / 4755` | `50014` | `10364` | `509997` | `810 / 721 / 1401 / 1055 / 1981` | `475 / 592 / 904 / 765 / 2019` |

| Dataset | Current checkpoint / run | Current best validation status | Final test status | Notes |
| --- | --- | --- | --- | --- |
| MTHv2-combo-qbudget | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth` | Valid bias `-2.0/0.8`: CER `3.76`, AR `96.24`, CR `96.45`. | Test bias `-2.0/0.8`: CER `3.31`, AR `96.69`, CR `96.90`, empty `0.89`, Pred/GT `0.997`. | Strong original qbudget result; qbudget improves clean CER `3.83` to bias CER `3.31`. |
| MTHv2-combo-qbudget-count001 | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/checkpoint_best_regular.pth` | Valid bias `-2.0/0.8`: CER `3.72`, AR `96.28`, CR `96.54`. | Test bias `-2.0/0.8`: CER `3.25`, AR `96.75`, CR `97.00`, empty `0.77`, Pred/GT `0.998`. | Current strongest MTHv2-combo result; expected-count auxiliary loss gives a small but consistent gain over original qbudget. |
| HDRC | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth` | Valid bias `-2.0/0.4`: CER `12.32`, AR `87.68`, CR `88.71`. | Test bias `-2.0/0.4`: CER `9.30`, AR `90.70`, CR `91.80`, empty `0.98`, Pred/GT `0.977`. | Harder domain; long columns remain the main weakness. |
| HDRC-random-head | `logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth` | Valid bias `-1.2/1.0`: CER `22.02`, AR `77.98`, CR `79.12`. | Test bias `-1.2/1.0`: CER `17.28`, AR `82.72`, CR `83.97`, empty `1.80`, Pred/GT `0.919`. | Random target classifier control for charset adaptation; clearly weaker than charset-aware initialization. |
| CHDAC | `logs/chdac_qbudgetpre_headlong_full_lowbb_0605/checkpoint_best_regular.pth` from `logs/chdac_qbudgetpre_head_long_0604_src6727/checkpoint_best_regular.pth` | Valid bias `-2.0/0`: CER `42.92`, AR `57.08`, CR `58.96`; clean valid CER `46.09`. | Test bias `-2.0/0`: CER `33.13`, AR `66.87`, CR `68.73`, empty `4.12`, Pred/GT `0.888`. | Low-backbone-LR finetuning stabilizes CHDAC versus the earlier run, but largest charset/domain shift still leaves CHDAC far weaker than MTHv2/HDRC. |

## PaddleOCR Baseline Comparison (MTHv2-combo)

Rows below are PaddleOCR/PP-OCR recognition-only runs on the same MTHv2-combo test set (`10455` samples), converted with the local PaddleOCR export script to micro `CER/AR/CR`. These are separated from MMOCR because the training code, model implementations, and default recognition heads differ.

| Framework | Model | Orientation | Split | Samples | CER micro | AR micro | CR micro | Paddle acc | 1-N.E.D | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file | Notes |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| PaddleOCR | SVTRv2 | `Rot90(k=3), 48x1024 fixed` | test | 10455 | 5.58 | 94.42 | 95.30 | 65.05 | 0.9071 | 0.00 | 0.991 | 24.27 | 15.99 | 12.53 | 9.82 | 4.56 | `/home/ubuntu/PaddleOCR/output/rec/mthv2_svtrv2_rot90_w1024_gpu0/best_accuracy.pdparams` | `/home/ubuntu/PaddleOCR/output/rec/mthv2_svtrv2_rot90_w1024_gpu0/test_predictions_metrics.json` | From scratch; config `max_text_length=57`, so `NRTRLabelEncode` filters train labels with length 56. |
| PaddleOCR | SVTRv2 | `Rot90(k=3), 48x1024 MultiScaleSampler` | test | 10455 | 5.89 | 94.11 | 95.29 | 62.84 | 0.9027 | 0.01 | 0.996 | 25.32 | 17.05 | 12.77 | 10.50 | 4.82 | `/home/ubuntu/PaddleOCR/output/rec/mthv2_svtrv2_rot90_ms_w1024_gpu1/best_accuracy.pdparams` | `/home/ubuntu/PaddleOCR/output/rec/mthv2_svtrv2_rot90_ms_w1024_gpu1/test_predictions_metrics.json` | From scratch; official-style `MultiScaleDataSet`/`MultiScaleSampler`, `max_text_length=64` keeps MTHv2 max-length labels. |

## MMOCR Baseline Comparison (MTHv2-combo)

All rows below are from MMOCR runs on the same MTHv2-combo test set (`10455` samples), converted to micro `CER/AR/CR` with our local converter.

| Framework | Model | Orientation | Split | Samples | CER micro | AR micro | CR micro | recog/1-N.E.D | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| MMOCR | CRNN | `Rot90(k=3)` | test | 10455 | 4.49 | 95.51 | 95.63 | 0.9032 | 0.04 | 1.000 | 29.90 | 18.07 | 14.93 | 12.41 | 2.97 | `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_28.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_metrics.json` |
| MMOCR | SVTR-tiny | `Rot90(k=3)` | test | 10455 | 4.44 | 95.56 | 95.68 | 0.9092 | 0.16 | 0.999 | 26.37 | 18.07 | 13.56 | 10.53 | 3.11 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_metrics.json` |
| MMOCR | SVTR-small | `Rot90(k=3)` | test | 10455 | 4.66 | 95.34 | 95.44 | 0.9027 | 0.04 | 0.999 | 27.80 | 19.62 | 14.82 | 11.48 | 3.21 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530/svtr_small_k3_epoch29_test_metrics.json` |
| MMOCR | SVTR-L | `Rot90(k=3), 48x160` | test | 10455 | 4.84 | 95.16 | 95.26 | 0.9015 | 0.11 | 0.999 | 28.10 | 19.72 | 14.66 | 10.96 | 3.43 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601/svtr_large_k3_officialgeom_epoch29_test_metrics.json` |
| MMOCR | ABINet | `Rot90(k=3), 32x128` | test | 10455 | 9.25 | 90.75 | 90.91 | 0.8620 | 0.00 | 1.000 | 34.56 | 21.17 | 16.56 | 15.31 | 8.00 | `/home/ubuntu/mmocr/work_dirs/mthv2_abinet_k3_full_gpu1/best_recog_1-N.E.D_epoch_19.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_abinet_k3_epoch19_test_0603_gpu/abinet_k3_epoch19_test_metrics.json` |
| MMOCR | ABINet-vision | `Rot90(k=3), 32x128` | test | 10455 | 10.09 | 89.91 | 90.02 | 0.8537 | 0.00 | 1.000 | 34.94 | 22.48 | 17.75 | 16.65 | 8.80 | `/home/ubuntu/mmocr/work_dirs/mthv2_abinet_vision_k3_20e_full_gpu1_0605/best_recog_1-N.E.D_epoch_20.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_abinet_vision_k3_epoch20_test_0605/mthv2_abinet_vision_k3_epoch20_test_metrics.json` |
| MMOCR | MASTER | `Rot90(k=3), 48x160` | test | 10455 | 17.00 | 83.00 | 89.85 | 0.8369 | 0.00 | 1.061 | 32.01 | 25.15 | 29.22 | 27.02 | 15.56 | `/home/ubuntu/mmocr/work_dirs/mthv2_master_k3_full_gpu1_0605/best_recog_1-N.E.D_epoch_12.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_master_k3_epoch12_test_0605/mthv2_master_k3_epoch12_test_metrics.json` |
| MMOCR | SAR | `Rot90(k=3), height=48, width=768` | test | 10455 | 26.80 | 73.20 | 87.65 | 0.7988 | 0.00 | 1.107 | 42.75 | 21.41 | 17.61 | 22.46 | 27.34 | `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_768_20e_fresh_gpu1_0603_2115/best_recog_1-N.E.D_epoch_20.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_sar_k3_768_epoch20_test_0604/sar_k3_epoch20_test_metrics.json` |
| MMOCR | RobustScanner | `Rot90(k=3), 48x160` | test | 10455 | 11.33 | 88.67 | 88.82 | 0.8198 | 0.01 | 0.999 | 46.58 | 26.74 | 24.79 | 20.55 | 9.43 | `/home/ubuntu/mmocr/work_dirs/mthv2_robustscanner_k3_5e_full_gpu1_0605/best_recog_1-N.E.D_epoch_5.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_robustscanner_k3_epoch5_test_0605/mthv2_robustscanner_k3_epoch5_test_metrics.json` |
| MMOCR | CRNN | `Rot90(k=1)` | test | 10455 | 27.26 | 72.74 | 73.81 | 0.6948 | 0.01 | 0.900 | 44.10 | 38.18 | 37.89 | 34.55 | 25.93 | `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_28.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_metrics.json` |
| MMOCR | SVTR-tiny | `Rot90(k=1)` | test | 10455 | 6.58 | 93.42 | 93.52 | 0.8805 | 0.02 | 0.997 | 31.40 | 21.90 | 17.94 | 13.86 | 5.02 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530/svtr_tiny_epoch29_test_metrics.json` |

## MMOCR Pending Conversion

| Model | Orientation | Status | Best val recog/1-N.E.D | Best epoch | Log dir / checkpoint |
| --- | --- | --- | ---: | ---: | --- |
| SAR | vertical config | Training ended, test conversion pending | 0.1863 | 5 | `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300` |

## PaddleOCR Baseline Comparison (HDRC)

Rows below are PaddleOCR/PP-OCR recognition-only runs on the same HDRC test set (`3381` samples), converted with the local PaddleOCR export script to micro `CER/AR/CR`. These are separated from MMOCR because the training code, model implementations, and default recognition heads differ.

| Framework | Model | Orientation | Split | Samples | CER micro | AR micro | CR micro | Paddle acc | 1-N.E.D | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file | Notes |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| PaddleOCR | SVTRv2 | `Rot90(k=3), 48x1024 MultiScaleSampler` | test | 3381 | 35.10 | 64.90 | 66.18 | 55.43 | 0.7594 | 0.21 | 0.810 | 20.54 | 17.24 | 14.93 | 29.24 | 42.39 | `/home/ubuntu/PaddleOCR/output/rec/hdrc_svtrv2_rot90_ms_w1024_gpu1/best_accuracy.pdparams` | `/home/ubuntu/PaddleOCR/output/rec/hdrc_svtrv2_rot90_ms_w1024_gpu1/test_predictions_metrics.json` | From scratch; strong long-line deletion, especially len>=11 (`Pred/GT len 0.736` in that bucket). |

## MMOCR Baseline Comparison (HDRC)

All rows below are from MMOCR runs on the HDRC test set (`3381` samples), converted to micro `CER/AR/CR` with our local converter.

| Framework | Model | Orientation | Split | Samples | CER micro | AR micro | CR micro | recog/1-N.E.D | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| MMOCR | CRNN | `Rot90(k=3)` | test | 3381 | 15.09 | 84.91 | 85.21 | 0.8242 | 0.00 | 0.993 | 23.57 | 25.16 | 11.08 | 13.32 | 14.72 | `/home/ubuntu/mmocr/work_dirs/hdrc_crnn_k3_full_gpu1/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_crnn_k3_best_epoch29_test_0603/hdrc_crnn_k3_epoch29_test_metrics.json` |
| MMOCR | SVTR-tiny | `Rot90(k=3)` | test | 3381 | 16.29 | 83.71 | 83.89 | 0.8649 | 0.00 | 0.997 | 17.04 | 12.10 | 7.64 | 11.52 | 19.10 | `/home/ubuntu/mmocr/work_dirs/hdrc_svtr_tiny_k3_full_gpu1/best_recog_1-N.E.D_epoch_30.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_svtr_tiny_k3_epoch30_test_0603/hdrc_svtr_tiny_k3_epoch30_test_metrics.json` |
| MMOCR | SVTR-L | `Rot90(k=3), 48x160` | test | 3381 | 21.84 | 78.16 | 78.43 | 0.8382 | 0.06 | 0.989 | 17.04 | 13.81 | 9.12 | 14.82 | 26.42 | `/home/ubuntu/mmocr/work_dirs/hdrc_svtr_large_k3_officialgeom_full_gpu1/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_svtr_large_k3_officialgeom_epoch29_test_0603/hdrc_svtr_large_k3_officialgeom_epoch29_test_metrics.json` |
| MMOCR | ABINet | `Rot90(k=3), 32x128` | test | 3381 | 22.39 | 77.61 | 77.84 | 0.8220 | 0.03 | 0.999 | 23.25 | 16.48 | 7.53 | 15.39 | 26.92 | `/home/ubuntu/mmocr/work_dirs/hdrc_abinet_k3_full_gpu1/best_recog_1-N.E.D_epoch_19.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_abinet_k3_epoch19_test_0603/hdrc_abinet_k3_epoch19_test_metrics.json` |
| MMOCR | ABINet-vision | `Rot90(k=3), 32x128` | test | 3381 | 24.57 | 75.43 | 75.67 | 0.8024 | 0.03 | 0.998 | 23.89 | 19.01 | 9.39 | 18.47 | 29.05 | `/home/ubuntu/mmocr/work_dirs/hdrc_abinet_vision_k3_20e_full_gpu1_0605/best_recog_1-N.E.D_epoch_19.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_abinet_vision_k3_epoch19_test_0605/hdrc_abinet_vision_k3_epoch19_test_metrics.json` |
| MMOCR | MASTER | `Rot90(k=3), 48x160` | test | 3381 | 53.71 | 46.29 | 61.52 | 0.7007 | 0.00 | 1.102 | 24.36 | 31.24 | 20.12 | 46.53 | 64.91 | `/home/ubuntu/mmocr/work_dirs/hdrc_master_k3_full_gpu1_0605/best_recog_1-N.E.D_epoch_12.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_master_k3_epoch12_test_0605/hdrc_master_k3_epoch12_test_metrics.json` |
| MMOCR | SAR | `Rot90(k=3), height=48, width=768` | test | 3381 | 29.26 | 70.74 | 73.24 | 0.8235 | 0.00 | 0.951 | 16.24 | 13.05 | 8.67 | 23.18 | 36.42 | `/home/ubuntu/mmocr/work_dirs/hdrc_sar_k3_768_20e_full_gpu1_0604/best_recog_1-N.E.D_epoch_20.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_sar_k3_768_epoch20_test_0604/hdrc_sar_k3_768_epoch20_test_metrics.json` |
| MMOCR | RobustScanner | `Rot90(k=3), 48x160` | test | 3381 | 62.61 | 37.39 | 40.20 | 0.4622 | 0.06 | 0.912 | 43.79 | 54.44 | 47.78 | 65.57 | 66.69 | `/home/ubuntu/mmocr/work_dirs/hdrc_robustscanner_k3_5e_full_gpu1_0605/best_recog_1-N.E.D_epoch_5.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_robustscanner_k3_epoch5_test_0605/hdrc_robustscanner_k3_epoch5_test_metrics.json` |
| MMOCR | RobustScanner-10e | `Rot90(k=3), 48x160` | test | 3381 | 26.41 | 73.59 | 73.98 | 0.7776 | 0.00 | 0.997 | 26.43 | 21.17 | 13.59 | 23.70 | 29.86 | `/home/ubuntu/mmocr/work_dirs/hdrc_robustscanner_k3_10e_full_gpu1_0605/best_recog_1-N.E.D_epoch_10.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_robustscanner_k3_epoch10_test_0605/hdrc_robustscanner_k3_epoch10_test_metrics.json` |


## MMOCR Baseline Comparison (CHDAC)

CHDAC rows below are from MMOCR runs on the CHDAC test set (`4755` samples). CRNN has full micro `CER/AR/CR`; SVTR-Tiny collapsed to near-empty CTC predictions and is kept as a failed-run note rather than a paper-ready metric row.

| Framework | Model | Orientation | Split | Samples | CER micro | AR micro | CR micro | recog/1-N.E.D | Empty pred | Pred/GT len | Checkpoint | Result file |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| MMOCR | CRNN | `Rot90(k=3)` | test | 4755 | 56.85 | 43.15 | 43.47 | 0.4262 | 0.00 | 0.962 | `/home/ubuntu/mmocr/work_dirs/chdac_crnn_k3_full_gpu1_0604/best_recog_1-N.E.D_epoch_30.pth` | `/home/ubuntu/mmocr/work_dirs/eval_chdac_crnn_k3_epoch30_test_0604/chdac_crnn_k3_epoch30_test_metrics.json` |
| MMOCR | ABINet | `Rot90(k=3), 32x128` | test | 4755 | 88.69 | 11.31 | 11.69 | 0.1535 | 0.00 | 0.973 | `/home/ubuntu/mmocr/work_dirs/chdac_abinet_k3_full_gpu1_0604/best_recog_1-N.E.D_epoch_19.pth` | `/home/ubuntu/mmocr/work_dirs/eval_chdac_abinet_k3_epoch19_test_0604/chdac_abinet_k3_epoch19_test_metrics.json` |
| MMOCR | SVTR-Tiny | `Rot90(k=3)` | test | 4755 | failed | failed | failed | 0.0091 | 99%+ diagnostic empty/near-empty predictions | n/a | `/home/ubuntu/mmocr/work_dirs/chdac_svtr_tiny_k3_full_gpu1_0604/best_recog_1-N.E.D_epoch_30.pth` | `/home/ubuntu/mmocr/work_dirs/eval_chdac_svtr_tiny_k3_epoch30_test_0604/best_recog_1-N.E.D_epoch_30.pth_predictions.pkl` |
| MMOCR | SVTR-L | `Rot90(k=3), 48x160 official geom` | test | 4755 | failed | failed | failed | 0.0068 | 99.56% empty predictions | n/a | `/home/ubuntu/mmocr/work_dirs/chdac_svtr_large_k3_officialgeom_full_gpu1_0604/best_recog_1-N.E.D_epoch_23.pth` | `/home/ubuntu/mmocr/work_dirs/eval_chdac_svtr_large_k3_officialgeom_epoch23_test_0604/best_recog_1-N.E.D_epoch_23.pth_predictions.pkl` |

## Append Template

When adding a new dataset, append one clean row and one validation-protocol calibrated bias row to the main table:

| Dataset | Split | Decode | Bias blank/nonblank | Samples | CER micro | AR micro | CR micro | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| NEW_DATASET | test | clean | 0/0 | - | - | - | - | - | - | - | - | - | - | - | `.../checkpoint_best_regular.pth` | `.../ctc_error_summary_test_clean_YYYY.json` |
| NEW_DATASET | test | bias | B/NB | - | - | - | - | - | - | - | - | - | - | - | `.../checkpoint_best_regular.pth` | `.../ctc_error_summary_test_bias_YYYY.json` |
