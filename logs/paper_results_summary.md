# Paper Results Summary

Last updated: 2026-06-03

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
| HDRC | test | clean | 0/0 | 3381 | 10.01 | 89.99 | 90.33 | 2.19 | 0.938 | 12.74 | 9.19 | 5.37 | 8.40 | 11.13 | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_clean_0527.json` |
| HDRC | test | bias | -2.0/0.4 | 3381 | 9.30 | 90.70 | 91.80 | 0.98 | 0.977 | 9.87 | 7.35 | 4.54 | 7.74 | 10.64 | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth` | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_bias_b-20_nb04_0527.json` |

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
| HDRC | valid | clean | 0/0 | 2854 | 13.44 | 86.56 | 86.94 | Checkpoint-selection reference. | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_clean_0527.json` |
| HDRC | valid | bias | -2.0/0.4 | 2854 | 12.32 | 87.68 | 88.71 | Best setting from validation sweep. | `logs/mth1000mth1200pre_hdrcft_full_0527-1732/decode_bias_sweep_valid_0527.json` |

## Current Takeaways

| Item | Observation |
| --- | --- |
| Best MTH1000 test | `bias -1.2/1.0`, AR `95.12`, CR `95.50`, CER `4.88`. |
| Best MTH1200 test | `bias -1.2/1.0`, AR `94.82`, CR `95.00`, CER `5.18`. |
| Best TKH test | `bias -1.6/1.0`, AR `98.96`, CR `99.02`, CER `1.04`. |
| Best MTHv2-combo test | qbudget bias `-2.0/0.8`, AR `96.69`, CR `96.90`, CER `3.31`. |
| Best HDRC test | `bias -2.0/0.4`, AR `90.70`, CR `91.80`, CER `9.30`. |
| Main remaining weakness | MTH1000/MTH1200/MTHv2 short columns and HDRC long columns; qbudget MTHv2-combo `len=1` CER is still `31.56` under clean decoding. |
| Bias effect on MTH1200 | Test CER improves from `5.95` to `5.18`; empty prediction rate improves from `6.75` to `3.80`. |
| Bias effect on TKH | Test CER improves from `1.47` to `1.04`; empty prediction rate stays `0.00`. |
| Bias effect on MTHv2-combo | Test CER improves from `4.47` to `3.90`; empty prediction rate improves from `3.68` to `1.04`. |
| Bias effect on MTHv2-combo-qbudget | Test CER improves from `3.83` to `3.31`; empty prediction rate improves from `2.89` to `0.89`. |
| Bias effect on HDRC | Test CER improves from `10.01` to `9.30`; empty prediction rate improves from `2.19` to `0.98`, mainly by reducing deletions. |

## MMOCR Baseline Comparison (MTHv2-combo)

All rows below are from MMOCR runs on the same MTHv2-combo test set (`10455` samples), converted to micro `CER/AR/CR` with our local converter.

