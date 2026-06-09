# Structure-Learning Ablation Plan

Purpose: close Gate C for ICDAR / CCF-B readiness by testing whether character-box-supervised query structure learning contributes beyond line-level CTC training.

## Current Evidence Status

No paper-ready no-structure ablation was found in the current logs.

2026-06-05 03:01 update:

- The recommended no-structure control has started and writes to `logs/mthv2_no_structure_ctc_full_0605`.
- Process PID `1148725` is running `finetuning.py` on GPU0.
- The run is still in epoch 0 and has not produced validation or test AR/CR.
- This run intentionally omits localization-supervised query learning and should be interpreted as a conservative lower-bound no-localization control. If it is very weak, the paper should not overstate the magnitude as the isolated effect of character boxes alone; it should say the comparison is against a line-level CTC model trained without character-box localization supervision under the current budget.

2026-06-05 09:39 update:

- The run has completed multiple validation epochs and remains active as PID `1148725`.
- Validation behavior is weak so far: epoch 0 `cer_oracle_direction=83.197218`, and epochs 1--10 are near `1.0` CER with blank-heavy predictions.
- Do not enter this run into the paper table until final clean/test and validation-protocol bias results are generated.
- If the final result remains weak, write it as a conservative no-structure lower-bound control rather than a pure estimate of the causal effect of character boxes.

2026-06-06 clean-postprocess update:

- Training has finished and `checkpoint_best_regular.pth` exists.
- Clean validation postprocess completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_valid_clean_0606.json`
  - samples: `10948`
  - CER/AR/CR micro: `99.9943 / 0.0057 / 0.0057`
  - empty prediction rate: `99.9635`
- Clean test postprocess completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0606.json`
  - samples: `10455`
  - CER/AR/CR micro: `99.9981 / 0.0019 / 0.0019`
  - empty prediction rate: `99.9713`
- At this checkpoint, validation decode-bias sweep had started as `logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0606.out`; it was completed in the final-postprocess update below.
- The clean result confirms severe blank-collapse. Keep the paper interpretation conservative: this is a no-localization lower-bound control under the current training budget, not a pure causal estimate of the full character-box supervision effect.

2026-06-06 final-postprocess update:

- Validation decode-bias sweep completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0606.json`
  - selected bias: `blank=-2.0`, `nonblank=0.4`
  - valid CER/AR/CR: `99.8631 / 0.1369 / 0.3654`
- Fixed-bias test completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_b-20_nb04_0606.json`
  - test CER/AR/CR: `99.8859 / 0.1141 / 0.1562`
  - empty prediction rate: `98.7757`
- Gate C is complete for MTHv2 as a conservative no-localization lower-bound control. The result remains far below SAQT even after validation-protocol blank/nonblank calibration.

Existing MTHv2 runs:

- `logs/mthv2_mth1000mth1200tkh_full_0528-0957`: downstream full-model recognition training from a localization-supervised query checkpoint, without query budget.
- `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`: downstream full-model recognition training from a query-budget localization-supervised query checkpoint.
- These runs support query-budget analysis, not the core "with vs without character-box structure learning" claim.

Existing HDRC runs:

- `logs/mth1000mth1200pre_hdrcft_full_0527-1732`: smart charset adaptation from the trusted localization-supervised query checkpoint.
- `logs/hdrc_charset_random_full_visible1_0605`: completed random-head charset adaptation control.
- These runs support charset adaptation, not a no-structure control.

## Minimum Acceptable Ablation

Run at least one no-structure control on MTHv2:

- Same architecture family as SAQT.
- No character-box localization-supervised query learning.
- Train only with line-level CTC supervision.
- Evaluate using the same final protocol:
  - clean valid/test AR/CR
  - validation decode-bias sweep
  - test AR/CR with validation-protocol bias

The paper table should compare:

| Setting | Structure supervision | Recognition supervision | Decode | Test AR | Test CR |
| --- | --- | --- | --- | ---: | ---: |
| No-structure CTC control | none | line-level CTC | clean/bias | TBD | TBD |
| SAQT | character boxes during structure learning | line-level CTC | clean/bias | 96.17/96.69 | 96.29/96.90 |

