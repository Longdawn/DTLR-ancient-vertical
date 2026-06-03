# MTHv2 Query-Budget Full Finetune Analysis - 2026-06-03

## Run

- Experiment type: MTHv2-combo CTC full finetuning.
- Run directory: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- Best checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth`
- Final checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint.pth`
- Source head checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth`
- Source charset: `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl`
- Config: `config/MTHV2_dtlr.py`
- Dataset: `mth_combo`
- Key options: `num_classes=6727`, `batch_size=2`, `lr=1e-5`, `epochs=12`, `eval_epoch=1`, `max_iterations=10000`

## Validation Trajectory

| Epoch | Valid CER | Valid WER | Blank Pred Ratio | Train Loss | Test Loss |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.1182255793 | 0.3238549867 | 0.9894890109 | 0.4165442377 | 0.6589849504 |
| 1 | 0.1204471793 | 0.3277818143 | 0.9895275773 | 0.3710252590 | 0.6593003285 |
| 2 | 0.1083469574 | 0.3099726254 | 0.9894920558 | 0.3359842271 | 0.6120596847 |
| 3 | 0.1071132880 | 0.3081968064 | 0.9894881990 | 0.3212273773 | 0.5875849402 |
| 4 | 0.1076776368 | 0.2993907148 | 0.9894994643 | 0.3262324999 | 0.5790698769 |
| 5 | 0.1024624169 | 0.2959016314 | 0.9894520683 | 0.3112832069 | 0.5620321763 |
| 6 | 0.1035924233 | 0.3013889350 | 0.9895085986 | 0.3249393241 | 0.5710714577 |
| 7 | **0.1012771647** | 0.2983906013 | 0.9894674948 | 0.3068085942 | 0.5589902558 |
| 8 | 0.1468992922 | 0.5482284712 | 0.9900830375 | 0.3923331214 | 0.9629305144 |
| 9 | 0.3068244874 | 0.7257204166 | 0.9916077253 | 2.0086135004 | 1.8935349686 |
| 10 | 0.2213739720 | 0.6932814628 | 0.9902892679 | 1.2066647028 | 1.2859759517 |
| 11 | 0.1841722468 | 0.6326822527 | 0.9899766773 | 0.8238531037 | 1.0405412936 |

## Baseline Comparison

Trusted MTHv2 full baseline:

- Run: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- Best valid CER: `0.11397798822246911`
- Best epoch: `9`
- Best checkpoint: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`

Full-MTHv2 stage-1 candidate:

- Run: `logs/mthv2_fullstage1pre_mthv2_full_tmux_0601`
- Best valid CER: `0.13439168210258723`
- Best epoch: `2`

Query-budget full finetune:

- Best valid CER: `0.10127716468336462`
- Best epoch: `7`

Improvements:

- Over trusted MTH1000+MTH1200-pretrained MTHv2 full baseline: `0.0127008235` absolute CER, about `11.1%` relative reduction.
- Over full-MTHv2 stage-1 candidate: `0.0331145174` absolute CER, about `24.6%` relative reduction.

## Interpretation

This result is clearly useful by validation CER. The query-budget branch did not beat the old head-reconstruction baseline by itself, but after full finetuning it becomes the strongest observed MTHv2-combo validation run so far. This means head-reconstruction CER alone was not sufficient to reject the branch; the query-budget stage-1 representation appears to support a better full-finetuning trajectory.

The improvement is not explained by a large change in blank prediction ratio, which stays near `0.9895` around the best epochs. The next analysis must inspect clean/bias CER, empty prediction rate, pred/GT length ratio, and length buckets to determine whether gains come from short columns, long columns, or general substitution/deletion reduction.

There is clear late-epoch instability. The run is stable and improving through epoch 7, then degrades sharply from epoch 8 onward. The final checkpoint should not be used. All downstream evaluation must use `checkpoint_best_regular.pth`.

## Decision

- Status: clearly useful validation result.
- Replacement mainline: strong candidate. Test clean now beats the old MTHv2 bias result by CER, but validation bias sweep and test-bias metrics are still needed before final mainline replacement.
- Use for paper: yes as a strong candidate result. It is useful evidence that query-budget fixes the full-MTHv2 over-activation branch at downstream full-finetune level.

## Test Clean Metrics

Result file: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_clean_0603.json`

| Split | Decode | Samples | CER micro | AR micro | CR micro | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| test | clean | 10455 | 3.83 | 96.17 | 96.29 | 2.89 | 0.982 | 31.56 | 23.16 | 17.92 | 11.62 | 1.98 |

Compared with the old MTHv2 full baseline:

- Old clean test CER: `4.47`; qbudget clean test CER: `3.83`; absolute reduction `0.64` percentage points.
- Old bias test CER: `3.90`; qbudget clean test CER: `3.83`; qbudget clean is already slightly better by CER.
- Old bias CR is still slightly higher: `96.37` vs qbudget clean `96.29`.
- Empty prediction rate improves over old clean: `3.68` -> `2.89`, but is worse than old bias `1.04`.

## Valid Clean Metrics

Result file: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_valid_clean_0603.json`

| Split | Decode | Samples | CER micro | AR micro | CR micro | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | clean | 10948 | 4.37 | 95.63 | 95.75 | 2.67 | 0.980 | 23.89 | 20.13 | 16.65 | 11.03 | 2.63 |

Compared with the old MTHv2 validation baseline:

- Old clean valid CER: `5.20`; qbudget clean valid CER: `4.37`; absolute reduction `0.83` percentage points.
- Old bias valid CER: `4.56`; qbudget clean valid CER: `4.37`; qbudget clean is already better by CER.
- Old bias valid CR is still slightly higher: `95.82` vs qbudget clean `95.75`.
- Short-column behavior is better than qbudget test on len=1/len=2, but still remains the main weakness: valid len=1 CER `23.89`, len=2 CER `20.13`.

## Valid Bias Selection

Result file: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/decode_bias_sweep_valid_0603.json`

Best validation setting: `blank=-2.0`, `nonblank=0.8`, `ratio=0.0`.

| Split | Decode | Samples | CER micro | AR micro | CR micro | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | bias -2.0/0.8 | 10948 | 3.76 | 96.24 | 96.45 | 0.56 | 0.997 | 21.03 | 17.29 | 13.93 | 9.54 | 2.27 |

## Test Bias Metrics

Result file: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_bias_b-20_nb08_0603.json`

| Split | Decode | Samples | CER micro | AR micro | CR micro | Empty pred | Pred/GT len | Len=1 CER | Len=2 CER | Len=3-5 CER | Len=6-10 CER | Len>=11 CER |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| test | bias -2.0/0.8 | 10455 | 3.31 | 96.69 | 96.90 | 0.89 | 0.997 | 27.95 | 19.48 | 14.86 | 10.46 | 1.72 |

Compared with the old MTHv2 full baseline:

- Old bias test CER: `3.90`; qbudget bias test CER: `3.31`; absolute reduction `0.59` percentage points.
- Old bias test CR: `96.37`; qbudget bias test CR: `96.90`; absolute improvement `0.53` percentage points.
- Empty prediction rate improves over old bias: `1.04` -> `0.89`.
- Short columns still dominate the remaining errors, but qbudget bias improves len=1/len=2 over qbudget clean: len=1 `31.56` -> `27.95`, len=2 `23.16` -> `19.48`.

## Required Next Steps

1. Use qbudget bias `-2.0/0.8` as the current MTHv2-combo main result.
2. If time allows, run a narrower sweep around `blank=-2.0`, `nonblank=0.8` only if we want to squeeze marginal gains; otherwise stop here for the paper table.
