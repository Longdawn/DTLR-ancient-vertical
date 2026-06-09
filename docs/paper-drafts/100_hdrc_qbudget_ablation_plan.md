# HDRC QBudget-Localization Query Variant Plan

Date: 2026-06-07

## Purpose

The current paper draft has MTHv2 evidence for query activation budget, but not HDRC evidence. If query budget remains a named method component, the strongest next experiment is an HDRC-side qbudget-localization query variant under the final AR/CR protocol.

This plan is intentionally conservative. It should not be reported as a clean causal estimate unless the compared checkpoints differ only by the query-budget regularizer. If the qbudget candidate also uses extra MTHv2 localization-supervised query learning, the paper must state the comparison as a qbudget-localization-query variant rather than an isolated qbudget ablation.

## Current Evidence

### Existing HDRC Reference

- Head reconstruction:
  - `logs/mth1000mth1200pre_hdrcft_head_0527-1530/checkpoint_best_regular.pth`
  - source localization checkpoint: `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`
  - command source: `logs/mth1000mth1200pre_hdrcft_head_0527-1530/info.txt`
- Full-model recognition training:
  - `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth`
  - clean test AR/CR: `89.99 / 90.33`
  - validation-fixed bias test AR/CR: `90.70 / 91.80`

### Existing QBudget Localization Checkpoint

- `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/checkpoint.pth`
- charset:
  - `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl`
- source:
  - continued from `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`
  - trained on MTHv2-combo character boxes with `config/MTHV2_stage1_query_budget.py`

Important caveat: this checkpoint differs from the HDRC reference not only by query-budget regularization, but also by an additional MTHv2-combo localization-supervised query learning stage. It is useful as a qbudget-localization-query candidate, but not as a perfectly matched single-factor qbudget ablation.

## Minimum Executable Experiment

### Stage A: HDRC Head Reconstruction From QBudget Localization Checkpoint

Run only after GPU0 is free. Do not use GPU1.

```bash
tmux new-session -d -s hdrc_qbudget_head_0607 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth1000 --num_workers 0 --resume logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/checkpoint.pth --new_class_embedding --smart_mapping --path_old_charset logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl --save_log --output_dir logs/hdrc_qbudget_head_0607 -c config/MTH1000_dtlr.py --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6727 batch_size=2 lr=1e-4 epochs=3 eval_epoch=1 max_iterations=10000'
```

Decision rule after Stage A:

- If best validation CER is clearly worse than the existing HDRC head-reconstruction reference (`logs/mth1000mth1200pre_hdrcft_head_0527-1530`, final-protocol clean valid CER `20.56`), do not spend a full-model recognition slot.
- If it is close or better, continue to Stage B.

### Stage B: HDRC Full-Model Recognition Training

```bash
tmux new-session -d -s hdrc_qbudget_full_0607 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth1000 --num_workers 0 --resume logs/hdrc_qbudget_head_0607/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl --save_log --output_dir logs/hdrc_qbudget_full_0607 -c config/MTH1000_dtlr.py --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000'
```

Current status:

- 2026-06-07 04:12 check: `logs/hdrc_qbudget_full_0607/log.txt` still contains only epoch 0 and epoch 1 validation records. Epoch 1 clean valid CER is `9.60%`.
- `logs/hdrc_qbudget_full_0607/info.txt` is still updating in epoch 2 around step `4720/12142`; GPU0 remains highly occupied. Do not launch postprocess yet.
- 2026-06-07 04:17 check: epoch 2 validation finished with clean valid CER `15.42%`, marked "not best"; the best checkpoint remains epoch 1 with clean valid CER `9.60%`. Training has continued into epoch 3.
- 2026-06-07 04:36 check: epoch 3 is still training around step `4170/12142`; GPU0 remains highly occupied by the full run. No final clean/test or calibration JSON exists.
- 2026-06-07 04:38 check: epoch 3 is still training around step `4630/12142`; `checkpoint_best_regular.pth` remains from epoch 1 and no postprocess output exists.
- 2026-06-07 05:04 check: the run was early-stopped after epoch 2/3 validation regression, and `FORCE_POSTPROCESS=1` was used on the epoch-1 best checkpoint. Final postprocess completed successfully.
- Clean test AR/CR: `91.50 / 91.64`.
- Development-set calibrated test AR/CR: `93.44 / 94.36` with bias `blank=-2.0`, `nonblank=1.0`.
- Paper-safe interpretation: this is useful qbudget-localization-query variant evidence, not a pure query-budget causal ablation.

### Stage C: Final AR/CR Postprocess

