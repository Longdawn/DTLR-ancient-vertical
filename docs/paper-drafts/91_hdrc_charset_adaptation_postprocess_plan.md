# HDRC Charset-Adaptation Ablation Postprocess Plan

This note is for Gate D only: random target classifier initialization vs. charset-aware classifier adaptation on HDRC. Do not copy any result into the paper body until the full finetuning run has completed and the clean/calibrated test AR/CR files exist.

## Current State

2026-06-05 update: Gate D postprocess is complete.

- Random-head full finetuning completed:
  - `logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth`
- Required postprocess artifacts now exist:
  - `logs/hdrc_charset_random_full_visible1_0605/micro_valid_clean_0605.json`
  - `logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.json`
  - `logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.json`
  - `logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_b-12_nb10_0605.json`
- Random-head test AR/CR:
  - clean: `81.01 / 81.41`
  - validation-protocol bias `-1.2/1.0`: `82.72 / 83.97`
- Smart charset-aware reference test AR/CR:
  - clean: `89.99 / 90.33`
  - validation-protocol bias `-2.0/0.4`: `90.70 / 91.80`

The remaining commands below are preserved for reproducibility, not as pending actions.

- Smart-mapping reference full run:
  - `logs/mth1000mth1200pre_hdrcft_full_0527-1732`
  - test calibrated result: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_bias_b-20_nb04_0527.json`
- Random-head reconstruction:
  - `logs/hdrc_charset_random_head_visible1_0605`
  - best checkpoint exists: `logs/hdrc_charset_random_head_visible1_0605/checkpoint_best_regular.pth`
- Random-head full finetuning:
  - queued by `hdrc_charset_random_full_wait_0605`
  - expected output dir: `logs/hdrc_charset_random_full_visible1_0605`

## Required Completion Criteria

Gate D is not closed until all files below exist and have the expected split sample counts:

1. `logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth`
2. `logs/hdrc_charset_random_full_visible1_0605/micro_valid_clean_0605.json`
3. `logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.json`
4. `logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.json`
5. `logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_*.json`

Expected sample counts:

- HDRC valid: `2854`
- HDRC test: `3381`

## Clean Valid

Run after `logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth` exists:

```bash
tmux new-session -d -s hdrc_random_full_valid_clean_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth --split val --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/hdrc_charset_random_full_visible1_0605/micro_valid_clean_0605.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6700 > logs/hdrc_charset_random_full_visible1_0605/micro_valid_clean_0605.out 2>&1; echo EXIT:$? >> logs/hdrc_charset_random_full_visible1_0605/micro_valid_clean_0605.out'
```

## Clean Test

```bash
tmux new-session -d -s hdrc_random_full_test_clean_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6700 > logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.out 2>&1; echo EXIT:$? >> logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.out'
```

## Validation Bias Sweep

Use validation only for bias selection.

```bash
tmux new-session -d -s hdrc_random_full_valid_sweep_0605 'cd /home/ubuntu/DTLR && MPLCONFIGDIR=/tmp/matplotlib CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.0 -1.6 -1.2 -0.8 -0.4 0.0 --nonblank_biases 0.0 0.4 0.8 1.0 --ratio_nonblank_biases 0.0 --output_json logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6700 > logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.out 2>&1; echo EXIT:$? >> logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.out'
```

## Test With Selected Bias

Read rank 0 in `decode_bias_sweep_valid_0605.json`, then substitute the selected values below:

```bash
tmux new-session -d -s hdrc_random_full_test_bias_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_charset_random_full_visible1_0605/checkpoint_best_regular.pth --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --blank_bias BLANK --nonblank_bias NONBLANK --output_json logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_SELECTED_0605.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6700 > logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_SELECTED_0605.out 2>&1; echo EXIT:$? >> logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_SELECTED_0605.out'
```

## Paper Update Rule

After clean and calibrated test results exist:

1. Compare random-head full test AR/CR against smart-mapping HDRC full test AR/CR.
2. Update `logs/paper_results_summary.md` and `logs/paper_results_summary.csv`.
3. Update `docs/paper-drafts/97_experiment_evidence_inventory.md`.
4. Only then add a charset-adaptation ablation table to `docs/paper-drafts/05_results_analysis.md`.

If random-head performs similarly to smart mapping, downgrade the classifier-adaptation claim to an implementation convenience rather than a strong contribution.
