# Experiment Postprocess Workflow

This workflow converts a finished CTC finetuning experiment into paper-ready rows.

Scope: single-column / line-level recognition only. Do not use this workflow for page-level layout analysis.

## Non-Negotiable Checks

- Use `checkpoint_best_regular.pth`, not the final checkpoint, unless explicitly justified.
- Do not start a new evaluation before checking GPU processes and existing output files.
- Long validation/test runs should run in `tmux`.
- A result is incomplete until it has CER/AR/CR, empty prediction rate, Pred/GT length ratio, and length buckets.
- Decode bias must be selected on validation, then applied once to test.

## 1. Check State First

```bash
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
ls -lh logs/RUN_DIR/*clean*.json logs/RUN_DIR/*bias*.json logs/RUN_DIR/*sweep*.json 2>/dev/null
```

If the expected JSON already exists and has the full sample count, do not rerun it.

## 2. Clean Valid

```bash
tmux new-session -d -s EVAL_VALID_CLEAN 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c CONFIG.py --dataset_file DATASET --checkpoint CHECKPOINT --split val --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/RUN_DIR/micro_valid_clean_YYYY.json --options num_classes=NUM_CLASSES > logs/RUN_DIR/micro_valid_clean_YYYY.out 2>&1; echo EXIT:$? >> logs/RUN_DIR/micro_valid_clean_YYYY.out'
```

## 3. Clean Test

```bash
tmux new-session -d -s EVAL_TEST_CLEAN 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c CONFIG.py --dataset_file DATASET --checkpoint CHECKPOINT --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/RUN_DIR/micro_test_clean_YYYY.json --options num_classes=NUM_CLASSES > logs/RUN_DIR/micro_test_clean_YYYY.out 2>&1; echo EXIT:$? >> logs/RUN_DIR/micro_test_clean_YYYY.out'
```

## 4. Validation Bias Sweep

Use the same validation split used for selection. For MTHv2-combo, the current standard grid is:

```bash
tmux new-session -d -s EVAL_VALID_SWEEP 'cd /home/ubuntu/DTLR && MPLCONFIGDIR=/tmp/matplotlib CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c CONFIG.py --dataset_file DATASET --checkpoint CHECKPOINT --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.0 -1.6 -1.2 -0.8 -0.4 0.0 --nonblank_biases 0.0 0.4 0.8 1.0 --ratio_nonblank_biases 0.0 --output_json logs/RUN_DIR/decode_bias_sweep_valid_YYYY.json --options num_classes=NUM_CLASSES > logs/RUN_DIR/decode_bias_sweep_valid_YYYY.out 2>&1; echo EXIT:$? >> logs/RUN_DIR/decode_bias_sweep_valid_YYYY.out'
```

The sweep JSON is sorted by `cer_micro`. Use rank 0 as the validation-selected setting unless there is a documented tie-break reason.

## 5. Test Bias

Apply the validation-selected bias to test:

```bash
tmux new-session -d -s EVAL_TEST_BIAS 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c CONFIG.py --dataset_file DATASET --checkpoint CHECKPOINT --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --blank_bias BLANK --nonblank_bias NONBLANK --output_json logs/RUN_DIR/micro_test_bias_TAG_YYYY.json --options num_classes=NUM_CLASSES > logs/RUN_DIR/micro_test_bias_TAG_YYYY.out 2>&1; echo EXIT:$? >> logs/RUN_DIR/micro_test_bias_TAG_YYYY.out'
```

## 6. Format Table Rows

Use `tools/format_ctc_result_row.py` to avoid manual CER/AR/CR conversion mistakes.

Main test table row:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python tools/format_ctc_result_row.py --table main-md --input_json RESULT.json --dataset DATASET_NAME --split test --decode bias --blank_bias BLANK --nonblank_bias NONBLANK --checkpoint CHECKPOINT
```

Validation selection row:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python tools/format_ctc_result_row.py --table selection-md --input_json SWEEP.json --dataset DATASET_NAME --split valid --decode bias --blank_bias BLANK --nonblank_bias NONBLANK --checkpoint CHECKPOINT --notes "Best setting from validation sweep."
```

CSV row:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python tools/format_ctc_result_row.py --table csv --input_json RESULT.json --dataset DATASET_NAME --split test --decode bias --blank_bias BLANK --nonblank_bias NONBLANK --checkpoint CHECKPOINT
```

Append the generated rows to:

- `logs/paper_results_summary.md`
- `logs/paper_results_summary.csv`
- the run-specific analysis note under `experiments/notes/`
- `experiments/notes/goal_status.md` only for completion or major result updates

## 7. QBudget MTHv2 Example

Selected validation bias:

```text
blank=-2.0, nonblank=0.8
```

Current result files:

```text
logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_valid_clean_0603.json
logs/mthv2_qbudgetstage1pre_mthv2_full_0603/decode_bias_sweep_valid_0603.json
logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_clean_0603.json
logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_bias_b-20_nb08_0603.json
```

Final test-bias metrics:

```text
CER 3.31, AR 96.69, CR 96.90, empty 0.89, Pred/GT 0.997
```