Use `docs/EXPERIMENT_POSTPROCESS.md` exactly:

1. clean validation
2. clean test
3. validation decode-bias sweep
4. fixed-bias test using bias determined by the validation calibration protocol
5. table row formatting

Required output files:

- `logs/hdrc_qbudget_full_0607/micro_valid_clean_0607.json`
- `logs/hdrc_qbudget_full_0607/micro_test_clean_0607.json`
- `logs/hdrc_qbudget_full_0607/decode_bias_sweep_valid_0607.json`
- `logs/hdrc_qbudget_full_0607/micro_test_bias_*_0607.json`

Prepared sequential script:

- `logs/hdrc_qbudget_full_0607/run_postprocess_after_finish_0607.sh`
- This script checks that `checkpoint_best_regular.pth` exists and exits if the same full-model recognition run is still active.
- It also requires `log.txt` to contain epoch 11 before running. To postprocess an early best checkpoint deliberately, launch with `FORCE_POSTPROCESS=1`.
- Launch it only after full-model recognition training finishes and GPU0 is free:

```bash
tmux new-session -d -s hdrc_qbudget_full_postprocess_0607 'cd /home/ubuntu/DTLR && bash logs/hdrc_qbudget_full_0607/run_postprocess_after_finish_0607.sh'
```

Do not start the commands below until full-model recognition training has finished and GPU0 is free. All commands intentionally use GPU0 only.

Clean validation:

```bash
tmux new-session -d -s hdrc_qbudget_full_valid_clean_0607 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_qbudget_full_0607/checkpoint_best_regular.pth --split val --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/hdrc_qbudget_full_0607/micro_valid_clean_0607.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6727 > logs/hdrc_qbudget_full_0607/micro_valid_clean_0607.out 2>&1; echo EXIT:$? >> logs/hdrc_qbudget_full_0607/micro_valid_clean_0607.out'
```

Clean test:

```bash
tmux new-session -d -s hdrc_qbudget_full_test_clean_0607 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_qbudget_full_0607/checkpoint_best_regular.pth --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --output_json logs/hdrc_qbudget_full_0607/micro_test_clean_0607.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6727 > logs/hdrc_qbudget_full_0607/micro_test_clean_0607.out 2>&1; echo EXIT:$? >> logs/hdrc_qbudget_full_0607/micro_test_clean_0607.out'
```

Validation calibration sweep:

```bash
tmux new-session -d -s hdrc_qbudget_full_valid_sweep_0607 'cd /home/ubuntu/DTLR && MPLCONFIGDIR=/tmp/matplotlib CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_qbudget_full_0607/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.0 -1.6 -1.2 -0.8 -0.4 0.0 --nonblank_biases 0.0 0.4 0.8 1.0 --ratio_nonblank_biases 0.0 --output_json logs/hdrc_qbudget_full_0607/decode_bias_sweep_valid_0607.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6727 > logs/hdrc_qbudget_full_0607/decode_bias_sweep_valid_0607.out 2>&1; echo EXIT:$? >> logs/hdrc_qbudget_full_0607/decode_bias_sweep_valid_0607.out'
```

After the sweep finishes, read rank 0 from `decode_bias_sweep_valid_0607.json` and apply that fixed bias to test:

```bash
tmux new-session -d -s hdrc_qbudget_full_test_bias_0607 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_ctc_micro_batch.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/hdrc_qbudget_full_0607/checkpoint_best_regular.pth --split test --device cuda:0 --batch_size 2 --num_workers 0 --new_class_embedding --blank_bias BLANK --nonblank_bias NONBLANK --output_json logs/hdrc_qbudget_full_0607/micro_test_bias_SELECTED_0607.json --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6727 > logs/hdrc_qbudget_full_0607/micro_test_bias_SELECTED_0607.out 2>&1; echo EXIT:$? >> logs/hdrc_qbudget_full_0607/micro_test_bias_SELECTED_0607.out'
```

## Paper Interpretation

If the qbudget HDRC run improves over the existing HDRC reference:

- Safe wording: "the qbudget-localization query variant also improves HDRC under the same downstream protocol."
- Unsafe wording: "query budget alone causes the HDRC improvement."

If it is similar:

- Keep the current paper wording: MTHv2 provides internal evidence for query budget; HDRC supports charset adaptation and full-model recognition training.

If it is worse:

- Do not include it in the main paper body.
- Mention only internally that the MTHv2 qbudget-localization representation does not automatically adapt to HDRC.

## Priority

This experiment is higher priority than adding a new backbone. It directly addresses the current paper's evidence gap and is cheaper to interpret than a broad architecture change.