| Framework | Model | Orientation | Split | Samples | CER micro | AR micro | CR micro | recog/1-N.E.D | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| MMOCR | CRNN | `Rot90(k=3)` | test | 10455 | 4.49 | 95.51 | 95.63 | 0.9032 | 0.04 | 1.000 | 29.90 | 18.07 | 14.93 | 12.41 | 2.97 | `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_28.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_metrics.json` |
| MMOCR | SVTR-tiny | `Rot90(k=3)` | test | 10455 | 4.44 | 95.56 | 95.68 | 0.9092 | 0.16 | 0.999 | 26.37 | 18.07 | 13.56 | 10.53 | 3.11 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_metrics.json` |
| MMOCR | SVTR-small | `Rot90(k=3)` | test | 10455 | 4.66 | 95.34 | 95.44 | 0.9027 | 0.04 | 0.999 | 27.80 | 19.62 | 14.82 | 11.48 | 3.21 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530/svtr_small_k3_epoch29_test_metrics.json` |
| MMOCR | SVTR-L | `Rot90(k=3), 48x160` | test | 10455 | 4.84 | 95.16 | 95.26 | 0.9015 | 0.11 | 0.999 | 28.10 | 19.72 | 14.66 | 10.96 | 3.43 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601/svtr_large_k3_officialgeom_epoch29_test_metrics.json` |
| MMOCR | ABINet | `Rot90(k=3), 32x128` | test | 10455 | 9.25 | 90.75 | 90.91 | 0.8620 | 0.00 | 1.000 | 34.56 | 21.17 | 16.56 | 15.31 | 8.00 | `/home/ubuntu/mmocr/work_dirs/mthv2_abinet_k3_full_gpu1/best_recog_1-N.E.D_epoch_19.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_abinet_k3_epoch19_test_0603_gpu/abinet_k3_epoch19_test_metrics.json` |
| MMOCR | CRNN | `Rot90(k=1)` | test | 10455 | 27.26 | 72.74 | 73.81 | 0.6948 | 0.01 | 0.900 | 44.10 | 38.18 | 37.89 | 34.55 | 25.93 | `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_28.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_metrics.json` |
| MMOCR | SVTR-tiny | `Rot90(k=1)` | test | 10455 | 6.58 | 93.42 | 93.52 | 0.8805 | 0.02 | 0.997 | 31.40 | 21.90 | 17.94 | 13.86 | 5.02 | `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530/svtr_tiny_epoch29_test_metrics.json` |

## MMOCR Pending Conversion

| Model | Orientation | Status | Best val recog/1-N.E.D | Best epoch | Log dir / checkpoint |
| --- | --- | --- | ---: | ---: | --- |
| SAR | vertical config | Training ended, test conversion pending | 0.1863 | 5 | `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300` |

## MMOCR Baseline Comparison (HDRC)

All rows below are from MMOCR runs on the HDRC test set (`3381` samples), converted to micro `CER/AR/CR` with our local converter.

| Framework | Model | Orientation | Split | Samples | CER micro | AR micro | CR micro | recog/1-N.E.D | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| MMOCR | CRNN | `Rot90(k=3)` | test | 3381 | 15.09 | 84.91 | 85.21 | 0.8242 | 0.00 | 0.993 | 23.57 | 25.16 | 11.08 | 13.32 | 14.72 | `/home/ubuntu/mmocr/work_dirs/hdrc_crnn_k3_full_gpu1/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_crnn_k3_best_epoch29_test_0603/hdrc_crnn_k3_epoch29_test_metrics.json` |
| MMOCR | SVTR-tiny | `Rot90(k=3)` | test | 3381 | 16.29 | 83.71 | 83.89 | 0.8649 | 0.00 | 0.997 | 17.04 | 12.10 | 7.64 | 11.52 | 19.10 | `/home/ubuntu/mmocr/work_dirs/hdrc_svtr_tiny_k3_full_gpu1/best_recog_1-N.E.D_epoch_30.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_svtr_tiny_k3_epoch30_test_0603/hdrc_svtr_tiny_k3_epoch30_test_metrics.json` |
| MMOCR | SVTR-L | `Rot90(k=3), 48x160` | test | 3381 | 21.84 | 78.16 | 78.43 | 0.8382 | 0.06 | 0.989 | 17.04 | 13.81 | 9.12 | 14.82 | 26.42 | `/home/ubuntu/mmocr/work_dirs/hdrc_svtr_large_k3_officialgeom_full_gpu1/best_recog_1-N.E.D_epoch_29.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_svtr_large_k3_officialgeom_epoch29_test_0603/hdrc_svtr_large_k3_officialgeom_epoch29_test_metrics.json` |
| MMOCR | ABINet | `Rot90(k=3), 32x128` | test | 3381 | 22.39 | 77.61 | 77.84 | 0.8220 | 0.03 | 0.999 | 23.25 | 16.48 | 7.53 | 15.39 | 26.92 | `/home/ubuntu/mmocr/work_dirs/hdrc_abinet_k3_full_gpu1/best_recog_1-N.E.D_epoch_19.pth` | `/home/ubuntu/mmocr/work_dirs/eval_hdrc_abinet_k3_epoch19_test_0603/hdrc_abinet_k3_epoch19_test_metrics.json` |

## Append Template

When adding a new dataset, append one clean row and one validation-selected bias row to the main table:

| Dataset | Split | Decode | Bias blank/nonblank | Samples | CER micro | AR micro | CR micro | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER | Checkpoint | Result file |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| NEW_DATASET | test | clean | 0/0 | - | - | - | - | - | - | - | - | - | - | - | `.../checkpoint_best_regular.pth` | `.../ctc_error_summary_test_clean_YYYY.json` |
| NEW_DATASET | test | bias | B/NB | - | - | - | - | - | - | - | - | - | - | - | `.../checkpoint_best_regular.pth` | `.../ctc_error_summary_test_bias_YYYY.json` |