## Recommended First Run: MTHv2 No-Structure CTC

Use this as the first Gate C experiment after a GPU becomes available. Because no character-box localization-supervised query learning is used, this is a conservative control; if it is too weak, report it as a lower-bound no-localization baseline and consider a longer training budget.

Launch command:

```bash
tmux new-session -d -s mthv2_no_structure_ctc_full_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --new_class_embedding --save_log --output_dir logs/mthv2_no_structure_ctc_full_0605 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-4 epochs=12 eval_epoch=1 max_iterations=10000'
```

Important:

- Do not launch this while GPU1 is occupied by `logs/hdrc_charset_random_head_visible1_0605`.
- If using physical GPU1, keep `CUDA_VISIBLE_DEVICES=1 --device cuda:0` to avoid the direct `cuda:1` MSDA issue observed on 2026-06-05.
- This run intentionally omits `--resume`, `--pretrain_model_path`, `--smart_mapping`, and `--path_old_charset`.

## Postprocess Requirements

After the run finishes, follow `docs/EXPERIMENT_POSTPROCESS.md`:

1. Evaluate clean valid.
2. Evaluate clean test.
3. Run validation decode-bias sweep.
4. Apply selected bias to test.
5. Format rows with `tools/format_ctc_result_row.py`.
6. Update:
   - `logs/paper_results_summary.md`
   - `logs/paper_results_summary.csv`
   - `docs/paper-drafts/97_experiment_evidence_inventory.md`
   - `docs/paper-drafts/05_results_analysis.md`

Concrete commands for the current run are below. Run these only after
`logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth` exists and
the training process has exited.

Expected sample counts:

- MTHv2 valid: `10948`
- MTHv2 test: `10455`

Clean validation:

```bash
tmux new-session -d -s mthv2_nostruct_valid_clean_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth --split val --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/mthv2_no_structure_ctc_full_0605/micro_valid_clean_0605.json --options num_classes=6727 > logs/mthv2_no_structure_ctc_full_0605/micro_valid_clean_0605.out 2>&1; echo EXIT:$? >> logs/mthv2_no_structure_ctc_full_0605/micro_valid_clean_0605.out'
```

Clean test:

```bash
tmux new-session -d -s mthv2_nostruct_test_clean_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0605.json --options num_classes=6727 > logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0605.out 2>&1; echo EXIT:$? >> logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0605.out'
```

Validation decode-bias sweep:

```bash
tmux new-session -d -s mthv2_nostruct_valid_sweep_0605 'cd /home/ubuntu/DTLR && MPLCONFIGDIR=/tmp/matplotlib CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.0 -1.6 -1.2 -0.8 -0.4 0.0 --nonblank_biases 0.0 0.4 0.8 1.0 --ratio_nonblank_biases 0.0 --output_json logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0605.json --options num_classes=6727 > logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0605.out 2>&1; echo EXIT:$? >> logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0605.out'
```

Then read the rank-0 blank/nonblank values from
`decode_bias_sweep_valid_0605.json` and apply them to test:

```bash
tmux new-session -d -s mthv2_nostruct_test_bias_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --blank_bias BLANK --nonblank_bias NONBLANK --output_json logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_SELECTED_0605.json --options num_classes=6727 > logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_SELECTED_0605.out 2>&1; echo EXIT:$? >> logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_SELECTED_0605.out'
```

## Interpretation Rules

- If no-structure CTC is substantially worse than SAQT, the result supports the value of structure learning under the current training budget.
- If no-structure CTC is close to SAQT, the paper should weaken the structure-learning claim and emphasize the framework/integration rather than structure supervision as the main source of improvement.
- If no-structure CTC fails to train, do not hide it. Record the failure as protocol evidence, then consider a longer or staged no-structure baseline.

## Optional Stronger Follow-up

If time permits, repeat on HDRC:

- no-structure CTC on HDRC under the same final evaluation protocol.
- Compare against `logs/mth1000mth1200pre_hdrcft_full_0527-1732`.

This would make Gate C substantially stronger, but MTHv2 alone is the minimum needed to stop the core method claim from being unsupported.
