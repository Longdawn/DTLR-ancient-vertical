# MTHv2/HDRC Goal Status

Last updated: 2026-06-03 22:53 Asia/Shanghai

## Resume Rule

On resume, read this file first, then inspect the latest log directory listed below before continuing. Do not restart from scratch.

## Completed

- Read current repo state, existing configs, DTLR code paths, and relevant logs.
- Created the required plan note:
  - `experiments/notes/goal_plan_mthv2_hdrc.md`
- Added Module 1 target experiment configs:
  - `config/MTHV2_dtlr_sgq_short_ce.py`
  - `config/HDRC_dtlr_sgq_short_ce.py`
- Added SGQ config tests to:
  - `tests/test_sgq_short_query_loss.py`
- Verified SGQ unit/config smoke:
  - command: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_sgq_short_query_loss.py`
  - result: `Ran 5 tests ... OK`
- Attempted first MTHv2 runtime smoke:
  - log dir: `logs/mthv2_sgq_short_ce_smoke_0528-2237`
  - result: stopped because `--new_class_embedding` reset `start_epoch=0` and entered full validation before the capped training step.
- Completed corrected one-step MTHv2 runtime smoke:
  - log dir: `logs/mthv2_sgq_short_ce_train_smoke_0528-2238`
  - command used `--pretrain_model_path ...checkpoint_best_regular.pth`, `num_classes=6727`, `start_epoch=1`, `epochs=2`, `eval_epoch=999`, `max_optimizer_steps=1`
  - result: exited with code `0`, printed `Reached max_optimizer_steps=1 at epoch 1`
- Confirmed detached `nohup`/`setsid` jobs do not survive in this environment; full training must be kept as a managed foreground session.

## Modified Files

- `models/dino/dino.py`
  - already had uncommitted SGQ/prototype code when this turn started; current Module 1 uses SGQ short-query CE only.
- `tests/test_sgq_short_query_loss.py`
  - added MTHv2/HDRC SGQ config smoke tests.
- `config/MTHV2_dtlr_sgq_short_ce.py`
  - new experiment-only MTHv2 SGQ config.
- `config/HDRC_dtlr_sgq_short_ce.py`
  - new experiment-only HDRC SGQ config.
- `experiments/notes/goal_plan_mthv2_hdrc.md`
  - new goal plan and baseline summary.
- `experiments/notes/goal_status.md`
  - this resume/status file.

## Current Training

Status: running in managed foreground session.

Dataset: MTHv2 only (`dataset_file=mth_combo`).

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Latest observed training output:

- epoch `0` started.
- `loss_short_gt_ce` appears in metrics, so SGQ module is active.
- epoch `0` training segment reached step `4990/42088` at `2026-05-28 22:58:23` and then entered validation.
- latest observed validation progress before this status write: `Test: [750/10948]` at `2026-05-28 22:59:22`.
- `info.txt` has not been modified since `2026-05-28 22:59:22`.
- as of `2026-05-28 23:09:23`, PID `3408112` is still alive, but `ps -o ... wchan` shows it blocked in `pipe_write`; GPU utilization is `0%`.
- interpretation: the previous managed tool session was interrupted and its stdout pipe is no longer being drained, so the process is blocked while trying to print validation progress. It still holds about `20894 MiB` on GPU0.
- recovery action:
  - temporary `timeout 120 cat` drains were started for parent pipe fds `59` and `62`, writing to `recovered_stdout.log` and `recovered_stderr.log`.
  - the process recovered from `pipe_write` and validation resumed.
  - `gdb` fd redirection was attempted but failed due ptrace policy, so persistent drain readers were started in tmux:
    - `mthv2_sgq_stdout_drain_0528`
    - `mthv2_sgq_stderr_drain_0528`
  - latest observed validation progress after recovery: `Test: [8050/10948]` at `2026-05-28 23:18:55`.
  - `recovered_stdout_tmux.log` is growing, confirming the persistent stdout drain is active.
- epoch `0` validation completed and `log.txt` has been written:
  - epoch time: `0:41:30`
  - `test_cer_oracle_direction`: `0.12700862404436544`
  - `test_wer_oracle_direction`: `0.3670523743094075`
  - `test_blank_pred_ratio_unscaled`: `0.9895538636964736`
  - `test_loss_CTC`: `0.7515765839801588`
  - checkpoint files written:
    - `logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint.pth`
    - `logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth`
- epoch `1` training segment completed and validation is running.
- latest observed validation progress: `Test: [5920/10948]` at `2026-05-28 23:47:30`.
- `log.txt` still has only the epoch `0` row; no epoch `1` CER has been written yet.
- process state at `2026-05-28 23:47`: PID `3408112` is running (`Rsl`), not blocked; `recovered_stdout_tmux.log` and `info.txt` are both still growing.
- external process check:
  - PID `3408112` is running `/home/ubuntu/miniconda3/envs/DTLR/bin/python`.
  - GPU0 is active at about `88%` utilization and `20908/24576 MiB` memory.
  - GPU compute-app memory for PID `3408112`: `20894 MiB`.
- latest files in `logs/mthv2_sgq_short_ce_full_0528-2240`:
  - `config_args_all.json`
  - `config_args_raw.json`
  - `config_cfg.py`
  - `epoch_0/`
  - `info.txt`
  - no `log.txt` yet.

## Latest Baselines To Compare

MTHv2 baseline:

- full run: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- checkpoint: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`
- clean valid summary: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_valid_clean_0528.json`
- best valid decode-bias sweep: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/decode_bias_sweep_valid_0528.json`

HDRC baseline:

- full run: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`
- checkpoint: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth`
- clean valid summary: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_clean_0527.json`

## Latest Update 2026-05-28 23:58 Asia/Shanghai

## Latest Update 2026-05-30 17:35 Asia/Shanghai

New active task:

- Upgrade the existing fixed CTC blank/nonblank decode bias into a switchable adaptive calibration module for paper-oriented experiments.

Completed in this step:

- Read project instructions and current CTC calibration code paths.
- Confirmed the main implementation files:
  - `util/ctc_decoding.py`
  - `tools/sweep_ctc_decode_bias.py`
  - `tests/test_ctc_eval_utils.py`

Modified files:

- `experiments/notes/goal_status.md`

Training commands:

- None running.
- None completed in this step.

Latest log directory:

- No new training/evaluation log directory yet.

Next step:

- Add failing unit tests for adaptive CTC calibration, then implement the minimal code to pass them.

## Latest Update 2026-05-30 17:38 Asia/Shanghai

Completed in this step:

- Added TDD coverage for adaptive CTC calibration.
- Verified the tests failed before implementation because `apply_ctc_calibration()` did not accept `adaptive_mode`.
- Implemented `adaptive_mode="empty"` in `util/ctc_decoding.py`:
  - `adaptive_mode="none"` preserves fixed-bias behavior.
  - `adaptive_mode="empty"` applies `adaptive_max_scale` when the clean greedy path is empty and `adaptive_min_scale` otherwise.
  - Defaults keep existing behavior unchanged.
- Added adaptive sweep arguments to `tools/sweep_ctc_decode_bias.py`:
  - `--adaptive_modes`
  - `--adaptive_min_scales`
  - `--adaptive_max_scales`
- Verified adaptive setting construction with a lightweight Python smoke.

Modified files:

- `util/ctc_decoding.py`
- `tools/sweep_ctc_decode_bias.py`
- `tests/test_ctc_eval_utils.py`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_ctc_eval_utils.py`
  - result: `Ran 13 tests ... OK`
- Completed smoke:
  - imported `tools.sweep_ctc_decode_bias.build_settings`
  - built `none` and `empty` adaptive settings successfully
- Running:
  - none

Latest log directory:

- No new model evaluation log directory yet.

Next step:

- Run a small adaptive decode sweep on MTHv2 validation to check whether `adaptive_mode=empty` improves or at least preserves the fixed-bias baseline before committing to full validation/test reporting.

## Latest Update 2026-05-30 17:42 Asia/Shanghai

Completed in this step:

- Attempted MTHv2 adaptive sweep inside the default sandbox.
  - It failed because PyTorch could not see CUDA and DTLR `MSDeformAttn` is not implemented on CPU.
- Confirmed GPU visibility:
  - sandbox Python: `torch.cuda.is_available() == False`
  - escalated Python: `torch.cuda.is_available() == True`, `device_count == 2`
- Re-ran the MTHv2 adaptive calibration smoke on GPU successfully.
- Wrote smoke output:
  - `logs/mthv2_adaptive_calibration_smoke_0530.json`
- Smoke result on 50 validation samples:
  - fixed `adaptive_mode=none`, `-2.0/1.0`: CER `0.028790786948176585`
  - `adaptive_mode=empty`, min scale `0.5`, max scale `1.0`: same CER on this tiny sample
  - `adaptive_mode=empty`, min scale `0.0`, max scale `1.0`: CER `0.030710172744721688`
  - interpretation: chain works; 50 samples are not enough for paper claims.

Modified files:

- `util/ctc_decoding.py`
- `tools/sweep_ctc_decode_bias.py`
- `tests/test_ctc_eval_utils.py`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Failed inside sandbox:
  - `tools/sweep_ctc_decode_bias.py ... --max_samples 50 ...`
  - failure: `RuntimeError: Not implemented on the CPU`
- Completed on GPU:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 50 --new_class_embedding --blank_biases -2.0 --nonblank_biases 1.0 --ratio_nonblank_biases 0.0 --adaptive_modes none empty --adaptive_min_scales 0.0 0.5 1.0 --adaptive_max_scales 1.0 --output_json logs/mthv2_adaptive_calibration_smoke_0530.json`

Latest log directory:

- No new directory; latest output file is `logs/mthv2_adaptive_calibration_smoke_0530.json`.

Next step:

- If continuing the adaptive module, run a full validation sweep with a broader scale grid on MTHv2, then repeat only promising settings on HDRC.

## Latest Update 2026-05-31 12:54 Asia/Shanghai

Completed in this step:

- Resumed from `experiments/notes/goal_status.md` and inspected the latest MTHv2 full stage-1 log directory.
- Confirmed the run `logs/mthv2_full_stage1_0531-1248` was using CTC loss instead of stage-1 detection loss:
  - current log shows `loss_CTC` around `1022.9469` at step `0`, with only CTC metrics.
  - trusted stage-1 baseline `logs/mth1000_mth1200_stage1_0512-1755/log.txt` uses detection metrics: `train_loss_ce`, `train_loss_bbox`, `train_loss_giou`, epoch-0 `train_loss=8.4694`.
- Confirmed no `main_synthetic.py` process for `logs/mthv2_full_stage1_0531-1248` is still running and GPU memory is free.
- Root cause:
  - `config/MTHV2_stage1.py` set `mode_chr=True`.
  - current `models/dino/dino.py` routes `mode_chr=True` to `SetCriterion.forward_CTC()` during training.
  - therefore the new stage-1 experiment accidentally became a CTC training run, not detection/localization pretraining.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended/bad run, do not reuse:
  - `main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_0531-1248 -c config/MTHV2_stage1.py --save_log`
- Running:
  - none

Latest log directory:

- Bad/stopped diagnostic log:
  - `logs/mthv2_full_stage1_0531-1248`

Next step:

- Patch the experiment-only config `config/MTHV2_stage1.py` to force the detection criterion under current code, then run a short GPU smoke. Only relaunch a full run if the smoke prints `loss_ce/loss_bbox/loss_giou` and no `loss_CTC`.

## Latest Update 2026-05-31 12:56 Asia/Shanghai

Completed in this step:

- Patched the experiment-only config `config/MTHV2_stage1.py`.
- Changed `mode_chr=True` to `mode_chr=False` so `main_synthetic.py` uses DETR detection losses under the current `models/dino/dino.py` criterion routing.
- Left trusted baseline configs untouched, including `config/MTH1000_MTH1200_stage1.py`.

Modified files:

- `config/MTHV2_stage1.py`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - none
- Ended/bad run, do not reuse:
  - `logs/mthv2_full_stage1_0531-1248`

Latest log directory:

- `logs/mthv2_full_stage1_0531-1248` remains the latest bad/stopped diagnostic run.

Next step:

- Run a one-step/debug GPU smoke with the patched config and verify the log reports detection losses (`loss_ce`, `loss_bbox`, `loss_giou`) instead of `loss_CTC`.

## Latest Update 2026-05-31 12:58 Asia/Shanghai

Completed in this step:

- Ran GPU debug smoke for patched full-MTHv2 stage-1 config.
- Verified the smoke now uses detection losses:
  - log dir: `logs/mthv2_full_stage1_det_smoke_0531`
  - step `0`: `loss=67.8125`, `loss_ce=4.0780`, `loss_bbox=3.6427`, `loss_giou=1.9249`
  - step `10`: `loss=63.0619`, `loss_ce=2.7908`, `loss_bbox=3.5359`, `loss_giou=2.0501`
  - no `loss_CTC` appeared in the inspected smoke log.
- The smoke exited normally after the debug break.

Modified files:

- `config/MTHV2_stage1.py`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed smoke:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --output_dir logs/mthv2_full_stage1_det_smoke_0531 -c config/MTHV2_stage1.py --debug --save_log --options epochs=1 save_checkpoint_interval=999`
- Ended/bad run, do not reuse:
  - `logs/mthv2_full_stage1_0531-1248`
- Running:
  - none

Latest log directory:

- Valid smoke:
  - `logs/mthv2_full_stage1_det_smoke_0531`

Next step:

- Launch the corrected full MTHv2 stage-1 detection run in a new log directory, then monitor the first few printed steps for stable detection-loss behavior.

## Latest Update 2026-05-31 13:00 Asia/Shanghai

Completed in this step:

- Launched the corrected full MTHv2 stage-1 detection pretraining in a new log directory.
- Confirmed it is running on GPU0 and using detection losses, not CTC:
  - process PID: `3643119`
  - data workers observed: `3643228`, `3643260`
  - GPU compute-app memory for PID `3643119`: about `20080 MiB`
  - no `loss_CTC` matched in `stdout.log` or `info.txt`
- Latest observed training progress:
  - log dir: `logs/mthv2_full_stage1_det_0531-1258`
  - step `0/42088`: `loss=56.6150`, `loss_ce=2.2156`, `loss_bbox=3.7090`, `loss_giou=2.1072`
  - step `10/42088`: `loss=66.0472`, running avg `75.3392`
  - step `30/42088`: `loss=85.9474`, running avg `79.9334`
  - step `50/42088`: `loss=49.5183`, running avg `69.7941`

Modified files:

- `config/MTHV2_stage1.py`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_det_0531-1258 -c config/MTHV2_stage1.py --save_log`
- Completed smoke:
  - `logs/mthv2_full_stage1_det_smoke_0531`
- Ended/bad run, do not reuse:
  - `logs/mthv2_full_stage1_0531-1248`

Latest log directory:

- Active corrected run:
  - `logs/mthv2_full_stage1_det_0531-1258`

Next step:

- Let the corrected stage-1 run continue. On next resume, inspect `experiments/notes/goal_status.md`, then tail `logs/mthv2_full_stage1_det_0531-1258/stdout.log` and `info.txt`; after at least one checkpoint is saved, run MTH1000 valid box diagnostics against the trusted stage-1 baseline before doing head reconstruction or full finetuning.

## Latest Update 2026-05-31 13:03 Asia/Shanghai

1. 已完成内容

- 按用户要求删除了误走 CTC 的坏日志目录。
- 保留了当前正确的 detection run 和正确 smoke。
- 再次确认当前有效 run 仍在 GPU0 运行，并且日志继续显示 detection losses。
- 最新观察：
  - `logs/mthv2_full_stage1_det_0531-1258`
  - PID `3643119`
  - GPU 显存约 `16128 MiB`
  - step `420/42088`: `loss=18.4439`, running avg `36.2397`
  - 日志仍是 `loss_ce/loss_bbox/loss_giou`，不是 `loss_CTC`

2. 修改过的文件

- `experiments/notes/goal_status.md`
- 已保留此前修正过的 `config/MTHV2_stage1.py`

3. 正在运行或已结束的训练命令

- 正在运行（有效）：

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_det_0531-1258 -c config/MTHV2_stage1.py --save_log
```

- 已删除坏日志：
  - `logs/mthv2_full_stage1_0531-1248`
  - `logs/mthv2_full_stage1_smoke_0531`

4. 最新日志目录

- 当前有效日志目录：
  - `logs/mthv2_full_stage1_det_0531-1258`
- 保留的正确 smoke：
  - `logs/mthv2_full_stage1_det_smoke_0531`

5. 下一步要做什么

- 继续监控 `logs/mthv2_full_stage1_det_0531-1258/stdout.log` 和 `info.txt`。
- 第一个 checkpoint 保存后，先做 MTH1000 valid box diagnostic，对比 `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`，再决定是否重建分类头和微调。

## Latest Update 2026-05-31 13:04 Asia/Shanghai

1. 已完成内容

- 查询并确认当前有效 stage-1 训练预算。
- 当前配置来自 `logs/mthv2_full_stage1_det_0531-1258/config_cfg.py`：
  - `batch_size=2`
  - `epochs=6`
  - `save_checkpoint_interval=1`
  - `max_iterations=10000`
  - `mode_chr=False`
- 数据规模：
  - train samples: `84176`
  - train loader iterations per epoch: `42088`
- 实际 stage-1 预算：
  - 每个 epoch: `42088` optimizer iterations
  - 总计: `42088 * 6 = 252528` optimizer iterations
  - `max_iterations=10000` 在 `main_synthetic.py` stage-1 detection loop 中不作为停止条件。
- 按当前日志速度估算：
  - 当前每个 epoch 约 `3.8-4.0` 小时
  - 6 个 epoch 总训练约 `23-24` 小时

2. 修改过的文件

- `experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 正在运行（有效）：

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_det_0531-1258 -c config/MTHV2_stage1.py --save_log
```

4. 最新日志目录

- `logs/mthv2_full_stage1_det_0531-1258`

5. 下一步要做什么

- 继续等待 epoch 0 完成并保存第一个 checkpoint；随后做 MTH1000 valid box diagnostic，再决定是否继续全程或提前调整预算。

## Latest Update 2026-05-31 13:06 Asia/Shanghai

1. 已完成内容

- 对比当前 MTHv2 full stage-1 run 与旧 MTH1000+MTH1200 stage-1 baseline 的训练预算。
- 旧 baseline:
  - log dir: `logs/mth1000_mth1200_stage1_0512-1755`
  - datasets: MTH1200 + MTH1000
  - train samples: `35965 + 29423 = 65388`
  - batch size: `2`
  - iterations per epoch: `32694`
  - epochs: `7`
  - total optimizer iterations: `32694 * 7 = 228858`
  - epoch times in log: `3:22:54`, `3:26:00`, `3:15:46`, `3:15:17`, `3:15:01`, `3:14:58`, `3:17:39`
- Current full MTHv2 run:
  - log dir: `logs/mthv2_full_stage1_det_0531-1258`
  - datasets: MTH1000 + MTH1200 + TKH
  - train samples: `29423 + 35965 + 18788 = 84176`
  - batch size: `2`
  - iterations per epoch: `42088`
  - epochs: `6`
  - total optimizer iterations: `42088 * 6 = 252528`
- Difference:
  - dataset size: `+18788` samples (`+28.7%`)
  - iterations per epoch: `+9394` (`+28.7%`)
  - total iterations: `+23670` (`+10.3%`) because epochs changed from `7` to `6`
  - total wall-clock should be close to old baseline, not 28.7% longer.

2. 修改过的文件

- `experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 正在运行（有效）：

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_det_0531-1258 -c config/MTHV2_stage1.py --save_log
```

4. 最新日志目录

- `logs/mthv2_full_stage1_det_0531-1258`

5. 下一步要做什么

- 继续当前 6-epoch run；第一个 checkpoint 后做 box diagnostic，再决定是否需要缩短或继续完整预算。

## Latest Update 2026-05-30 17:46 Asia/Shanghai

Current step:

- Launch full MTHv2 validation sweep for adaptive CTC calibration.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- About to run:
  - `tools/sweep_ctc_decode_bias.py` on MTHv2 validation with fixed baseline and `adaptive_mode=empty` scale grid.

Latest log directory:

- Output file planned:
  - `logs/mthv2_adaptive_calibration_valid_0530.json`

Next step:

- Parse the full validation sweep result and decide whether adaptive calibration improves over the fixed `-2.0/1.0` baseline.

## Latest Update 2026-05-30 18:01 Asia/Shanghai

Completed in this step:

- Completed full MTHv2 validation sweep for `adaptive_mode=empty`.
- Output file:
  - `logs/mthv2_adaptive_calibration_valid_0530.json`
- Result:
  - best fixed baseline remains `blank_bias=-2.0`, `nonblank_bias=1.0`
  - best CER: `0.04561980037205964`
  - `adaptive_mode=empty` only matches fixed baseline when `adaptive_min_scale=1.0`, which is equivalent to fixed bias.
  - lower `adaptive_min_scale` did not improve overall CER.
- Interpretation:
  - sample-level "only boost clean-empty samples" is too conservative for MTHv2.
  - Need to try step-level confidence/margin gating before abandoning adaptive calibration.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.0 -1.8 -1.6 -1.4 --nonblank_biases 1.0 0.8 0.6 --ratio_nonblank_biases 0.0 --adaptive_modes none empty --adaptive_min_scales 0.0 0.25 0.5 0.75 1.0 --adaptive_max_scales 1.0 --output_json logs/mthv2_adaptive_calibration_valid_0530.json`

Latest log directory:

- No new directory; latest output file is `logs/mthv2_adaptive_calibration_valid_0530.json`.

Next step:

- Run MTHv2 validation sweep for margin-gated calibration, which adapts by CTC time-step confidence instead of whole-sample empty/nonempty status.

## Latest Update 2026-05-30 18:02 Asia/Shanghai

Current step:

- Launch MTHv2 validation margin-gated calibration sweep.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- About to run:
  - `tools/sweep_ctc_decode_bias.py` with `--margin_gate_mins/--margin_gate_maxs`.

Latest log directory:

- Output file planned:
  - `logs/mthv2_margin_gated_calibration_valid_0530.json`

Next step:

- Compare margin-gated best setting against fixed `-2.0/1.0` CER `0.04561980037205964`.

## Latest Update 2026-05-30 20:44 Asia/Shanghai

Completed in this step:

- Launched a large MTHv2 margin-gated calibration sweep.
- Observed that it ran for too long without writing output because the grid was too large:
  - 4 blank values x 4 nonblank values x 5 gate mins x 5 gate maxs = 400 decode settings.
  - The script applies calibration and Levenshtein scoring per setting per sample, so this grid is not practical without caching.
- Stopped the process with `kill -TERM`.
- Confirmed PID `3543167` stopped.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Stopped:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.4 -2.0 -1.6 -1.2 --nonblank_biases 1.2 1.0 0.8 0.6 --ratio_nonblank_biases 0.0 --margin_gate_mins -0.2 -0.1 0.0 0.1 0.2 --margin_gate_maxs 0.2 0.4 0.6 0.8 1.0 --adaptive_modes none --output_json logs/mthv2_margin_gated_calibration_valid_0530.json`
- Result:
  - no output JSON was written.

Latest log directory:

- No new completed output from the stopped large sweep.

Next step:

- Use a narrow margin-gate grid around the current best fixed setting, or add cached prediction output before running broader sweeps.

## Latest Update 2026-05-30 20:45 Asia/Shanghai

Current step:

- Launch narrow MTHv2 margin-gated calibration sweep around the current best fixed setting.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- About to run a narrow grid:
  - fixed `blank_bias=-2.0`
  - fixed `nonblank_bias=1.0`
  - selected margin gates only

Latest log directory:

- Output file planned:
  - `logs/mthv2_margin_gated_calibration_valid_narrow_0530.json`

Next step:

- Compare narrow margin-gated results against fixed validation CER `0.04561980037205964`.

## Latest Update 2026-05-30 21:01 Asia/Shanghai

Completed in this step:

- Completed narrow MTHv2 margin-gated calibration sweep.
- Output file:
  - `logs/mthv2_margin_gated_calibration_valid_narrow_0530.json`
- Result:
  - best margin-gated CER: `0.045809`
  - fixed baseline CER: `0.04561980037205964`
  - margin gating did not improve MTHv2 validation.
- Interpretation:
  - time-step margin gating reduces substitutions in some settings but increases deletions/empty rate enough to lose overall.
  - Do not use margin-gated calibration as the paper module.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.0 --nonblank_biases 1.0 --ratio_nonblank_biases 0.0 --margin_gate_mins -0.1 0.0 0.1 --margin_gate_maxs 0.3 0.5 0.7 --adaptive_modes none --output_json logs/mthv2_margin_gated_calibration_valid_narrow_0530.json`

Latest log directory:

- No new directory; latest output file is `logs/mthv2_margin_gated_calibration_valid_narrow_0530.json`.

Next step:

- Implement a predicted-short adaptive mode: keep the fixed bias for normal samples, but apply stronger scaling only when clean CTC decoding predicts a short sequence.

## Latest Update 2026-05-30 21:06 Asia/Shanghai

Completed in this step:

- Added `pred_short` adaptive calibration mode with TDD.
- New behavior:
  - compute clean CTC collapsed prediction length.
  - if clean predicted length is `<= adaptive_short_pred_max_len`, apply `adaptive_max_scale`.
  - otherwise apply `adaptive_min_scale`.
- Added sweep arguments:
  - `--adaptive_modes pred_short`
  - `--adaptive_short_pred_max_lens`
- Unit tests:
  - command: `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_ctc_eval_utils.py`
  - result: `Ran 15 tests ... OK`

Modified files:

- `util/ctc_decoding.py`
- `tools/sweep_ctc_decode_bias.py`
- `tests/test_ctc_eval_utils.py`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_ctc_eval_utils.py`
- Running:
  - none

Latest log directory:

- No new completed output yet for `pred_short`.

Next step:

- Run a small MTHv2 smoke for `pred_short`, then a full validation sweep if the command path works.

## Latest Update 2026-05-30 21:08 Asia/Shanghai

Completed in this step:

- Attempted to launch MTHv2 `pred_short` adaptive calibration smoke on GPU.
- The command was rejected by the external execution/usage-limit system before running.
- No new evaluation output was produced.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Attempted but not run:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 50 --new_class_embedding --blank_biases -2.0 --nonblank_biases 1.0 --ratio_nonblank_biases 0.0 --adaptive_modes none pred_short --adaptive_min_scales 1.0 --adaptive_max_scales 1.0 1.2 1.4 --adaptive_short_pred_max_lens 1 2 --output_json logs/mthv2_pred_short_calibration_smoke_0530.json`
- Rejection reason:
  - external usage limit hit; retry after `2026-05-31 12:28 PM` or after more credits are available.
- Running:
  - none

Latest log directory:

- No new `pred_short` output file.
- Latest completed adaptive files remain:
  - `logs/mthv2_adaptive_calibration_smoke_0530.json`
  - `logs/mthv2_adaptive_calibration_valid_0530.json`
  - `logs/mthv2_margin_gated_calibration_valid_narrow_0530.json`

Next step:

- After GPU execution is available again, run the `pred_short` smoke command above.
- If it succeeds, run a full MTHv2 validation sweep using a small grid:
  - fixed bias `-2.0/1.0`
  - `adaptive_mode=pred_short`
  - `adaptive_min_scale=1.0`
  - `adaptive_max_scale in {1.1, 1.2, 1.3, 1.4}`
  - `adaptive_short_pred_max_len in {1, 2, 3}`

## Latest Update 2026-05-31 12:45 Asia/Shanghai

New active experiment idea:

- Run a new stage-1 localization-aware pretraining using full MTHv2:
  - MTH1000
  - MTH1200
  - TKH
- Then use this checkpoint for:
  1. MTH1000 valid box diagnostic,
  2. CTC head reconstruction,
  3. downstream full finetuning comparison.

Completed in this step:

- Read current status and relevant configs/datasets.
- Confirmed previous trusted real stage-1 baseline used only:
  - `tkhmth2200_mth1200_dtlr`
  - `tkhmth2200_mth1000_dtlr`
- Confirmed full MTHv2 processed split sizes:
  - MTH1000 train/valid/test: `29423/4489/4044`
  - MTH1200 train/valid/test: `35965/4157/4029`
  - TKH train/valid/test: `18788/2302/2382`
  - full MTHv2 train total: `84176`
- Confirmed raw TKH character labels exist:
  - `data/TKHMTH2200/TKH/label_char`: `999` files
- Confirmed current GPU/process state:
  - no active `main_synthetic.py`, `finetuning.py`, MMOCR `tools/train.py`, or decode sweep process found in sandbox process view.
  - GPU0/GPU1 idle by `nvidia-smi`.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- None started in this step.

Latest log directory:

- None yet for this new experiment.

Next step:

- Create a new experiment-only stage-1 config for full MTHv2 real char-box pretraining.
- Smoke-test dataset construction and char-box usage before launching full stage-1 training.

## Latest Update 2026-05-31 12:47 Asia/Shanghai

Completed in this step:

- Added new experiment-only full MTHv2 stage-1 config:
  - `config/MTHV2_stage1.py`
- Config scope:
  - uses `tkhmth2200_mth1000_dtlr`
  - uses `tkhmth2200_mth1200_dtlr`
  - uses `tkhmth2200_tkh_dtlr`
  - enables raw character boxes with `mth1000_use_char_boxes=True`
  - sets `num_classes=6727`
  - sets `epochs=6`, about `252k` loader iterations with batch size `2`
- Existing trusted baseline config remains unchanged:
  - `config/MTH1000_MTH1200_stage1.py`

Modified files:

- `config/MTHV2_stage1.py`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- None started in this step.

Latest log directory:

- None yet for this new experiment.

Next step:

- Run dataset/char-box smoke for `config/MTHV2_stage1.py`.

## Latest Update 2026-05-31 12:50 Asia/Shanghai

Completed in this step:

- Ran dataset/char-box smoke for `config/MTHV2_stage1.py`.
- First smoke used `SLConfig` directly and falsely showed dummy boxes because `copy.copy(SLConfig)` drops config attributes inside `MTHCombo`; this is not the formal training path.
- Re-ran smoke with an argparse-style namespace matching `main_synthetic.py`.
- Formal-path smoke result:
  - total train samples: `84176`
  - charset size: `6727`
  - raw char boxes enabled for all three child datasets:
    - MTH1000: `20/20` checked samples used real boxes
    - MTH1200: `20/20` checked samples used real boxes
    - TKH: `20/20` checked samples used real boxes
- Interpretation:
  - `config/MTHV2_stage1.py` is valid for full MTHv2 stage-1 pretraining.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed dataset smoke:
  - loaded `config/MTHV2_stage1.py`
  - built `dataset_file=mth_combo`, split `train`
  - checked first 20 samples per subset for real character boxes
- Running:
  - none

Latest log directory:

- None yet for this new experiment.

Next step:

- Run a minimal runtime training smoke for full MTHv2 stage-1 config before launching the full run.

## Latest Update 2026-05-31 12:52 Asia/Shanghai

Current step:

- Launch minimal runtime smoke for full MTHv2 stage-1 config.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- About to run:
  - `main_synthetic.py`
  - config: `config/MTHV2_stage1.py`
  - dataset: `mth_combo`
  - debug mode, one epoch override

Latest log directory:

- Planned smoke output:
  - `logs/mthv2_full_stage1_smoke_0531`

Next step:

- Confirm smoke reaches finite loss and exits, then decide whether to launch full stage-1.

## Latest Update 2026-05-31 12:55 Asia/Shanghai

Completed in this step:

- Completed minimal runtime smoke for full MTHv2 stage-1.
- Smoke output directory:
  - `logs/mthv2_full_stage1_smoke_0531`
- Smoke result:
  - model built with `num_classes=6727`
  - train split built with `84176` samples
  - valid split built with `10948` samples
  - raw char boxes enabled for MTH1000/MTH1200/TKH
  - entered training loop
  - finite CTC loss observed:
    - step `0`: `loss_CTC=707.2429`
    - step `10`: `loss_CTC=674.4135`
  - debug break triggered and process exited with code `0`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --output_dir logs/mthv2_full_stage1_smoke_0531 -c config/MTHV2_stage1.py --debug --save_log --options epochs=1 save_checkpoint_interval=999`
- Running:
  - none

Latest log directory:

- `logs/mthv2_full_stage1_smoke_0531`

Next step:

- Launch full MTHv2 stage-1 pretraining on GPU0:
  - config `config/MTHV2_stage1.py`
  - output under `logs/mthv2_full_stage1_*`
  - expected budget about `42088 * 6 ~= 252k` loader iterations.

## Latest Update 2026-05-31 12:56 Asia/Shanghai

Current step:

- Launch full MTHv2 stage-1 pretraining on GPU0.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- About to run:
  - `main_synthetic.py`
  - config: `config/MTHV2_stage1.py`
  - dataset: `mth_combo`
  - output: `logs/mthv2_full_stage1_0531-1248`

Latest log directory:

- Planned:
  - `logs/mthv2_full_stage1_0531-1248`

Next step:

- Confirm PID, GPU memory, and first finite training log line after launch.

## Latest Update 2026-05-31 12:58 Asia/Shanghai

Completed in this step:

- Launched full MTHv2 stage-1 pretraining on GPU0.
- Background parent shell returned PID `3640623`.
- Actual training process:
  - main PID: `3640625`
  - dataloader worker PIDs observed: `3640734`, `3640766`
- GPU status:
  - GPU0 utilization: `100%`
  - GPU0 memory: about `19804 MiB / 24576 MiB`
- First finite training logs observed:
  - step `0`: `loss_CTC=1022.9469`, max mem `8396`
  - step `10`: `loss_CTC=805.0595`, max mem `13018`
- Dataset confirmed in training stdout:
  - train total `84176`, charset `6727`
  - valid total `10948`, charset `6727`
  - raw char boxes from MTH1000/MTH1200/TKH all enabled

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_0531-1248 -c config/MTHV2_stage1.py --save_log
```

- Full launch command used:

```bash
mkdir -p logs/mthv2_full_stage1_0531-1248 && setsid env MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_0531-1248 -c config/MTHV2_stage1.py --save_log > logs/mthv2_full_stage1_0531-1248/stdout.log 2>&1 < /dev/null &
```

Latest log directory:

- `logs/mthv2_full_stage1_0531-1248`
- stdout:
  - `logs/mthv2_full_stage1_0531-1248/stdout.log`
- main log:
  - `logs/mthv2_full_stage1_0531-1248/info.txt`

Next step:

- Monitor stage-1 through epoch completion.
- After checkpoint is available, run MTH1000 valid box diagnostic against trusted real stage-1 baseline:
  - new checkpoint: `logs/mthv2_full_stage1_0531-1248/checkpoint.pth`
  - trusted baseline: `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`
- Only if the diagnostic is competitive, proceed to CTC head reconstruction and downstream full finetuning.

Completed since previous status write:

- Re-read this status file, the goal plan, and the latest MTHv2 SGQ log directory after resume.
- Confirmed the full MTHv2 SGQ run is not complete and should not be restarted.
- Confirmed the previous stdout pipe recovery remains active:
  - tmux session `mthv2_sgq_stdout_drain_0528` is running.
  - tmux session `mthv2_sgq_stderr_drain_0528` is running.
- Confirmed host PID `3408112` is still running the MTHv2 SGQ full training command.
- Confirmed GPU state:
  - GPU0 utilization about `63%`.
  - GPU0 memory `20908/24576 MiB`.
  - compute app PID `3408112` uses `20894 MiB`.

Modified files in this step:

- `experiments/notes/goal_status.md`

Current training command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Latest observed results/progress:

- `log.txt` now has epoch `0` and epoch `1`.
- epoch `0`:
  - `test_cer_oracle_direction`: `0.12700862404436544`
  - `test_wer_oracle_direction`: `0.3670523743094075`
  - `test_blank_pred_ratio_unscaled`: `0.9895538636964736`
- epoch `1`:
  - `test_cer_oracle_direction`: `0.12201948555193866`
  - `test_wer_oracle_direction`: `0.3423195463956333`
  - `test_blank_pred_ratio_unscaled`: `0.9894848499402191`
  - checkpoint updated as new best at epoch `1`.
- MTHv2 baseline full-run best valid CER remains better:
  - baseline: `0.11397798822246911` at `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
  - current SGQ best so far: `0.12201948555193866`
- Latest `info.txt`/drained stdout progress:
  - epoch `2`, step `1170/42088`
  - last observed timestamp: `2026-05-28 23:57:24`
  - `loss_short_gt_ce` is present, so the SGQ auxiliary loss remains active.

Next step:

1. Keep monitoring the same MTHv2 SGQ run; do not start HDRC or any other full training while PID `3408112` is active.
2. Check `info.txt`, `log.txt`, process state, GPU state, and tmux drains periodically.
3. If epoch `2` completes, update this file with the new CER before deciding whether to continue, early-stop, or summarize.
4. If the process blocks again, first inspect `wchan`; if it is `pipe_write`, keep or restore the drain readers before changing the training process.

## Latest Update 2026-05-28 23:59 Asia/Shanghai

Completed since previous status write:

- Monitored `logs/mthv2_sgq_short_ce_full_0528-2240` again.
- Confirmed no new validation row yet; `log.txt` still contains epochs `0` and `1`.

## Latest Update 2026-05-29 22:56 Asia/Shanghai

Completed since previous status write:

- Resumed from `experiments/notes/goal_status.md` and `experiments/notes/goal_plan_mthv2_hdrc.md`.
- Confirmed the next requested work is an MMOCR comparison-model trial, not a repeat of completed DTLR MTHv2 SGQ or decode-calibration experiments.
- Checked GPU state before launch:
  - GPU0: idle, about `8 MiB` used.
  - GPU1: idle, `0 MiB` used.
- Selected the already-prepared MMOCR MTHv2 SAR config for the first comparison-model trial:
  - `/home/ubuntu/mmocr/configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py`

Modified files in this step:

- `experiments/notes/goal_status.md`

Current or next training command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options train_cfg.max_epochs=1 train_cfg.val_interval=1 train_dataloader.dataset.datasets.0.indices=64 val_dataloader.dataset.indices=64 train_dataloader.batch_size=2 train_dataloader.num_workers=0 train_dataloader.persistent_workers=False val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False default_hooks.checkpoint.interval=-1 default_hooks.checkpoint.save_last=False load_from=None work_dir=work_dirs/trial_mthv2_sar_gpu1_0529-2256
```

Latest log directory:

- pending launch: `/home/ubuntu/mmocr/work_dirs/trial_mthv2_sar_gpu1_0529-2256`

Next step:

1. Launch the MTHv2 SAR MMOCR trial on GPU1.
2. Monitor whether dataset loading, forward/backward, validation, and metric logging complete.
3. Update this file again with the final command status and latest MMOCR log directory before reporting back.

## Latest Update 2026-05-29 22:57 Asia/Shanghai

Completed since previous status write:

- Launched the MTHv2 SAR MMOCR trial on GPU1.
- The command initialized MMOCR and confirmed `GPU number: 1`.
- The run stopped before training because the validation subset override was placed at the outer `ConcatDataset` level:
  - error: `TypeError: __init__() got an unexpected keyword argument 'indices'`
- Root cause: training override used `train_dataloader.dataset.datasets.0.indices=64`, but validation used `val_dataloader.dataset.indices=64`. The correct validation override is `val_dataloader.dataset.datasets.0.indices=64`.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended training command:

```bash
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options train_cfg.max_epochs=1 train_cfg.val_interval=1 train_dataloader.dataset.datasets.0.indices=64 val_dataloader.dataset.indices=64 train_dataloader.batch_size=2 train_dataloader.num_workers=0 train_dataloader.persistent_workers=False val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False default_hooks.checkpoint.interval=-1 default_hooks.checkpoint.save_last=False load_from=None work_dir=work_dirs/trial_mthv2_sar_gpu1_0529-2256
```

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/trial_mthv2_sar_gpu1_0529-2256`

Next step:

1. Relaunch with `val_dataloader.dataset.datasets.0.indices=64`.
2. Keep GPU1 assignment with `CUDA_VISIBLE_DEVICES=1`.
3. Monitor whether training and validation complete.

## Latest Update 2026-05-29 22:58 Asia/Shanghai

Completed since previous status write:

- Relaunched the MTHv2 SAR MMOCR trial with the corrected validation subset override.
- Confirmed MMOCR used one visible GPU through `CUDA_VISIBLE_DEVICES=1`:
  - MMOCR runtime printed `GPU number: 1`.
- Trial completed successfully.
- Training completed:
  - epoch `1`
  - `32/32` training iterations
  - batch size `2`
  - train subset size `64`
  - final trial loss: `loss: 4.3756`, `loss_ce: 4.3756`
- Validation completed:
  - `4/4` validation batches
  - validation subset size `64`
  - MMOCR metric: `recog/1-N.E.D: 0.0000`
- Checkpoint saving was disabled for this trial, so no model checkpoint was written.
- Post-run GPU check:
  - GPU0: idle, about `8 MiB` used.
  - GPU1: idle, `0 MiB` used.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended training command:

```bash
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options train_cfg.max_epochs=1 train_cfg.val_interval=1 train_dataloader.dataset.datasets.0.indices=64 val_dataloader.dataset.datasets.0.indices=64 train_dataloader.batch_size=2 train_dataloader.num_workers=0 train_dataloader.persistent_workers=False val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False default_hooks.checkpoint.interval=-1 default_hooks.checkpoint.save_last=False load_from=None work_dir=work_dirs/trial_mthv2_sar_gpu1_0529-2258
```

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/trial_mthv2_sar_gpu1_0529-2258`
- latest log file: `/home/ubuntu/mmocr/work_dirs/trial_mthv2_sar_gpu1_0529-2258/20260529_225718/20260529_225718.log`

Next step:

1. For a real MMOCR comparison baseline, run the same SAR config on full MTHv2 without the `indices=64` subset overrides.
2. Decide checkpoint interval and validation schedule before full launch to avoid unnecessary huge checkpoint churn.
3. After full training, export predictions and compute DTLR-aligned CER/AR/CR plus short-text bucket metrics instead of relying only on MMOCR `1-N.E.D`.

## Latest Update 2026-05-29 23:00 Asia/Shanghai

Completed since previous status write:

- Prepared the first full MMOCR comparison run on MTHv2.
- Selected model/config:
  - SAR
  - `/home/ubuntu/mmocr/configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py`
- Confirmed base schedule:
  - `max_epochs=5`
  - `val_interval=1`
  - optimizer: `Adadelta(lr=1.0)`
- Confirmed MTHv2 SAR config:
  - full train JSON: `data/mmocr_exports/mthv2/textrecog_train.json`
  - full val JSON: `data/mmocr_exports/mthv2/textrecog_val.json`
  - full test JSON: `data/mmocr_exports/mthv2/textrecog_test.json`
  - charset: `data/mmocr_exports/mthv2/charset.txt`
  - batch size: `16`
- Checked GPU state before launch:
  - GPU0: idle, about `8 MiB` used.
  - GPU1: idle, `0 MiB` used.
- Planned checkpoint policy for the full run:
  - validate every epoch
  - save best by `recog/1-N.E.D`
  - keep at most one old interval checkpoint to reduce checkpoint churn

Modified files in this step:

- `experiments/notes/goal_status.md`

Current or next training command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_full_gpu1_0529-2300
```

Latest log directory:

- pending launch: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Start this full SAR run on GPU1 in a tmux session so it does not depend on the current API tool pipe.
2. Confirm the process is alive and the log file is growing.
3. Update this file with session name, PID/process status, and latest log path.

## Latest Update 2026-05-29 23:02 Asia/Shanghai

Completed since previous status write:

- Created MMOCR work directory:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- Started the first full MMOCR comparison run in tmux:
  - tmux session: `mmocr_mthv2_sar_gpu1_0529`
  - model: SAR
  - dataset: full MTHv2
  - GPU assignment: `CUDA_VISIBLE_DEVICES=1`
- Confirmed tmux session is present.
- Confirmed host GPU process:
  - PID `3477358`
  - process: `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`
  - GPU memory: about `22024 MiB`
- Confirmed GPU state:
  - GPU0: idle, about `8 MiB` used.
  - GPU1: `100%` utilization, about `22030/24576 MiB` used.
- Confirmed training progress from stdout:
  - `Epoch(train) [1][ 100/5261]`
  - ETA about `4:12:17`
  - latest logged loss: `loss: 6.5429`, `loss_ce: 6.5429`

Modified files in this step:

- `experiments/notes/goal_status.md`

Running training command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_full_gpu1_0529-2300
```

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- stdout mirror: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`
- MMOCR log file: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/20260529_230121/20260529_230121.log`

Next step:

1. Monitor the same tmux session and stdout log; do not start another full comparison run on GPU1 while PID `3477358` is active.
2. After epoch `1` validation finishes, record `recog/1-N.E.D` and checkpoint files.
3. After all epochs complete, export or collect predictions and compute DTLR-aligned CER/AR/CR plus short-text bucket metrics.

## Latest Update 2026-05-29 23:14 Asia/Shanghai

Completed since previous status write:

- Received request to start another MMOCR comparison model on GPU0 using MTHv2 while SAR continues on GPU1.
- Selected CRNN as the second comparison model because it is the classic CTC baseline and complements SAR's attention decoder.
- Checked GPU state:
  - GPU0: idle, about `8 MiB` used.
  - GPU1: active, about `22030/24576 MiB` used by the SAR run.
- Checked SAR progress:
  - latest observed: `Epoch(train) [1][1300/5261]`
  - latest loss: `loss: 4.8946`, `loss_ce: 4.8946`
- Inspected MMOCR CRNN configs:
  - base config: `/home/ubuntu/mmocr/configs/textrecog/crnn/_base_crnn_mini-vgg.py`
  - MTH1000 config: `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mth1000.py`
- Planned a new MTHv2 CRNN config using:
  - full MTHv2 train/val/test JSONs
  - MTHv2 exported charset
  - `load_from = None`, matching the current SAR from-scratch comparison setting
  - `OneMinusNEDMetric`, matching the SAR validation metric for best-checkpoint selection

Modified files in this step:

- `experiments/notes/goal_status.md`

Current training:

- SAR remains active on GPU1:
  - tmux session: `mmocr_mthv2_sar_gpu1_0529`
  - log dir: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Latest log directory:

- current active SAR log: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Add the new MMOCR CRNN MTHv2 config file.
2. Validate that the config loads with the correct charset and annotation files.
3. Start CRNN full MTHv2 training on GPU0 in a separate tmux session if config loading is clean.

## Latest Update 2026-05-29 23:15 Asia/Shanghai

Completed since previous status write:

- Added new MMOCR CRNN MTHv2 config:
  - `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`
- Config choices:
  - inherits from MMOCR CRNN MTH1000 config
  - `load_from = None`
  - dictionary: `data/mmocr_exports/mthv2/charset.txt`
  - train JSON: `mmocr_exports/mthv2/textrecog_train.json`
  - val JSON: `mmocr_exports/mthv2/textrecog_val.json`
  - test JSON: `mmocr_exports/mthv2/textrecog_test.json`
  - train batch size: `16`
  - validation metric: `OneMinusNEDMetric`
  - max epochs: `5`
- Verified config loading with openmmlab Python:
  - `load_from None`
  - dictionary and annotation files are correct
  - `train_bs 16`
  - `val_eval OneMinusNEDMetric`
  - `max_epochs 5`

Modified files in this step:

- `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`
- `experiments/notes/goal_status.md`

Current training:

- SAR remains active on GPU1:
  - tmux session: `mmocr_mthv2_sar_gpu1_0529`
  - log dir: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Latest log directory:

- current active SAR log: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Start full CRNN MTHv2 training on GPU0 in a tmux session.
2. Save logs under `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_full_gpu0_0529-2315`.
3. Confirm PID, GPU0 memory, and first training progress line.

## Latest Update 2026-05-29 23:18 Asia/Shanghai

Completed since previous status write:

- Started CRNN MTHv2 full training on GPU0:
  - tmux session: `mmocr_mthv2_crnn_gpu0_0529`
  - work dir: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_full_gpu0_0529-2315`
  - PID: `3479047`
- Detected invalid CRNN training immediately:
  - `Epoch(train) [1][ 100/5261] ... loss: nan loss_ctc: nan`
  - NaN continued through later logged steps.
- Stopped the GPU0 CRNN process:
  - `kill -TERM 3479047`
  - GPU0 returned to idle.
- Confirmed SAR remains active on GPU1:
  - PID `3477358`
  - GPU1 memory about `22024 MiB`
- Root-cause evidence for CRNN NaN:
  - example image: `/home/ubuntu/mmocr/data/tkhmth2200_mth1000_dtlr/lines/005_000.jpg`
  - original size: `width=108`, `height=1309`
  - label length: `15`
  - without vertical rotation, resizing to height `32` leaves an effective narrow-width CTC sequence, which is too short for many vertical-line labels.
  - after rotating the vertical line first, the long text direction becomes the CRNN time axis.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended training command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_full_gpu0_0529-2315
```

Latest log directory:

- failed CRNN log: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_full_gpu0_0529-2315`
- active SAR log: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Fix the CRNN MTHv2 config so vertical line images are rotated before CRNN/CTC resizing.
2. Run a small GPU0 CRNN smoke after the fix and require finite `loss_ctc`.
3. Only start a full GPU0 CRNN run if the smoke is clean.

## Latest Update 2026-05-29 23:23 Asia/Shanghai

Completed since previous status write:

- Fixed CRNN vertical pipeline in:
  - `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`
- First attempted fix still produced NaN because the rotate condition was written with reversed `img_shape` order.
- Diagnosed `img_shape` convention:
  - MMOCR uses `(height, width)`.
  - correct vertical condition is `results['img_shape'][1] < results['img_shape'][0]`.
- Confirmed corrected pipeline transforms vertical samples properly:
  - sample 0 input changed from `32x32` to `32x384`
  - CRNN feature time steps changed to `97`
  - target length was `15`
- Re-ran GPU0 smoke after correction:
  - command used train subset `64`, val subset `64`
  - work dir: `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_crnn_vertical_gpu0_0529-2323`
  - result: completed successfully
  - training: `Epoch(train) [1][4/4]`
  - finite loss: `loss: 44.1857`, `loss_ctc: 44.1857`
  - validation: `Epoch(val) [1][64/64] recog/1-N.E.D: 0.0000`

Modified files in this step:

- `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`
- `experiments/notes/goal_status.md`

Ended smoke command:

```bash
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --cfg-options train_cfg.max_epochs=1 train_cfg.val_interval=1 train_dataloader.dataset.datasets.0.indices=64 val_dataloader.dataset.datasets.0.indices=64 train_dataloader.batch_size=16 train_dataloader.num_workers=0 train_dataloader.persistent_workers=False val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False default_hooks.checkpoint.interval=-1 default_hooks.checkpoint.save_last=False load_from=None work_dir=work_dirs/smoke_mthv2_crnn_vertical_gpu0_0529-2323
```

Latest log directories:

- successful CRNN smoke: `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_crnn_vertical_gpu0_0529-2323`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Start full CRNN MTHv2 training on GPU0 with the corrected vertical config.
2. Use a separate tmux session and log directory.
3. Confirm GPU0 process, first training progress, and finite loss before reporting back.

## Latest Update 2026-05-29 23:24 Asia/Shanghai

Completed since previous status write:

- Started full CRNN MTHv2 training on GPU0 with the corrected vertical config.
- tmux session:
  - `mmocr_mthv2_crnn_gpu0_0529b`
- Work directory:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- Confirmed host GPU processes:
  - CRNN PID `3480811`, `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`, about `2218 MiB` on GPU0.
  - SAR PID `3477358`, `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`, about `22024 MiB` on GPU1.
- Confirmed GPU state:
  - GPU0: active, about `88%` utilization and `2232/24576 MiB` used.
  - GPU1: active, about `100%` utilization and `22030/24576 MiB` used.
- Confirmed CRNN full run has finite CTC loss:
  - `Epoch(train) [1][ 100/5261] ... loss: 7.4661 loss_ctc: 7.4661`
  - `Epoch(train) [1][ 500/5261] ... loss: 6.9162 loss_ctc: 6.9162`
- Confirmed SAR is still running normally on GPU1:
  - latest observed SAR progress before CRNN full launch: `Epoch(train) [1][2200/5261]`

Modified files in this step:

- `experiments/notes/goal_status.md`

Running training commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_full_gpu1_0529-2300
```

Latest log directories:

- CRNN full run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- SAR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`

Next step:

1. Monitor both tmux sessions:
   - `mmocr_mthv2_crnn_gpu0_0529b`
   - `mmocr_mthv2_sar_gpu1_0529`
2. Record epoch validation metrics and checkpoint paths when each finishes validation.
3. If CRNN finishes much earlier, do not start another GPU0 full comparison run until its validation result and checkpoint status are recorded.

## Latest Update 2026-05-29 23:34 Asia/Shanghai

Completed since previous status write:

- Added cleanup rule from user:
  - after a smoke/short run is completed and the corresponding formal long training has started and been confirmed healthy, delete the smoke/short-run log directories.
- Confirmed current formal long trainings are still active:
  - CRNN PID `3480811`, GPU0, about `2800 MiB`
  - SAR PID `3477358`, GPU1, about `22024 MiB`
- Deleted completed short-run / failed-short-run MMOCR directories:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_full_gpu0_0529-2315`
  - `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_crnn_vertical_gpu0_0529-2320`
  - `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_crnn_vertical_gpu0_0529-2323`
  - `/home/ubuntu/mmocr/work_dirs/trial_mthv2_sar_gpu1_0529-2256`
  - `/home/ubuntu/mmocr/work_dirs/trial_mthv2_sar_gpu1_0529-2258`
- Verified those short-run directories are no longer present.
- Confirmed latest CRNN progress:
  - `Epoch(train) [4][3200/5261]`
  - latest loss: `loss: 5.0750`, `loss_ctc: 5.0750`
- Confirmed latest SAR progress:
  - `Epoch(train) [1][3300/5261]`
  - latest loss: `loss: 4.4455`, `loss_ce: 4.4455`

Modified files in this step:

- `experiments/notes/goal_status.md`
- Deleted only short-run MMOCR work directories listed above.

Running training commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_full_gpu1_0529-2300
```

Latest log directories:

- CRNN full run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- SAR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`

Next step:

1. Continue monitoring CRNN and SAR full runs.
2. Record validation metrics/checkpoints when each run completes an epoch or finishes.
3. For future MMOCR smoke/short tests, delete their work directories after the corresponding full run has started and finite loss/progress are confirmed.

## Latest Update 2026-05-29 23:41 Asia/Shanghai

Completed since previous status write:

- Checked whether CRNN finished.
- Confirmed CRNN tmux session `mmocr_mthv2_crnn_gpu0_0529b` is no longer present.
- Confirmed GPU0 is idle again:
  - GPU0: `0%`, about `8 MiB`
- Confirmed CRNN completed normally through epoch `5` validation, not an abnormal exit.
- CRNN validation `recog/1-N.E.D` by epoch:
  - epoch 1: `0.0488`
  - epoch 2: `0.1433`
  - epoch 3: `0.1885`
  - epoch 4: `0.2432`
  - epoch 5: `0.2844`
- Best checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_5.pth`
  - best valid metric: `recog/1-N.E.D = 0.2844`
  - checkpoint size: `51215811` bytes
- Other CRNN output:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/epoch_5.pth`
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/last_checkpoint`
- Confirmed SAR is still active on GPU1:
  - PID `3477358`
  - GPU1 memory about `22024 MiB`
  - latest observed progress: `Epoch(train) [1][4100/5261]`

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended training command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- completed CRNN full run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- SAR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`

Next step:

1. Do not treat CRNN as final paper metric yet; it still needs test-set inference and DTLR-aligned CER/AR/CR/short-bucket evaluation.
2. Because CRNN's valid `1-N.E.D` was still improving at epoch 5, consider extending CRNN training later if following the planned early-stopping/max-epoch protocol.
3. Continue monitoring SAR on GPU1 until epoch validation metrics are available.

## Latest Update 2026-05-29 23:43 Asia/Shanghai

Completed since previous status write:

- User requested continuing CRNN training using the same log/work directory.
- Confirmed GPU0 is idle:
  - GPU0: `0%`, about `8 MiB`
- Confirmed CRNN resume checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/epoch_5.pth`
  - `last_checkpoint` points to this file.
- Confirmed SAR remains active on GPU1:
  - GPU1: about `100%`, `22030/24576 MiB`
- Plan for CRNN continuation:
  - resume in the same work directory
  - append stdout to the existing `stdout.log`
  - increase `train_cfg.max_epochs` from `5` to `15`
  - keep best-checkpoint selection by `recog/1-N.E.D`

Modified files in this step:

- `experiments/notes/goal_status.md`

Current or next CRNN resume command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --resume --cfg-options train_cfg.max_epochs=15 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- CRNN full run/resume: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Start CRNN resume on GPU0 in a new tmux session.
2. Confirm it resumes from epoch 5 and continues to epoch 6, not restarting from epoch 1.
3. Monitor first new training log line and GPU0 process.

## Latest Update 2026-05-29 23:44 Asia/Shanghai

Completed since previous status write:

- Started CRNN resume on GPU0 in tmux:
  - tmux session: `mmocr_mthv2_crnn_gpu0_resume_0529`
- Confirmed it resumed correctly, not restarted:
  - `Auto resumed from the latest checkpoint .../epoch_5.pth`
  - `resumed epoch: 5, iter: 26305`
  - new training progress is epoch `6`
- Confirmed CRNN process:
  - PID `3482527`
  - process: `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`
  - GPU0 memory: about `2626 MiB`
- Confirmed GPU state:
  - GPU0: active, about `83%`, `2640/24576 MiB`
  - GPU1: active, about `96%`, `22030/24576 MiB`
- Latest CRNN resume progress:
  - `Epoch(train) [6][ 600/5261]`
  - latest finite loss: `loss: 4.6154`, `loss_ctc: 4.6154`

Modified files in this step:

- `experiments/notes/goal_status.md`

Running CRNN resume command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --resume --cfg-options train_cfg.max_epochs=15 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- CRNN resume/full run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Continue monitoring CRNN through epoch 15 or until evidence supports early stopping.
2. Record each new validation `recog/1-N.E.D` and best checkpoint path.
3. Continue monitoring SAR on GPU1.

## Latest Update 2026-05-30 00:52 Asia/Shanghai

Completed since previous status write:

- Checked CRNN resume status after user reported it finished.
- Confirmed CRNN resume tmux session `mmocr_mthv2_crnn_gpu0_resume_0529` is no longer present.
- Confirmed CRNN completed normally through epoch `15` validation.
- Confirmed only SAR remains active on GPU:
  - SAR PID `3477358`
  - GPU1 memory about `22026 MiB`
- CRNN validation `recog/1-N.E.D` by epoch:
  - epoch 1: `0.0488`
  - epoch 2: `0.1433`
  - epoch 3: `0.1885`
  - epoch 4: `0.2432`
  - epoch 5: `0.2844`
  - epoch 6: `0.3318`
  - epoch 7: `0.3715`
  - epoch 8: `0.3961`
  - epoch 9: `0.4389`
  - epoch 10: `0.4580`
  - epoch 11: `0.4867`
  - epoch 12: `0.4959`
  - epoch 13: `0.5451`
  - epoch 14: `0.5558`
  - epoch 15: `0.5852`
- Best CRNN checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_15.pth`
  - best valid metric: `recog/1-N.E.D = 0.5852`
  - checkpoint size: `59442179` bytes
- Other CRNN output:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/epoch_15.pth`
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/last_checkpoint`
- SAR latest observed progress:
  - `Epoch(train) [2][2100/5261]`
  - latest loss: `loss: 4.0591`, `loss_ce: 4.0591`

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended CRNN resume command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --resume --cfg-options train_cfg.max_epochs=15 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- completed CRNN full/resume run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- SAR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`

Next step:

1. CRNN is still improving at epoch `15`; if following the planned convergence/early-stopping protocol, consider continuing it later to a higher max epoch rather than freezing epoch `15` as final.
2. Do not report CRNN as final paper metric until test-set inference and DTLR-aligned CER/AR/CR/short-bucket metrics are computed from the best checkpoint.
3. Continue monitoring SAR on GPU1.

## Latest Update 2026-05-30 01:05 Asia/Shanghai

Completed since previous status write:

- User requested continuing CRNN further in one step.
- Confirmed GPU0 is idle:
  - GPU0: `0%`, about `8 MiB`
- Confirmed CRNN resume checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/epoch_15.pth`
  - `last_checkpoint` points to this file.
- Confirmed SAR remains active on GPU1:
  - latest observed SAR progress: `Epoch(train) [2][3500/5261]`
  - latest SAR loss: `loss: 3.9384`, `loss_ce: 3.9384`
- Plan for CRNN continuation:
  - resume in the same work directory
  - append stdout to the existing `stdout.log`
  - increase `train_cfg.max_epochs` from `15` to `30`
  - keep best-checkpoint selection by `recog/1-N.E.D`

Modified files in this step:

- `experiments/notes/goal_status.md`

Current or next CRNN resume command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --resume --cfg-options train_cfg.max_epochs=30 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- CRNN full/resume run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Start CRNN resume on GPU0 to `max_epochs=30`.
2. Confirm it resumes from epoch 15 and continues to epoch 16, not restarting from epoch 1.
3. Monitor first new training log line and GPU0 process.

## Latest Update 2026-05-30 01:06 Asia/Shanghai

Completed since previous status write:

- Started CRNN continuation to `max_epochs=30` on GPU0.
- tmux session:
  - `mmocr_mthv2_crnn_gpu0_resume30_0530`
- Confirmed it resumed correctly, not restarted:
  - `Auto resumed from .../epoch_15.pth`
  - `resumed epoch: 15, iter: 78915`
  - new training progress is epoch `16`
- Confirmed CRNN process:
  - PID `3484871`
  - process: `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`
  - GPU0 memory: about `2548 MiB`
- Confirmed GPU state:
  - GPU0: active, about `86%`, `2562/24576 MiB`
  - GPU1: active, about `99%`, `22032/24576 MiB`
- Latest CRNN progress:
  - `Epoch(train) [16][ 500/5261]`
  - latest finite loss: `loss: 1.8837`, `loss_ctc: 1.8837`
- SAR remains active on GPU1.

Modified files in this step:

- `experiments/notes/goal_status.md`

Running CRNN resume command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --resume --cfg-options train_cfg.max_epochs=30 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- CRNN full/resume run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Monitor CRNN to epoch `30`, recording validation `recog/1-N.E.D` and best checkpoint changes.
2. Continue monitoring SAR on GPU1.
3. Do not start another GPU0 long run while CRNN PID `3484871` is active.

## Latest Update 2026-05-30 01:08 Asia/Shanghai

Completed since previous status write:

- Checked SAR status.
- Confirmed SAR tmux session is still active:
  - `mmocr_mthv2_sar_gpu1_0529`
- Confirmed SAR GPU process:
  - PID `3477358`
  - process: `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`
  - GPU1 memory: about `22026 MiB`
- Confirmed CRNN continuation is also active:
  - PID `3484871`
  - GPU0 memory: about `2548 MiB`
- SAR completed epoch `1` training and validation:
  - epoch 1 valid `recog/1-N.E.D`: `0.0358`
  - best checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/best_recog_1-N.E.D_epoch_1.pth`
  - epoch checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/epoch_1.pth`
- SAR is currently training epoch `2`:
  - latest observed progress: `Epoch(train) [2][3700/5261]`
  - latest loss: `loss: 3.9239`, `loss_ce: 3.9239`
  - latest ETA in log: about `2:49:23`
- Note: SAR validation is slow on this config:
  - epoch 1 validation had `685` batches.
  - each validation batch logged around `3.34s`.

Modified files in this step:

- `experiments/notes/goal_status.md`

Running training commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_full_gpu1_0529-2300
```

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --resume --cfg-options train_cfg.max_epochs=30 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- SAR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`
- CRNN full/resume run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`

Next step:

1. Continue SAR until epoch `2` validation finishes; record new `recog/1-N.E.D` and whether best checkpoint updates.
2. Continue CRNN to epoch `30`; record validation curve and best checkpoint.
3. Do not launch another long run while both GPUs are occupied.

## Latest Update 2026-05-30 01:56 Asia/Shanghai

Completed since previous status write:

- Checked CRNN epoch-30 continuation after user reported it finished.
- Confirmed CRNN tmux session `mmocr_mthv2_crnn_gpu0_resume30_0530` is no longer present.
- Confirmed GPU0 is idle:
  - GPU0: `0%`, about `8 MiB`
- Confirmed CRNN completed normally through epoch `30` validation.
- Confirmed SAR remains active on GPU1:
  - SAR PID `3477358`
  - GPU1 memory about `22026 MiB`
- CRNN validation `recog/1-N.E.D` after epoch 15:
  - epoch 16: `0.5990`
  - epoch 17: `0.6064`
  - epoch 18: `0.6222`
  - epoch 19: `0.6254`
  - epoch 20: `0.6287`
  - epoch 21: `0.6414`
  - epoch 22: `0.6427`
  - epoch 23: `0.6388`
  - epoch 24: `0.6495`
  - epoch 25: `0.6582`
  - epoch 26: `0.6633`
  - epoch 27: `0.6715`
  - epoch 28: `0.6738`
  - epoch 29: `0.6404`
  - epoch 30: `0.6526`
- Best CRNN checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_28.pth`
  - best valid metric: `recog/1-N.E.D = 0.6738`
  - checkpoint size: `70244675` bytes
- Latest CRNN epoch checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/epoch_30.pth`
- Interpretation:
  - CRNN improved substantially through epoch `28`.
  - Epochs `29` and `30` regressed from the best, so epoch `28` is the current best validation checkpoint.
  - Do not continue CRNN immediately unless explicitly exploring longer training; next useful step is test inference and DTLR-aligned metric conversion from the epoch-28 best checkpoint.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended CRNN command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py --resume --cfg-options train_cfg.max_epochs=30 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324
```

Latest log directories:

- completed CRNN full/resume run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/stdout.log`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Keep CRNN stopped for now; use epoch-28 best checkpoint for later test-set prediction and CER/AR/CR/short-bucket evaluation.
2. Continue monitoring SAR on GPU1.
3. GPU0 is available for the next comparison model only if the user asks to launch another one.

## Latest Update 2026-05-30 02:19 Asia/Shanghai

Completed since previous status write:

- User requested launching another MTHv2 comparison model on idle GPU0.
- Selected SVTR-tiny as the third MMOCR comparison baseline:
  - CRNN covers classic CTC.
  - SAR covers attention decoding.
  - SVTR covers modern visual Transformer recognition.
- Confirmed GPU state before work:
  - GPU0: idle, about `8 MiB`.
  - GPU1: active with SAR, about `22032/24576 MiB`.
- Added new SVTR MTHv2 config:
  - `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`
- Config choices:
  - `load_from = None`
  - MTHv2 charset: `data/mmocr_exports/mthv2/charset.txt`
  - train/val/test JSONs from `data/mmocr_exports/mthv2/`
  - rotate vertical line images before resizing
  - input pipeline resize: `256x64`
  - SVTR encoder image size: `[32, 256]`
  - SVTR output sequence length: `64`
  - validation metric: `OneMinusNEDMetric`
  - max epochs: `30`
- Verified config/data sample loading:
  - dictionary path is correct.
  - train ann file is correct.
  - batch size is `16`.
  - sample tensor shape after pipeline: `(3, 64, 256)`.
  - first sample target lengths are covered by the 64-step CTC output.
- SAR remains active on GPU1:
  - latest observed SAR progress: `Epoch(train) [3][1600/5261]`

Modified files in this step:

- `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`
- `experiments/notes/goal_status.md`

Current or next SVTR smoke command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-tiny_30e_mthv2.py --cfg-options train_cfg.max_epochs=1 train_cfg.val_interval=1 train_dataloader.dataset.datasets.0.indices=64 val_dataloader.dataset.datasets.0.indices=64 train_dataloader.batch_size=16 train_dataloader.num_workers=0 train_dataloader.persistent_workers=False val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False default_hooks.checkpoint.interval=-1 default_hooks.checkpoint.save_last=False load_from=None work_dir=work_dirs/smoke_mthv2_svtr_tiny_gpu0_0530-0219
```

Latest log directories:

- pending SVTR smoke: `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_tiny_gpu0_0530-0219`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- completed CRNN full run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`

Next step:

1. Run SVTR-tiny smoke on GPU0.
2. Require finite loss and successful validation before launching full SVTR training.
3. After full SVTR starts and is confirmed healthy, delete the SVTR smoke directory per the user's cleanup rule.

## Latest Update 2026-05-30 02:20 Asia/Shanghai

Completed since previous status write:

- Ran SVTR-tiny MTHv2 smoke on GPU0:
  - work dir: `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_tiny_gpu0_0530-0219`
  - train subset: `64`
  - val subset: `64`
  - batch size: `16`
  - result: completed successfully
  - training: `Epoch(train) [1][4/4]`
  - finite loss: `loss: 25.3365`, `loss_ctc: 25.3365`
  - validation: `Epoch(val) [1][4/4] recog/1-N.E.D: 0.0000`
- Updated SVTR full config:
  - `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`
  - full-run batch size changed from `16` to `64` for train/val/test.
  - cosine schedule changed to run through epoch `30` instead of ending at epoch `20`.
- SAR remains active on GPU1.

Modified files in this step:

- `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`
- `experiments/notes/goal_status.md`

Ended SVTR smoke command:

```bash
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-tiny_30e_mthv2.py --cfg-options train_cfg.max_epochs=1 train_cfg.val_interval=1 train_dataloader.dataset.datasets.0.indices=64 val_dataloader.dataset.datasets.0.indices=64 train_dataloader.batch_size=16 train_dataloader.num_workers=0 train_dataloader.persistent_workers=False val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False default_hooks.checkpoint.interval=-1 default_hooks.checkpoint.save_last=False load_from=None work_dir=work_dirs/smoke_mthv2_svtr_tiny_gpu0_0530-0219
```

Current or next SVTR full command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-tiny_30e_mthv2.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220
```

Latest log directories:

- successful SVTR smoke: `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_tiny_gpu0_0530-0219`
- pending SVTR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Launch SVTR-tiny full training on GPU0 in tmux.
2. Confirm finite loss and GPU process.
3. Delete the SVTR smoke directory after the full run is confirmed healthy.

## Latest Update 2026-05-30 02:22 Asia/Shanghai

Completed since previous status write:

- Started SVTR-tiny full MTHv2 training on GPU0.
- tmux session:
  - `mmocr_mthv2_svtr_gpu0_0530`
- Work directory:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- Confirmed SVTR process:
  - PID `3487530`
  - process: `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`
  - GPU0 memory: about `3864 MiB`
- Confirmed GPU state:
  - GPU0: active, about `94%`, `3878/24576 MiB`
  - GPU1: active with SAR, about `99%`, `22032/24576 MiB`
- Confirmed SVTR full run is healthy:
  - `Epoch(train) [1][ 100/1316] ... loss: 7.6628 loss_ctc: 7.6628`
  - `Epoch(train) [1][ 400/1316] ... loss: 6.8294 loss_ctc: 6.8294`
- Deleted SVTR smoke directory after full run was confirmed healthy:
  - `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_tiny_gpu0_0530-0219`
- Verified the smoke directory is deleted.
- SAR remains active on GPU1:
  - PID `3477358`

Modified files in this step:

- `experiments/notes/goal_status.md`
- Deleted short-run directory:
  - `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_tiny_gpu0_0530-0219`

Running SVTR command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-tiny_30e_mthv2.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220
```

Running SAR command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_full_gpu1_0529-2300
```

Latest log directories:

- SVTR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- SVTR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/stdout.log`
- SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- CRNN completed run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`

Next step:

1. Monitor SVTR epoch `1` validation and record `recog/1-N.E.D`.
2. Continue monitoring SAR on GPU1.
3. Do not start another long GPU0 run while SVTR PID `3487530` is active.

## Latest Update 2026-05-30 02:40 Asia/Shanghai

Completed since previous status write:

- User asked whether CRNN results can be converted to CER/AR/CR.
- Added conversion script:
  - `tools/eval_mmocr_textrecog_predictions.py`
- Conversion method:
  - run MMOCR `tools/test.py --save-preds` to dump per-sample predictions.
  - read the dumped prediction pkl.
  - compute character-level edit distance.
  - report `cer_micro`, `micro_ar`, `micro_cr`, insertion/deletion/substitution rates, empty prediction rate, and length buckets.
- Verified the conversion pipeline on 8 test samples:
  - prediction pkl: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_sample_0530/best_recog_1-N.E.D_epoch_28.pth_predictions.pkl`
  - sample metrics JSON: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_sample_0530/metrics_sample.json`
- The sample conversion is only a pipeline check, not a final result.

Modified files in this step:

- `tools/eval_mmocr_textrecog_predictions.py`
- `experiments/notes/goal_status.md`

Current or next evaluation command:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/test.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_28.pth --save-preds --work-dir work_dirs/eval_mthv2_crnn_epoch28_test_0530 --cfg-options test_dataloader.num_workers=0 test_dataloader.persistent_workers=False test_dataloader.batch_size=32
```

Latest log directories:

- CRNN evaluation sample: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_sample_0530`
- pending CRNN full test evaluation: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530`
- active SVTR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Run full CRNN epoch-28 best checkpoint inference on MTHv2 test.
2. Convert the full prediction pkl to CER/AR/CR.
3. Report the final CRNN test metrics and write them back here.
- Confirmed PID `3408112` is still running and not blocked:
  - state `Rsl`
  - `wchan` is `-`
  - elapsed about `01:19:49`
- Confirmed `info.txt` and `recovered_stdout_tmux.log` are still growing.

Modified files in this step:

- `experiments/notes/goal_status.md`

Current training command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Latest observed progress:

- epoch `2`, step `1740/42088`
- last observed timestamp: `2026-05-28 23:59:37`
- epoch `2` validation has not started yet.
- next expected milestone is completion of epoch `2` training segment followed by validation and a new `log.txt` row.

Next step:

1. Continue monitoring the current MTHv2 SGQ run.
2. Update this file again when epoch `2` validation writes a CER row, or earlier if the process blocks/crashes.
3. Do not launch HDRC until this MTHv2 run is complete or explicitly stopped and summarized.

## Latest Update 2026-05-29 00:01 Asia/Shanghai

Completed since previous status write:

- Resumed the active goal and re-read:
  - `experiments/notes/goal_status.md`
  - `experiments/notes/goal_plan_mthv2_hdrc.md`
  - latest logs under `logs/mthv2_sgq_short_ce_full_0528-2240`
- Confirmed the current MTHv2 SGQ full run is still in progress and must not be restarted.
- Confirmed `log.txt` still has only epoch `0` and epoch `1`; no epoch `2` validation row yet.
- Confirmed PID `3408112` is still running and not blocked:
  - state `Rsl`
  - `wchan` is `-`
  - elapsed about `01:20:42`
- Confirmed latest files are still growing:
  - `info.txt` modified at `2026-05-29 00:00`
  - `recovered_stdout_tmux.log` modified at `2026-05-29 00:00`

Modified files in this step:

- `experiments/notes/goal_status.md`

Current training command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Latest observed progress:

- epoch `2`, step `1970/42088`
- last observed timestamp: `2026-05-29 00:00:31`
- epoch `2` validation has not started yet.
- current best SGQ validation CER remains epoch `1`: `0.12201948555193866`
- MTHv2 baseline best validation CER remains better: `0.11397798822246911`

Next step:

1. Continue monitoring the current MTHv2 SGQ run.
2. Keep the stdout/stderr tmux drain sessions alive while PID `3408112` runs.
3. Update this file again at the next meaningful milestone: epoch `2` validation row, process block/crash, or training completion.
4. Do not launch HDRC or another module while this MTHv2 run is active.

## Latest Update 2026-05-29 00:03 Asia/Shanghai

Completed since previous status write:

- Waited a short monitoring window and rechecked the same MTHv2 SGQ run.
- Confirmed training continues to advance; it is not stalled.
- Confirmed PID `3408112` remains active and not blocked:
  - state `Rsl`
  - `wchan` is `-`
  - elapsed about `01:23:28`
- Confirmed GPU0 is actively used:
  - utilization `100%`
  - memory `20908/24576 MiB`
- Confirmed `info.txt` and `recovered_stdout_tmux.log` are still growing.

Modified files in this step:

- `experiments/notes/goal_status.md`

Current training command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Latest observed progress:

- epoch `2`, step `2580/42088`
- last observed timestamp: `2026-05-29 00:02:52`
- epoch `2` validation has not started yet.
- `log.txt` still contains only epoch `0` and epoch `1`.

Next step:

1. Continue monitoring until epoch `2` validation finishes and writes a new `log.txt` row, unless the process blocks or crashes first.
2. Keep the drain sessions alive while PID `3408112` runs.
3. Do not launch HDRC or any other training concurrently.

## Latest Update 2026-05-29 11:34 Asia/Shanghai

Completed since previous status write:

- Resumed the active goal and re-read:
  - `experiments/notes/goal_status.md`
  - `experiments/notes/goal_plan_mthv2_hdrc.md`
  - latest logs under `logs/mthv2_sgq_short_ce_full_0528-2240`
- Confirmed the MTHv2 SGQ full run reached epoch `11` validation and wrote all 12 rows to `log.txt`.
- Confirmed host PID `3408112` is now a zombie/defunct process, so the training command has ended and is no longer actively training.
- Confirmed latest log artifacts:
  - `logs/mthv2_sgq_short_ce_full_0528-2240/log.txt`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint.pth`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth`
  - epoch output directories `epoch_0/` through `epoch_11/`

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended training command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Current result from `log.txt`:

- best SGQ validation CER: `0.11552016232612522` at epoch `5`
- baseline MTHv2 validation CER: `0.11397798822246911`
- final epoch `11` regressed badly:
  - `test_cer_oracle_direction`: `0.49223755104084943`
  - `test_blank_pred_ratio_unscaled`: `0.9959249996849339`
- preliminary decision: MTHv2 SGQ training does not improve overall validation CER versus baseline. Still need to run the required post-training summaries before finalizing the module decision.

Next step:

1. Generate required MTHv2 SGQ post-training summaries:
   - best epoch/checkpoint details from `log.txt`
   - overall AR/CR/CER
   - clean CTC error summary
   - calibrated/decode-bias summary if applicable
   - `len=1/2` empty rates
   - length-bucket CER
   - representative error cases
2. Write the MTHv2 SGQ experiment summary under `experiments/notes/`.
3. Only after this summary is written, decide whether to run HDRC SGQ or move to Module 2. Do not start another training before the summary is complete.

## Latest Update 2026-05-29 11:36 Asia/Shanghai

Completed since previous status write:

- Checked baseline MTHv2 clean summary format and confirmed it covers all `10948` validation samples.
- Confirmed GPU is idle after the MTHv2 SGQ training:
  - GPU0 `0%`, `8 MiB`
  - GPU1 `0%`, `0 MiB`
- Confirmed the temporary SGQ stdout/stderr drain tmux sessions are no longer listed; only unrelated sessions remain.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended training command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_mth1000mth1200tkh_head_0528-0003/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --output_dir logs/mthv2_sgq_short_ce_full_0528-2240 -c config/MTHV2_dtlr_sgq_short_ce.py --save_log --options batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000
```

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Run full-validation clean CTC error analysis for the best SGQ checkpoint.
2. Run overall AR/CR/CER evaluation for the best SGQ checkpoint.
3. If clean summary is worse or ambiguous, run decode-bias sweep/summary before writing the experiment decision.

## Latest Update 2026-05-29 11:39 Asia/Shanghai

Completed since previous status write:

- Attempted full-validation clean CTC error analysis for the best SGQ checkpoint:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/analyze_ctc_errors.py -c config/MTHV2_dtlr_sgq_short_ce.py --dataset_file mth_combo --checkpoint logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --output_json logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_clean_0529.json --output_cases logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_clean_0529.jsonl --save_all_cases
```

- Result: failed before producing summary because the sandboxed run fell back to CPU and `MSDeformAttn` has no CPU implementation:
  - error: `RuntimeError: Not implemented on the CPU`
- Interpretation: execution environment issue, not an experiment result. Need rerun with host GPU access.

Modified files in this step:

- `experiments/notes/goal_status.md`

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Rerun the same clean CTC error analysis with escalated/host GPU execution.
2. After it succeeds, update this file and continue with AR/CR/CER evaluation.

## Latest Update 2026-05-29 11:48 Asia/Shanghai

Completed since previous status write:

- Reran full-validation clean CTC error analysis with host GPU access.
- Output files written:
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_clean_0529.json`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_clean_0529.jsonl`
- Full valid sample count: `10948`.

Completed command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/analyze_ctc_errors.py -c config/MTHV2_dtlr_sgq_short_ce.py --dataset_file mth_combo --checkpoint logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --output_json logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_clean_0529.json --output_cases logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_clean_0529.jsonl --save_all_cases
```

Key clean valid results:

- overall clean CER: `0.052277212763345515`
- overall empty rate: `0.029046401169163318`
- overall deletion rate: `0.026610763288856153`
- `len=1`:
  - CER `0.2697563874034462`
  - empty `0.1711229946524064`
  - deletion `0.1711229946524064`
- `len=2`:
  - CER `0.23022151898734178`
  - empty `0.022151898734177215`
  - deletion `0.12460443037974683`
- `11+`:
  - CER `0.03324255392729002`

Comparison to MTHv2 baseline clean valid:

- baseline overall clean CER `0.051956146066460804`; SGQ is slightly worse.
- baseline `len=1` empty `0.1948900772430184`; SGQ improves to `0.1711229946524064`.
- baseline `len=2` empty `0.030854430379746837`; SGQ improves to `0.022151898734177215`.
- baseline `len=1` CER `0.26737967914438504`; SGQ worsens to `0.2697563874034462`.
- baseline `len=2` CER `0.22151898734177214`; SGQ worsens to `0.23022151898734178`.

Modified files in this step:

- `experiments/notes/goal_status.md`

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Run overall AR/CR/CER evaluation for the best SGQ checkpoint.
2. Run decode-bias sweep/summary if needed to decide whether SGQ combines usefully with calibration.
3. Write the MTHv2 SGQ experiment summary.

## Latest Update 2026-05-29 12:30 Asia/Shanghai

Completed since previous status write:

- Confirmed the overall AR/CR/CER evaluation completed after the tool session handle was lost.
- Output file written:
  - `logs/mthv2_sgq_short_ce_full_0528-2240/chinese_micro_valid_0529.json`
- Confirmed no active `eval_chinese_micro.py` or `analyze_ctc_errors.py` process remains.
- Confirmed GPU is idle:
  - GPU0 `0%`, `8 MiB`
  - GPU1 `0%`, `0 MiB`

Completed command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/eval_chinese_micro.py --dataset mth_combo --mode val --weights logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth --config config/MTHV2_dtlr_sgq_short_ce.py --device cuda:0 --new_class_embedding --new_label_enc --output_json logs/mthv2_sgq_short_ce_full_0528-2240/chinese_micro_valid_0529.json
```

Overall AR/CR/CER results:

- samples: `10948`
- macro AR: `0.8844746886079347`
- macro CR: `0.886798645751378`
- macro CER: `0.11552531139206534`
- micro AR: `0.9476850146840798`
- micro CR: `0.9490353834386244`
- micro CER: `0.05231498531592019`
- edit totals:
  - chars `105897`
  - insertions `143`
  - deletions `2742`
  - substitutions `2655`

Modified files in this step:

- `experiments/notes/goal_status.md`

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Run decode-bias sweep for the SGQ checkpoint using the same MTHv2 validation split.
2. Generate calibrated summary for the best sweep setting.
3. Write the MTHv2 SGQ experiment summary under `experiments/notes/`.

## Latest Update 2026-05-29 12:43 Asia/Shanghai

Completed since previous status write:

- Ran full-validation decode-bias sweep for the SGQ checkpoint on MTHv2 valid.
- Output file written:
  - `logs/mthv2_sgq_short_ce_full_0528-2240/decode_bias_sweep_valid_0529.json`
- Sweep covered 24 settings:
  - `blank_bias`: `-2.0 -1.6 -1.2 -0.8 -0.4 0.0`
  - `nonblank_bias`: `0.0 0.4 0.8 1.0`
  - `ratio_nonblank_bias`: `0.0`

Completed command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr_sgq_short_ce.py --dataset_file mth_combo --checkpoint logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_biases -2.0 -1.6 -1.2 -0.8 -0.4 0.0 --nonblank_biases 0.0 0.4 0.8 1.0 --ratio_nonblank_biases 0.0 --output_json logs/mthv2_sgq_short_ce_full_0528-2240/decode_bias_sweep_valid_0529.json
```

Best SGQ decode-bias result:

- setting:
  - `blank_bias=-1.6`
  - `nonblank_bias=1.0`
  - `ratio_nonblank_bias=0.0`
- overall CER: `0.044553`
- empty rate: `0.008677`
- deletion rate: `0.006837`
- substitution rate: `0.034902`
- length-bin CER from sweep printout:
  - `len=1`: `0.235294`
  - `len=2`: `0.202927`
  - `11+`: `0.027958`

Comparison to MTHv2 baseline best decode-bias sweep:

- baseline best: `blank_bias=-2.0`, `nonblank_bias=1.0`, overall CER `0.04561980037205964`
- SGQ calibrated best is better overall than baseline calibrated best in this sweep grid.
- SGQ calibrated `len=1/2` CER is worse than baseline calibrated `len=1/2`:
  - baseline `len=1`: `0.22281639928698752`
  - SGQ `len=1`: `0.235294`
  - baseline `len=2`: `0.19026898734177214`
  - SGQ `len=2`: `0.202927`

Modified files in this step:

- `experiments/notes/goal_status.md`

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Generate calibrated CTC summary/cases for the best SGQ sweep setting:
   - `blank_bias=-1.6`
   - `nonblank_bias=1.0`
2. Write the MTHv2 SGQ experiment summary.

## Latest Update 2026-05-29 12:54 Asia/Shanghai

Completed since previous status write:

- Generated full-validation calibrated CTC summary and cases for the best SGQ sweep setting.
- Output files written:
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_bias_b-16_nb10_0529.json`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_bias_b-16_nb10_0529.jsonl`

Completed command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/analyze_ctc_errors.py -c config/MTHV2_dtlr_sgq_short_ce.py --dataset_file mth_combo --checkpoint logs/mthv2_sgq_short_ce_full_0528-2240/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_bias -1.6 --nonblank_bias 1.0 --ratio_nonblank_bias 0.0 --output_json logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_bias_b-16_nb10_0529.json --output_cases logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_bias_b-16_nb10_0529.jsonl --save_all_cases
```

Best calibrated SGQ valid results:

- setting:
  - `blank_bias=-1.6`
  - `nonblank_bias=1.0`
  - `ratio_nonblank_bias=0.0`
- overall CER: `0.04455272576182517`
- empty rate: `0.008677383997077091`
- deletion rate: `0.006836832016015562`
- insertion rate: `0.0028140551668130354`
- substitution rate: `0.03490183857899657`
- `len=1`:
  - CER `0.23529411764705882`
  - empty `0.055852644087938205`
  - deletion `0.055852644087938205`
- `len=2`:
  - CER `0.20292721518987342`
  - empty `0.0`
  - deletion `0.029272151898734177`
- `11+`:
  - CER `0.02795789564691134`

Modified files in this step:

- `experiments/notes/goal_status.md`

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Extract representative error cases from clean and calibrated JSONL outputs.
2. Write MTHv2 SGQ experiment summary under `experiments/notes/`.
3. Decide whether Module 1 should continue to HDRC or count as no-improvement on MTHv2 and move to Module 2.

## Latest Update 2026-05-29 13:02 Asia/Shanghai

Completed since previous status write:

- Extracted key metrics and representative errors from:
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_clean_0529.json`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_summary_valid_bias_b-16_nb10_0529.json`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_clean_0529.jsonl`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/ctc_error_cases_valid_bias_b-16_nb10_0529.jsonl`
- Wrote MTHv2 SGQ experiment summary:
  - `experiments/notes/mthv2_sgq_short_ce_summary_0529.md`

Summary decision:

- Module 1 SGQ on MTHv2 is mixed but not a clean success for the original short-text target.
- Clean inference:
  - improves len=1/2 empty and deletion rates,
  - regresses overall clean CER and len=1/2 CER.
- Calibrated inference:
  - improves overall calibrated CER versus MTHv2 baseline calibrated best (`0.04455272576182517` vs `0.04561980037205964`),
  - still regresses len=1/2 CER versus calibrated baseline.
- Count SGQ as a no-improvement module for the original short-text objective on MTHv2.
- Recommendation recorded in summary:
  - do not spend a full HDRC SGQ training slot unless the objective is broadened to overall calibrated CER;
  - move to Module 2, Short-Bucket Decode Calibration.

Modified files in this step:

- `experiments/notes/goal_status.md`
- `experiments/notes/mthv2_sgq_short_ce_summary_0529.md`

Training command status:

- MTHv2 SGQ full training has ended.
- No active training or evaluation process is currently required before starting Module 2 work.

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Update the goal plan with Module 1 MTHv2 result and Module 2 as the active next module.
2. Start Module 2 as a switchable evaluation/decode calibration module, keeping default decode behavior unchanged.
3. Smoke-test Module 2 on a small MTHv2 valid subset before running full MTHv2/HDRC calibrated summaries.

## Latest Update 2026-05-29 13:04 Asia/Shanghai

Completed since previous status write:

- Updated `experiments/notes/goal_plan_mthv2_hdrc.md`:
  - Module 1 SGQ now records the completed MTHv2 result and summary path.
  - Module 1 SGQ is marked as one no-improvement module for the original short-text objective on MTHv2.
  - HDRC SGQ is not recommended as the next full training run based on MTHv2 evidence.
  - Module 2 Short-Bucket Decode Calibration is marked as the active next module.

Modified files in this step:

- `experiments/notes/goal_status.md`
- `experiments/notes/goal_plan_mthv2_hdrc.md`

Training command status:

- No active training.
- No active evaluation process.

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Inspect existing CTC calibration code paths.
2. Implement or expose Module 2 as a switchable evaluation/decode calibration path with baseline defaults unchanged.
3. Smoke-test on a small MTHv2 subset before full valid summaries.

## Latest Update 2026-05-29 13:07 Asia/Shanghai

Completed since previous status write:

- Inspected existing Module 2 code paths:
  - `util/ctc_decoding.py`
  - `tools/analyze_ctc_errors.py`
  - `tools/sweep_ctc_decode_bias.py`
  - `tools/eval_chinese_micro.py`
- Confirmed CTC calibration is already switchable:
  - default `blank_bias=0.0`, `nonblank_bias=0.0`, `ratio_nonblank_bias=0.0`
  - default path returns `pred_probs` unchanged.
- Ran Module 2 unit tests:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_ctc_eval_utils.py
```

- Result:
  - `Ran 11 tests in 0.019s`
  - `OK`

Modified files in this step:

- `experiments/notes/goal_status.md`

Training command status:

- No active training.
- No active full evaluation process.

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Run a small MTHv2 decode-bias sweep smoke with the baseline checkpoint.
2. If smoke passes, run or reuse full MTHv2 baseline calibration summary and run HDRC baseline decode-bias sweep.

## Latest Update 2026-05-29 13:09 Asia/Shanghai

Completed since previous status write:

- Ran Module 2 MTHv2 decode-bias sweep smoke on 10 validation samples.
- Output file written:
  - `logs/mthv2_module2_decode_calibration_smoke_0529.json`

Completed command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 10 --new_class_embedding --blank_biases 0.0 -1.0 --nonblank_biases 0.0 1.0 --ratio_nonblank_biases 0.0 --output_json logs/mthv2_module2_decode_calibration_smoke_0529.json
```

Smoke result:

- command exited `0`
- loaded MTHv2 valid split with total `10948`, evaluated first `10`
- generated 4 sweep rows
- best smoke CER `0.005882`

Modified files in this step:

- `experiments/notes/goal_status.md`

Training command status:

- No active training.
- No active full evaluation process.

Latest log directory:

- `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Reuse existing MTHv2 full baseline decode-bias sweep:
   - `logs/mthv2_mth1000mth1200tkh_full_0528-0957/decode_bias_sweep_valid_0528.json`
2. Run HDRC baseline full decode-bias sweep on valid.
3. Generate calibrated HDRC summary for the best HDRC sweep setting.

## Latest Update 2026-05-29 13:13 Asia/Shanghai

Completed since previous status write:

- Found existing HDRC baseline full decode-bias sweep:
  - `logs/mth1000mth1200pre_hdrcft_full_0527-1732/decode_bias_sweep_valid_0527.json`
- Sweep covers `80` settings.
- Best HDRC valid settings are tied; selected the first best setting for summary:
  - `blank_bias=-2.0`
  - `nonblank_bias=0.4`
  - `ratio_nonblank_bias=0.0`
- Generated HDRC valid calibrated CTC summary/cases for the selected best setting.
- Output files written:
  - `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_bias_b-20_nb04_0529.json`
  - `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_cases_valid_bias_b-20_nb04_0529.jsonl`

Completed command:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/analyze_ctc_errors.py -c config/MTH1000_dtlr.py --dataset_file mth1000 --checkpoint logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 20000 --new_class_embedding --blank_bias -2.0 --nonblank_bias 0.4 --ratio_nonblank_bias 0.0 --output_json logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_bias_b-20_nb04_0529.json --output_cases logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_cases_valid_bias_b-20_nb04_0529.jsonl --save_all_cases --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg
```

HDRC calibrated valid result:

- samples: `2854`
- overall CER: `0.12318806364795316`
- empty rate: `0.008409250175192713`
- deletion rate: `0.04934132867463053`
- insertion rate: `0.010293214977099957`
- substitution rate: `0.06355351999622268`
- `len=1`:
  - CER `0.12352941176470589`
  - empty `0.047058823529411764`
  - deletion `0.047058823529411764`
- `len=2`:
  - CER `0.08728813559322034`
  - empty `0.0`
  - deletion `0.027966101694915254`
- `11+`:
  - CER `0.14687396625868343`

Comparison to HDRC clean baseline:

- clean overall CER `0.13437839369186458` -> calibrated `0.12318806364795316`
- clean empty `0.017869656622284513` -> calibrated `0.008409250175192713`
- clean deletion `0.0863119127437556` -> calibrated `0.04934132867463053`
- clean `len=1` empty `0.09607843137254903` -> calibrated `0.047058823529411764`
- clean `len=2` empty `0.003389830508474576` -> calibrated `0.0`

Modified files in this step:

- `experiments/notes/goal_status.md`

Training command status:

- No active training.
- No active evaluation process.

Latest log directories:

- MTHv2 Module 2 evidence: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- HDRC Module 2 evidence: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`

Next step:

1. Extract representative Module 2 error cases.
2. Write `experiments/notes/module2_decode_calibration_summary_0529.md`.
3. Decide whether Module 2 satisfies the goal and whether a third module is needed.

## Latest Update 2026-05-29 13:23 Asia/Shanghai

Completed since previous status write:

- Extracted representative Module 2 error cases for MTHv2 and HDRC.
- Wrote Module 2 summary:
  - `experiments/notes/module2_decode_calibration_summary_0529.md`
- Updated goal plan:
  - `experiments/notes/goal_plan_mthv2_hdrc.md`

Module 2 decision:

- Short-Bucket Decode Calibration is useful and satisfies the current goal on both target datasets.
- MTHv2:
  - overall CER improved from `0.051956146066460804` to `0.04561980037205964`
  - `len=1` empty improved from `0.1948900772430184` to `0.0451574569221628`
  - `len=2` empty improved from `0.030854430379746837` to `0.0015822784810126582`
  - `len=1/2` CER also improved
- HDRC:
  - overall CER improved from `0.13437839369186458` to `0.12318806364795316`
  - `len=1` empty improved from `0.09607843137254903` to `0.047058823529411764`
  - `len=2` empty improved from `0.003389830508474576` to `0.0`
  - `len=1/2` CER also improved
- No additional full training is needed for the current goal unless a stricter target is set for remaining substitution/over-activation errors.

Modified files in this step:

- `experiments/notes/goal_status.md`
- `experiments/notes/goal_plan_mthv2_hdrc.md`
- `experiments/notes/module2_decode_calibration_summary_0529.md`

Training command status:

- No active training.
- No active evaluation process.

Latest relevant log directories:

- MTHv2 Module 2 evidence: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- HDRC Module 2 evidence: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`
- MTHv2 SGQ run: `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

1. Verify final file state and key artifacts.
2. If all required artifacts are present, report the current goal result.

## Latest Update 2026-05-29 16:01 Asia/Shanghai

Completed since previous status write:

- Re-read the required resume files:
  - `experiments/notes/goal_status.md`
  - `experiments/notes/goal_plan_mthv2_hdrc.md`
  - latest relevant logs under `logs/`
- Re-checked the completed MTHv2 SGQ training log:
  - `logs/mthv2_sgq_short_ce_full_0528-2240/log.txt`
  - final row is epoch `11`
  - best SGQ validation CER remains epoch `5`: `0.11552016232612522`
  - baseline MTHv2 validation CER remains better: `0.11397798822246911`
- Confirmed key Module 1 and Module 2 artifacts exist:
  - `experiments/notes/mthv2_sgq_short_ce_summary_0529.md`
  - `experiments/notes/module2_decode_calibration_summary_0529.md`
  - `logs/mthv2_mth1000mth1200tkh_full_0528-0957/decode_bias_sweep_valid_0528.json`
  - `logs/mth1000mth1200pre_hdrcft_full_0527-1732/decode_bias_sweep_valid_0527.json`
  - `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_bias_b-20_nb04_0529.json`
  - `logs/mthv2_sgq_short_ce_full_0528-2240/decode_bias_sweep_valid_0529.json`
- Final verification command completed:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_ctc_eval_utils.py tests/test_sgq_short_query_loss.py
```

Verification result:

- `Ran 16 tests in 0.989s`
- `OK`

Modified files in this step:

- `experiments/notes/goal_status.md`

Training/evaluation command status:

- No active full training is expected for the current goal.
- The MTHv2 SGQ full training command has ended and was summarized.
- The Module 2 decode calibration evaluation commands have ended and were summarized.

Latest relevant log directories:

- MTHv2 Module 2 evidence: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- HDRC Module 2 evidence: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`
- MTHv2 SGQ Module 1 run: `logs/mthv2_sgq_short_ce_full_0528-2240`

Current goal conclusion:

- Module 1 SGQ counts as one no-improvement module for the original short-text objective.
- Module 2 Short-Bucket Decode Calibration satisfies the current goal on both MTHv2 and HDRC:
  - MTHv2 overall CER, `len=1/2` CER, and `len=1/2` empty rates all improved.
  - HDRC overall CER, `len=1/2` CER, and `len=1/2` empty rates all improved.
- No CHDAC, detection, stage-1, data deletion, or concurrent full training was used for the completed goal work.

Next step:

- No further module is required for the current goal.
- If a future resume starts a stricter follow-up objective, first read this file, `experiments/notes/goal_plan_mthv2_hdrc.md`, and:
  - `experiments/notes/module2_decode_calibration_summary_0529.md`
  - latest logs under `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
  - latest logs under `logs/mth1000mth1200pre_hdrcft_full_0527-1732`

## Latest Update 2026-05-29 16:08 Asia/Shanghai

Completed since previous status write:

- Completed a stricter completion audit against the requirement to keep overall `AR/CR/CER` non-regressing.
- Added explicit overall AR/CR rows to Module 2 summary for both datasets, computed from the same CTC edit-rate summaries:
  - `AR = 1 - (insertion rate + deletion rate + substitution rate)`
  - `CR = 1 - (deletion rate + substitution rate)`
- Updated the goal plan Module 2 section with the same AR/CR evidence.

Module 2 overall metric evidence:

- MTHv2:
  - AR `0.9480438539335392` -> `0.9543801996279404`
  - CR `0.9502724345354708` -> `0.9582141137142696`
  - CER `0.051956146066460804` -> `0.04561980037205964`
- HDRC:
  - AR `0.8656216063081354` -> `0.8768119363520468`
  - CR `0.8694461494877001` -> `0.8871051513291468`
  - CER `0.13437839369186458` -> `0.12318806364795316`

Modified files in this step:

- `experiments/notes/goal_status.md`
- `experiments/notes/goal_plan_mthv2_hdrc.md`
- `experiments/notes/module2_decode_calibration_summary_0529.md`

Training/evaluation command status:

- No active training.
- No active evaluation process.

Latest relevant log directories:

- MTHv2 Module 2 evidence: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- HDRC Module 2 evidence: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`
- MTHv2 SGQ Module 1 run: `logs/mthv2_sgq_short_ce_full_0528-2240`

Next step:

- Final verification is complete for the current goal.
- No additional module or full training is required unless a future objective asks for a stricter follow-up target.

## Latest Update 2026-05-30 02:45 Asia/Shanghai

Completed since previous status write:

- Completed full CRNN epoch-28 best-checkpoint inference on the MTHv2 test split.
- Converted the MMOCR prediction dump to DTLR-aligned character-level metrics: CER, AR, CR, insertion/deletion/substitution rates, empty prediction rate, and length buckets.
- Confirmed this is not an algebraic conversion from MMOCR `1-N.E.D`; it is recomputed from per-sample predictions and ground truth.
- MMOCR test metric from `tools/test.py`:
  - `recog/1-N.E.D`: `0.6948`
- Converted CRNN MTHv2 test metrics:
  - samples: `10455`
  - `cer_micro`: `0.27257511010538327`
  - `micro_ar`: `0.7274248898946167`
  - `micro_cr`: `0.7381315280102485`
  - `empty_pred_rate`: `0.00009564801530368245`
  - `ins_rate`: `0.010706638115631691`
  - `del_rate`: `0.11089084839587444`
  - `sub_rate`: `0.15097762359387712`
- Key CRNN test length buckets:
  - `len=1`: samples `1331`, CER `0.44102178812922616`, empty `0.0007513148009015778`
  - `len=2`: samples `1032`, CER `0.3817829457364341`, empty `0.0`
  - `3-5`: samples `1272`, CER `0.3789079700572435`, empty `0.0`
  - `6-10`: samples `579`, CER `0.345508166969147`, empty `0.0`
  - `11+`: samples `6241`, CER `0.2593183788240766`, empty `0.0`
- Checked active comparison runs:
  - SAR is still running on GPU1, PID `3477358`; epoch `2` validation reached `recog/1-N.E.D: 0.0801`, then training epoch `3`.
  - SVTR-tiny is still running on GPU0, PID `3487530`; latest observed best validation is epoch `11`, `recog/1-N.E.D: 0.7349`, and epoch `12` training is active.

Modified files in this step:

- `tools/eval_mmocr_textrecog_predictions.py`
- `experiments/notes/goal_status.md`

Ended CRNN evaluation/conversion commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/test.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_28.pth --save-preds --work-dir work_dirs/eval_mthv2_crnn_epoch28_test_0530 --cfg-options test_dataloader.num_workers=0 test_dataloader.persistent_workers=False test_dataloader.batch_size=32
```

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/eval_mmocr_textrecog_predictions.py --predictions /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/best_recog_1-N.E.D_epoch_28.pth_predictions.pkl --output_json /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_metrics.json --output_cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_cases.jsonl
```

Currently running training commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_full_gpu1_0529-2300
```

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-tiny_30e_mthv2.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220
```

Latest relevant log directories and files:

- CRNN full training: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324`
- CRNN best checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_vertical_full_gpu0_0529-2324/best_recog_1-N.E.D_epoch_28.pth`
- CRNN test evaluation: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530`
- CRNN converted metrics JSON: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_metrics.json`
- CRNN converted cases JSONL: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_cases.jsonl`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- active SVTR-tiny full run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`

Next step:

1. Report the CRNN converted MTHv2 test metrics to the user.
2. Continue monitoring SAR and SVTR-tiny; do not restart CRNN or repeat its completed test conversion.
3. When SAR or SVTR finishes, compute the same CER/AR/CR conversion from their best checkpoints before comparing against DTLR.

## Latest Update 2026-05-30 02:49 Asia/Shanghai

Completed since previous status write:

- User asked whether there are visualization images for the CRNN result.
- Added a visualization helper script:
  - `tools/visualize_mmocr_textrecog_predictions.py`
- The script reads the converted CRNN case JSONL, MMOCR test annotation JSON, and original line images, then creates PNG contact sheets for:
  - top error cases
  - `len=1` errors
  - `len=2` errors
  - low-error/good examples
- First attempted to write the visualization directory under the MMOCR eval work dir:
  - `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test`
  - result: failed with `OSError: [Errno 30] Read-only file system` because current sandbox can write only under `/home/ubuntu/DTLR` and `/tmp`.

Modified files in this step:

- `tools/visualize_mmocr_textrecog_predictions.py`
- `experiments/notes/goal_status.md`

Ended visualization command:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/visualize_mmocr_textrecog_predictions.py --cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_cases.jsonl --ann /home/ubuntu/mmocr/data/mmocr_exports/mthv2/textrecog_test.json --data_root /home/ubuntu/mmocr/data --output_dir /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test --rows 24
```

Latest relevant log directories:

- CRNN converted metrics: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530`
- planned visualization output: `debug_vis/mmocr_crnn_epoch28_test_0530`
- active SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- active SVTR-tiny full run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`

Next step:

1. Regenerate the CRNN visualization sheets under writable `debug_vis/mmocr_crnn_epoch28_test_0530`.
2. Verify the PNG files exist and have nonzero dimensions.
3. Report the image paths to the user.

## Latest Update 2026-05-30 02:51 Asia/Shanghai

Completed since previous status write:

- The first writable visualization run produced `debug_vis/mmocr_crnn_epoch28_test_0530/top_errors.png`, then became too slow while creating the `len=1` sheet.
- Root cause: the script drew only the first `--rows` cases but allocated the PNG canvas height from the full selected case list.
- Stopped the slow visualization process:
  - PID `3490095`
  - command: `kill -TERM 3490095`
- Fixed `tools/visualize_mmocr_textrecog_predictions.py` so each sheet allocates canvas height from `cases[:rows]`.

Modified files in this step:

- `tools/visualize_mmocr_textrecog_predictions.py`
- `experiments/notes/goal_status.md`

Ended visualization command:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/visualize_mmocr_textrecog_predictions.py --cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_cases.jsonl --ann /home/ubuntu/mmocr/data/mmocr_exports/mthv2/textrecog_test.json --data_root /home/ubuntu/mmocr/data --output_dir debug_vis/mmocr_crnn_epoch28_test_0530 --rows 24
```

Latest visualization output:

- partial output exists: `debug_vis/mmocr_crnn_epoch28_test_0530/top_errors.png`

Current training status:

- SAR remains active on GPU1 from `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`.
- SVTR-tiny remains active on GPU0 from `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`.

Next step:

1. Rerun the fixed visualization command.
2. Verify all expected PNG sheets exist.
3. Report the visualization paths to the user.

## Latest Update 2026-05-30 02:53 Asia/Shanghai

Completed since previous status write:

- Reran the fixed CRNN visualization command successfully.
- Generated four PNG contact sheets under:
  - `debug_vis/mmocr_crnn_epoch28_test_0530`
- Verified each PNG opens and has nonzero dimensions:
  - `top_errors.png`: `(1254, 8718)`, `408741` bytes
  - `len1_errors.png`: `(1254, 8718)`, `291508` bytes
  - `len2_errors.png`: `(1254, 8718)`, `538763` bytes
  - `good_examples.png`: `(1254, 8718)`, `1173801` bytes
- Opened `top_errors.png` once for visual sanity check; it shows original line image thumbnails with GT/PRED text and per-case CER/I/D/S metadata.
- Checked GPU status:
  - GPU0 remains active with SVTR-tiny, about `3878/24576 MiB`.
  - GPU1 remains active with SAR, about `22032/24576 MiB`.

Modified files in this step:

- `tools/visualize_mmocr_textrecog_predictions.py`
- `experiments/notes/goal_status.md`

Ended visualization command:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/visualize_mmocr_textrecog_predictions.py --cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_cases.jsonl --ann /home/ubuntu/mmocr/data/mmocr_exports/mthv2/textrecog_test.json --data_root /home/ubuntu/mmocr/data --output_dir debug_vis/mmocr_crnn_epoch28_test_0530 --rows 24
```

Latest visualization outputs:

- `debug_vis/mmocr_crnn_epoch28_test_0530/top_errors.png`
- `debug_vis/mmocr_crnn_epoch28_test_0530/len1_errors.png`
- `debug_vis/mmocr_crnn_epoch28_test_0530/len2_errors.png`
- `debug_vis/mmocr_crnn_epoch28_test_0530/good_examples.png`
- `debug_vis/mmocr_crnn_epoch28_test_0530/index.json`

Current training status:

- SAR remains active on GPU1 from `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`.
- SVTR-tiny remains active on GPU0 from `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`.

Next step:

1. Report the CRNN visualization image paths to the user.
2. Continue monitoring SAR and SVTR-tiny; when either finishes, convert its best checkpoint to CER/AR/CR and generate comparable visualization if needed.

## Latest Update 2026-05-30 02:59 Asia/Shanghai

Completed since previous status write:

- User requested moving only the newly generated MMOCR experiment visualization files into the MMOCR experiment directory.
- Created target directory:
  - `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test`
- Moved the generated CRNN visualization files from:
  - `debug_vis/mmocr_crnn_epoch28_test_0530`
- Moved files:
  - `top_errors.png`
  - `len1_errors.png`
  - `len2_errors.png`
  - `good_examples.png`
  - `index.json`
- Verified the source directory no longer contains files.
- Verified the destination contains exactly the moved visualization outputs:
  - `top_errors.png`: `408741` bytes
  - `len1_errors.png`: `291508` bytes
  - `len2_errors.png`: `538763` bytes
  - `good_examples.png`: `1173801` bytes
  - `index.json`: `495` bytes

Modified files in this step:

- `experiments/notes/goal_status.md`
- moved generated files from `debug_vis/mmocr_crnn_epoch28_test_0530/` to `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/`

Ended commands:

```bash
mkdir -p /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test
```

```bash
mv debug_vis/mmocr_crnn_epoch28_test_0530/top_errors.png debug_vis/mmocr_crnn_epoch28_test_0530/len1_errors.png debug_vis/mmocr_crnn_epoch28_test_0530/len2_errors.png debug_vis/mmocr_crnn_epoch28_test_0530/good_examples.png debug_vis/mmocr_crnn_epoch28_test_0530/index.json /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/
```

Latest visualization outputs:

- `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/top_errors.png`
- `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/len1_errors.png`
- `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/len2_errors.png`
- `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/good_examples.png`
- `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/index.json`

Current training status:

- SAR remains active on GPU1 from `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`.
- SVTR-tiny remains active on GPU0 from `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`.

Next step:

1. Report the corrected MMOCR visualization paths to the user.
2. Continue monitoring SAR and SVTR-tiny.

## Latest Update 2026-05-30 03:01 Asia/Shanghai

Completed since previous status write:

- User asked what `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_sample_0530` is.
- Inspected the directory and confirmed it is only the first small CRNN evaluation/conversion pipeline check, not the formal full test result.
- Directory contents include:
  - `best_recog_1-N.E.D_epoch_28.pth_predictions.pkl`: `3101` bytes
  - `metrics_sample.json`: `1148` bytes
  - `cases_sample.jsonl`: `1785` bytes
  - copied config and MMOCR log files.
- `metrics_sample.json` confirms:
  - samples: `8`
  - `cer_micro`: `0.7738095238095238`
  - this was a pipeline sanity check only and should not be used in the paper or comparison table.
- The valid formal CRNN test result remains:
  - `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530`
  - metrics: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/crnn_epoch28_test_metrics.json`
  - visualizations: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/vis_crnn_epoch28_test/`

Modified files in this step:

- `experiments/notes/goal_status.md`

Training/evaluation command status:

- No new training or evaluation was started for this question.
- SAR and SVTR-tiny are still the active MMOCR training runs from previous status entries.

Latest relevant log directories:

- sample-only CRNN check: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_sample_0530`
- formal CRNN full test evaluation: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530`

Next step:

1. Tell the user that the `_sample_` directory is a disposable 8-sample sanity check.
2. Use only `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530` for formal CRNN comparison evidence.

## Latest Update 2026-05-30 03:15 Asia/Shanghai

Completed since previous status write:

- User asked how the remaining two active MMOCR runs are doing.
- Checked process state, GPU state, stdout logs, validation metric curves, and current best checkpoints for SAR and SVTR-tiny.
- Both runs are still active:
  - SAR PID `3477358`, GPU1, about `22032/24576 MiB`
  - SVTR-tiny PID `3487530`, GPU0, about `3878/24576 MiB`

Current SAR status:

- run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- config: `/home/ubuntu/mmocr/configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py`
- validation curve so far:
  - epoch `1`: `recog/1-N.E.D = 0.0358`
  - epoch `2`: `recog/1-N.E.D = 0.0801`
- current best checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/best_recog_1-N.E.D_epoch_2.pth`
- latest observed progress:
  - epoch `3` validation is running
  - latest observed validation batch: `[400/685]` at `2026-05-30 03:15`
- interpretation:
  - SAR is improving but still very weak at the moment.
  - It is not yet close to CRNN's valid `1-N.E.D` peak (`0.6738`) or SVTR-tiny's current best.
  - Continue to at least finish epoch `3` validation before making a stop/continue decision.

Current SVTR-tiny status:

- run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- config: `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`
- validation curve highlights:
  - epoch `8`: `0.5901`
  - epoch `9`: `0.6685`
  - epoch `10`: `0.6894`
  - epoch `14`: `0.7970`
  - epoch `18`: `0.8222`
  - epoch `19`: `0.8393`
  - epoch `21`: `0.8457`
  - epoch `22`: `0.8528`
  - epoch `24`: `0.8550`
  - epoch `25`: `0.8613`
- current best checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/best_recog_1-N.E.D_epoch_25.pth`
- latest observed progress:
  - epoch `26` training is active
  - latest observed train progress: `[26][1000/1316]`
- interpretation:
  - SVTR-tiny is already stronger than CRNN on validation by MMOCR `1-N.E.D`:
    - CRNN best valid: `0.6738`
    - SVTR-tiny current best valid: `0.8613`
  - The formal comparison still needs test-set prediction export and CER/AR/CR conversion after training finishes.

Modified files in this step:

- `experiments/notes/goal_status.md`

Training/evaluation command status:

- No new training or evaluation was started.
- Existing SAR and SVTR-tiny training processes continue running.

Latest relevant log directories:

- SAR active run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- SAR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`
- SVTR-tiny active run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- SVTR-tiny stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/stdout.log`

Next step:

1. Wait for SVTR-tiny to finish the planned `30` epochs, then run test-set prediction export and CER/AR/CR conversion from the best checkpoint.
2. Continue monitoring SAR; once epoch `3` validation completes, decide whether it is worth continuing or should be stopped as a weak baseline.

## Latest Update 2026-05-30 03:18 Asia/Shanghai

Completed since previous status write:

- User asked whether the CRNN run horizontally rotated the dataset.
- Inspected the CRNN MTHv2 config:
  - `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`
- Confirmed CRNN uses an on-the-fly data pipeline transform, not a permanent dataset rewrite:
  - train pipeline lines `20-27`: `ConditionApply` + `ImgAugWrapper Rot90(k=1)`
  - test pipeline lines `42-49`: same transform
  - condition: `results['img_shape'][1] < results['img_shape'][0]`
- Interpretation:
  - for vertical line images whose width is smaller than height, the image is rotated before CRNN resizing.
  - original files and annotations under `/home/ubuntu/mmocr/data` are not modified.
  - labels are not rewritten; only the loaded image tensor is rotated for CRNN.

Modified files in this step:

- `experiments/notes/goal_status.md`

Training/evaluation command status:

- No new training or evaluation was started.
- Existing SAR and SVTR-tiny training runs continue from previous status entries.

Latest relevant config:

- `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`

Next step:

1. Explain to the user that CRNN's input pipeline rotates vertical images horizontally on the fly, because CRNN/CTC expects the sequence along the width axis.

## Latest Update 2026-05-30 03:19 Asia/Shanghai

Completed since previous status write:

- User asked whether rotating the CRNN input can make image text order mismatch the original label.
- Verified the actual `imgaug.augmenters.Rot90(k=1, keep_size=False)` direction using a small matrix:
  - input rows top-to-bottom: `[1, 2, 3]`
  - output left-to-right became `[3, 2, 1]`
- Interpretation:
  - `Rot90(k=1)` places the original top of the vertical line on the right side after rotation.
  - If MTHv2 labels are ordered top-to-bottom, then the current CRNN/SVTR rotation direction can make the visual left-to-right time order correspond to bottom-to-top.
  - That is a real possible mismatch for CTC-style left-to-right recognizers.
- Consequence:
  - The current CRNN result should be treated as a preliminary baseline that may be underestimating CRNN.
  - For a cleaner formal baseline, use the opposite rotation direction, likely `Rot90(k=3)`, or keep `k=1` only if labels are intentionally bottom-to-top.

Modified files in this step:

- `experiments/notes/goal_status.md`

Verification command:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python - <<'PY'
import numpy as np
import imgaug.augmenters as iaa
img = np.array([[1, 1], [2, 2], [3, 3]], dtype=np.uint8)
out = iaa.Rot90(k=1, keep_size=False)(image=img)
print(out)
PY
```

Training/evaluation command status:

- No new model training was started by this check.
- Existing SAR and SVTR-tiny training runs continue from previous status entries.

Next step:

1. Tell the user that the concern is valid: current `k=1` rotation may reverse top-to-bottom reading order.
2. Recommend rerunning formal CRNN/SVTR rotation-sensitive baselines with `Rot90(k=3)` after current active runs are handled, unless dataset labels are confirmed bottom-to-top.

## Latest Update 2026-05-30 03:25 Asia/Shanghai

Completed since previous status write:

- User challenged why CRNN/SVTR can still have effective accuracy if `Rot90(k=1)` may reverse the visual reading order.
- Performed a deeper direction/order check instead of assuming the previous conclusion was sufficient.
- Generated orientation diagnostic images for selected MTHv2 test samples:
  - `debug_vis/orientation_check_0530/idx_0_orientation.png`
  - `debug_vis/orientation_check_0530/idx_1_orientation.png`
  - `debug_vis/orientation_check_0530/idx_660_orientation.png`
  - `debug_vis/orientation_check_0530/idx_1331_orientation.png`
  - `debug_vis/orientation_check_0530/idx_3302_orientation.png`
- Visual check on `idx_0_orientation.png`:
  - original line image reads top-to-bottom and matches GT prefix `北京三時...`
  - therefore the JSON labels are normal top-to-bottom for this sample.
- Recomputed CRNN test CER under three target-order assumptions:
  - normal GT vs prediction: `0.27257511010538327`
  - reversed GT vs prediction: `0.9012277568424301`
  - normal GT vs reversed prediction: `0.9012277568424301`
- Interpretation:
  - CRNN predictions are aligned with the normal label order, not reversed order.
  - The model is not simply outputting bottom-to-top/reversed strings.
  - The likely reason a `k=1` run can still work is model capacity/global context:
    - CRNN includes bidirectional sequence modeling, so each time step can depend on context from the opposite side.
    - SVTR uses stronger global/self-attention style sequence modeling, so it can learn an implicit order correction even more easily.
  - This can produce nontrivial accuracy, but it is still not the cleanest formal baseline because the visual order and target order are not locally aligned.
- Checked SVTR-tiny config and confirmed it also currently uses `Rot90(k=1)`:
  - `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`, train pipeline lines `40-47`
  - test pipeline lines `57-64`
- Checked SAR config for this specific rotation transform:
  - `rg` found `Rot90` only in SVTR among SAR/SVTR paths checked.

Modified files in this step:

- `experiments/notes/goal_status.md`
- generated diagnostic images under `debug_vis/orientation_check_0530/`

Verification commands:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python - <<'PY'
import mmengine, sys
sys.path.insert(0, '/home/ubuntu/DTLR')
from tools.eval_mmocr_textrecog_predictions import extract_texts, levenshtein_ops_any
p='/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/best_recog_1-N.E.D_epoch_28.pth_predictions.pkl'
preds=mmengine.load(p)
normal=revgt=revpred=0
chars=0
for s in preds:
    gt,pred=extract_texts(s)
    chars+=max(len(gt),1)
    normal+=levenshtein_ops_any(list(gt),list(pred))[0]
    revgt+=levenshtein_ops_any(list(gt[::-1]),list(pred))[0]
    revpred+=levenshtein_ops_any(list(gt),list(pred[::-1]))[0]
print(normal/chars, revgt/chars, revpred/chars)
PY
```

Training/evaluation command status:

- No new model training was started by this diagnostic.
- Existing SAR and SVTR-tiny runs continue from previous status entries.

Latest relevant config paths:

- CRNN: `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`
- SVTR-tiny: `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`

Next step:

1. Explain to the user that the accuracy is possible because the model learns an implicit sequence reordering, especially with bidirectional/global context.
2. Recommend not treating `k=1` as the cleanest final protocol; for formal baseline, compare or switch to `Rot90(k=3)` so visual left-to-right order matches top-to-bottom labels.

## Latest Update 2026-05-30 03:30 Asia/Shanghai

Completed since previous status write:

- User corrected the rotation-direction wording: counterclockwise rotation is the reading-order-preserving direction for top-to-bottom vertical text; clockwise rotation reverses the order.
- Rechecked `imgaug.augmenters.Rot90` with the same simple matrix:
  - original rows top-to-bottom: `[1, 2, 3]`
  - `Rot90(k=1)` output left-to-right: `[3, 2, 1]`
  - `Rot90(k=3)` output left-to-right: `[1, 2, 3]`
- Corrected interpretation:
  - In the practical image/read-order sense, the current `Rot90(k=1)` setting is the order-reversing rotation.
  - `Rot90(k=3)` is the order-preserving rotation for this dataset's normal top-to-bottom labels.
  - Previous wording that called `k=1` counterclockwise was wrong; the empirical output is what matters for this pipeline.

Modified files in this step:

- `experiments/notes/goal_status.md`

Verification command:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python - <<'PY'
import numpy as np
import imgaug.augmenters as iaa
img = np.array([[1, 1], [2, 2], [3, 3]], dtype=np.uint8)
for k in [1, 3]:
    print(k, iaa.Rot90(k=k, keep_size=False)(image=img))
PY
```

Training/evaluation command status:

- No model training or evaluation was started by this correction.
- Existing SAR and SVTR-tiny runs continue from previous status entries.

Next step:

1. Tell the user clearly that they are right: the current practical problem is `k=1` behaving as the order-reversing direction, while `k=3` preserves top-to-bottom order as left-to-right.

## Latest Update 2026-05-30 03:32 Asia/Shanghai

Completed since previous status write:

- User pointed out the previous rotation explanation was still confused and asked to recheck carefully.
- Checked the installed `imgaug` documentation from the local environment:
  - `imgaug.augmenters.Rot90` docstring says: `Rotate images clockwise by multiples of 90 degrees.`
  - parameter `k`: `How often to rotate clockwise by 90 degrees.`
- Verified against PIL and NumPy on a test matrix:
  - input:
    - `[[1, 2, 3], [4, 5, 6]]`
  - `imgaug Rot90(k=1)` output:
    - `[[4, 1], [5, 2], [6, 3]]`
    - matches PIL `ROTATE_270`, i.e. clockwise 90 degrees.
  - `imgaug Rot90(k=3)` output:
    - `[[3, 6], [2, 5], [1, 4]]`
    - matches PIL `ROTATE_90`, i.e. counterclockwise 90 degrees.
- Final corrected interpretation:
  - User is right: counterclockwise rotation is the order-preserving direction for top-to-bottom vertical text.
  - In `imgaug`, counterclockwise 90 degrees is `Rot90(k=3)`, not `k=1`.
  - Current CRNN/SVTR configs use `Rot90(k=1)`, which is clockwise and reverses top-to-bottom order into right-to-left/bottom-to-top when read by a left-to-right CTC/sequence decoder.

Modified files in this step:

- `experiments/notes/goal_status.md`

Verification command:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python - <<'PY'
import numpy as np
from PIL import Image
import imgaug.augmenters as iaa
arr = np.array([[1,2,3],[4,5,6]], dtype=np.uint8)
print(iaa.Rot90(k=1, keep_size=False)(image=arr))
print(iaa.Rot90(k=3, keep_size=False)(image=arr))
print(np.array(Image.fromarray(arr).transpose(Image.Transpose.ROTATE_90)))
print(np.array(Image.fromarray(arr).transpose(Image.Transpose.ROTATE_270)))
PY
```

Training/evaluation command status:

- No model training or evaluation was started by this correction.
- Existing SAR and SVTR-tiny runs continue from previous status entries.

Latest affected configs:

- CRNN currently uses clockwise/order-reversing `Rot90(k=1)`:
  - `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py`
- SVTR-tiny currently uses clockwise/order-reversing `Rot90(k=1)`:
  - `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py`

Next step:

1. Tell the user the corrected answer: current MMOCR CRNN/SVTR used clockwise `k=1`; the desired counterclockwise/order-preserving setting is `k=3`.
2. For formal comparison, prepare corrected `k=3` configs/runs after deciding whether to stop or finish the currently running `k=1` SVTR/SAR processes.

## Latest Update 2026-05-30 03:34 Asia/Shanghai

Completed since previous status write:

- User requested a concrete visual example: take one original image and apply `Rot90(k=1)`.
- Generated a side-by-side image using MTHv2 test sample `idx=0`:
  - original image on the left
  - `imgaug.augmenters.Rot90(k=1, keep_size=False)` result on the right
- Source image:
  - `/home/ubuntu/mmocr/data/tkhmth2200_mth1000_dtlr/lines/01-V001P000D_000.jpg`
- GT:
  - `北京三時學㑹出資付之印行各曰宋藏遺珍不忘所`
- Output image:
  - `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/orientation_k1_check/idx0_original_vs_rot90_k1.png`
- Opened the generated PNG for sanity check:
  - it shows the original vertical line on the left.
  - the `k=1` result is horizontal on the right.
  - visually, the top of the original line is on the right side after `k=1`, confirming the order issue for left-to-right sequence decoders.

Modified files in this step:

- `experiments/notes/goal_status.md`
- generated `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/orientation_k1_check/idx0_original_vs_rot90_k1.png`

Ended command:

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python - <<'PY'
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imgaug.augmenters as iaa
# Generated side-by-side original vs Rot90(k=1) for MTHv2 test idx=0.
PY
```

Current training status:

- SAR and SVTR-tiny continue running from the previous status entries.

Latest relevant output:

- `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_epoch28_test_0530/orientation_k1_check/idx0_original_vs_rot90_k1.png`

Next step:

1. Report the generated image path to the user.
2. If requested, generate the matching `k=3` side-by-side image for direct comparison.

## Latest Update 2026-05-30 03:35 Asia/Shanghai

Completed since previous status write:

- User reported GPU0 finished.
- Checked SVTR-tiny PID `3487530`; process is gone.
- Checked GPU status:
  - GPU0: idle, `8/24576 MiB`
  - GPU1: active with SAR, about `22032/24576 MiB`
- Confirmed SVTR-tiny completed normally through epoch `30`.
- SVTR-tiny validation curve ended with:
  - epoch `28`: `recog/1-N.E.D = 0.8681`
  - epoch `29`: `recog/1-N.E.D = 0.8702`
  - epoch `30`: `recog/1-N.E.D = 0.8698`
- Best SVTR-tiny checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/best_recog_1-N.E.D_epoch_29.pth`
- Latest checkpoint:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/epoch_30.pth`
- Interpretation:
  - this is a strong MMOCR preliminary result by valid `1-N.E.D`, much better than CRNN valid `0.6738`.
  - however, this SVTR-tiny run used the current `Rot90(k=1)` direction, so it should be marked preliminary/direction-sensitive until a corrected `k=3` protocol is run or explicitly accepted.

Modified files in this step:

- `experiments/notes/goal_status.md`

Training/evaluation command status:

- SVTR-tiny training command has ended.
- SAR remains active on GPU1.
- No SVTR test-set conversion has been run yet after this completion check.

Latest relevant log directories:

- completed SVTR-tiny run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- SVTR-tiny stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/stdout.log`
- active SAR run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Run SVTR-tiny test-set prediction export from best epoch `29` on GPU0.
2. Convert SVTR-tiny test predictions to CER/AR/CR using `tools/eval_mmocr_textrecog_predictions.py`.
3. Clearly label the result as preliminary because the run used `Rot90(k=1)`.

## Latest Update 2026-05-30 03:36 Asia/Shanghai

Completed since previous status write:

- Ran SVTR-tiny epoch-29 best checkpoint on the MTHv2 test split using GPU0.
- Exported per-sample MMOCR predictions with `--save-preds`.
- Converted the prediction pkl to DTLR-aligned CER/AR/CR and length buckets.
- MMOCR test metric:
  - `recog/1-N.E.D`: `0.8805`
- Converted SVTR-tiny MTHv2 test metrics:
  - samples: `10455`
  - `cer_micro`: `0.06583881132939977`
  - `micro_ar`: `0.9341611886706003`
  - `micro_cr`: `0.9352084755430463`
  - `empty_pred_rate`: `0.0001912960306073649`
  - `ins_rate`: `0.0010472868724460693`
  - `del_rate`: `0.003674854829208083`
  - `sub_rate`: `0.061116669627745625`
- Key length buckets:
  - `len=1`: samples `1331`, CER `0.3140495867768595`, empty `0.0007513148009015778`
  - `len=2`: samples `1032`, CER `0.2189922480620155`, empty `0.0`
  - `3-5`: samples `1272`, CER `0.17943637164244827`, empty `0.0007861635220125787`
  - `6-10`: samples `579`, CER `0.13861161524500906`, empty `0.0`
  - `11+`: samples `6241`, CER `0.05015962282500687`, empty `0.0`
- Comparison against completed CRNN test:
  - CRNN test CER `0.27257511010538327`
  - SVTR-tiny test CER `0.06583881132939977`
  - SVTR-tiny is substantially stronger on this preliminary `k=1` protocol.
- Caveat:
  - this result is preliminary/direction-sensitive because the SVTR-tiny config used `Rot90(k=1)`, which the local imgaug docs define as clockwise rotation.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/test.py configs/textrecog/svtr/svtr-tiny_30e_mthv2.py work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/best_recog_1-N.E.D_epoch_29.pth --save-preds --work-dir work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530 --cfg-options test_dataloader.num_workers=0 test_dataloader.persistent_workers=False test_dataloader.batch_size=64
```

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/eval_mmocr_textrecog_predictions.py --predictions /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530/best_recog_1-N.E.D_epoch_29.pth_predictions.pkl --output_json /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530/svtr_tiny_epoch29_test_metrics.json --output_cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530/svtr_tiny_epoch29_test_cases.jsonl
```

Latest relevant log directories and files:

- SVTR-tiny training run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220`
- SVTR-tiny best checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_full_gpu0_0530-0220/best_recog_1-N.E.D_epoch_29.pth`
- SVTR-tiny test eval: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530`
- SVTR-tiny converted metrics: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530/svtr_tiny_epoch29_test_metrics.json`
- SVTR-tiny converted cases: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_epoch29_test_0530/svtr_tiny_epoch29_test_cases.jsonl`
- active SAR run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Current training status:

- GPU0 is free after SVTR test conversion.
- SAR remains active on GPU1.

Next step:

1. Report SVTR-tiny completion and converted preliminary test metrics to the user.
2. Decide whether to use GPU0 for corrected `Rot90(k=3)` CRNN/SVTR formal rerun, after confirming the desired comparison protocol.

## Latest Update 2026-05-30 03:47 Asia/Shanghai

Completed since previous status write:

- User requested running corrected `k=3` experiments for two small MMOCR models simultaneously.
- Checked GPU state before setup:
  - GPU0: idle, `8/24576 MiB`
  - GPU1: active with SAR, about `22032/24576 MiB`
- Confirmed SAR is still active on GPU1:
  - PID `3477358`
- Created independent corrected configs without modifying the existing `k=1` configs:
  - `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2_k3.py`
  - `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py`
- Verified both new configs use `Rot90(k=3, keep_size=False)`:
  - CRNN train/test pipeline both use `k=3`
  - SVTR-tiny train/test pipeline both use `k=3`
- Updated default work_dir strings in the new configs:
  - CRNN: `work_dirs/mthv2_crnn_k3_full_gpu0`
  - SVTR-tiny: `work_dirs/mthv2_svtr_tiny_k3_full_gpu0`

Modified files in this step:

- `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2_k3.py`
- `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py`
- `experiments/notes/goal_status.md`

Commands ended:

```bash
cp /home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2.py /home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2_k3.py
```

```bash
cp /home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2.py /home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py
```

```bash
perl -0pi -e "s/k=1/k=3/g; s/work_dirs\/mthv2_crnn_full_gpu0/work_dirs\/mthv2_crnn_k3_full_gpu0/g" /home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2_k3.py
```

```bash
perl -0pi -e "s/k=1/k=3/g; s/work_dirs\/mthv2_svtr_tiny_full_gpu0/work_dirs\/mthv2_svtr_tiny_k3_full_gpu0/g" /home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py
```

Latest relevant config paths:

- CRNN k=3: `/home/ubuntu/mmocr/configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2_k3.py`
- SVTR-tiny k=3: `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py`

Next step:

1. Launch CRNN k=3 full run on GPU0 in tmux.
2. Launch SVTR-tiny k=3 full run on GPU0 in tmux.
3. Confirm both processes are alive and losses are finite before reporting.

## Latest Update 2026-05-30 03:50 Asia/Shanghai

Completed since previous status write:

- Created work directories for the two corrected `k=3` runs:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348`
  - `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348`
- Started both corrected `k=3` models simultaneously on GPU0 in tmux:
  - tmux session `mmocr_mthv2_crnn_k3_gpu0_0530`
  - tmux session `mmocr_mthv2_svtr_k3_gpu0_0530`
- Confirmed tmux sessions exist.
- Confirmed GPU0 is active:
  - GPU0: about `99%`, `6181/24576 MiB`
  - GPU1: about `100%`, `22032/24576 MiB`, still SAR
- Confirmed GPU compute processes:
  - CRNN k=3: PID `3493667`, about `2300 MiB`
  - SVTR-tiny k=3: PID `3494099`, about `3864 MiB`
  - SAR: PID `3477358`, about `22026 MiB`
- Confirmed both k=3 runs are healthy and have finite loss:
  - CRNN k=3 latest observed: epoch `1`, step `800/5261`, `loss_ctc=6.6433`
  - SVTR-tiny k=3 latest observed: epoch `1`, step `200/1316`, `loss_ctc=7.5139`

Modified files in this step:

- `experiments/notes/goal_status.md`

Running CRNN k=3 command:

```bash
tmux new-session -d -s mmocr_mthv2_crnn_k3_gpu0_0530 -c /home/ubuntu/mmocr '/bin/bash -lc "CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2_k3.py --cfg-options train_cfg.max_epochs=30 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348 > work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348/stdout.log 2>&1"'
```

Running SVTR-tiny k=3 command:

```bash
tmux new-session -d -s mmocr_mthv2_svtr_k3_gpu0_0530 -c /home/ubuntu/mmocr '/bin/bash -lc "CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348 > work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348/stdout.log 2>&1"'
```

Latest relevant logs:

- CRNN k=3 stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348/stdout.log`
- SVTR-tiny k=3 stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348/stdout.log`
- SAR stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/stdout.log`

Current training status:

- GPU0:
  - CRNN k=3 full run active.
  - SVTR-tiny k=3 full run active.
- GPU1:
  - SAR k=1 full run still active.

Next step:

1. Continue monitoring both GPU0 k=3 runs until at least first validation results are written.
2. Compare k=3 results against previous preliminary k=1 CRNN/SVTR results only after test-set conversion.

## Latest Update 2026-05-30 14:15 Asia/Shanghai

Completed since previous status write:

- User reported all experiments finished.
- Confirmed GPUs are idle:
  - GPU0: `0%`, `8/24576 MiB`
  - GPU1: `0%`, `0/24576 MiB`
- Confirmed active MMOCR tmux training sessions are gone:
  - `mmocr_mthv2_crnn_k3_gpu0_0530` ended.
  - `mmocr_mthv2_svtr_k3_gpu0_0530` ended.
  - `mmocr_mthv2_sar_gpu1_0529` ended.
- Confirmed processes are gone:
  - SAR PID `3477358`: ended.
  - CRNN k=3 PID `3493667`: ended.
  - SVTR-tiny k=3 PID `3494099`: ended.

CRNN k=3 completion:

- run: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348`
- completed through epoch `30`
- best valid `recog/1-N.E.D`: `0.8962` at epoch `28`
- final epoch `30` valid `recog/1-N.E.D`: `0.8957`
- best checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_28.pth`
- latest checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348/epoch_30.pth`

SVTR-tiny k=3 completion:

- run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348`
- completed through epoch `30`
- best valid `recog/1-N.E.D`: `0.9025` at epoch `29`
- final epoch `30` valid `recog/1-N.E.D`: `0.9019`
- best checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_29.pth`
- latest checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348/epoch_30.pth`

SAR completion:

- run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- completed through epoch `5`
- best valid `recog/1-N.E.D`: `0.1863` at epoch `5`
- best checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/best_recog_1-N.E.D_epoch_5.pth`
- latest checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300/epoch_5.pth`
- interpretation: SAR remains very weak and is not a useful strong baseline in the current setup.

Modified files in this step:

- `experiments/notes/goal_status.md`

Training/evaluation command status:

- All previously running MMOCR training commands have ended.
- No test-set conversion has been run yet for CRNN k=3 or SVTR-tiny k=3 after this completion check.

Latest relevant log directories:

- CRNN k=3: `/home/ubuntu/mmocr/work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348`
- SVTR-tiny k=3: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348`
- SAR: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

1. Run MTHv2 test-set prediction export and CER/AR/CR conversion for CRNN k=3 best epoch `28`.
2. Run MTHv2 test-set prediction export and CER/AR/CR conversion for SVTR-tiny k=3 best epoch `29`.
3. Optionally convert SAR epoch `5`, but it is weak by validation `1-N.E.D` and may not be worth prioritizing.

## Latest Update 2026-05-30 14:17 Asia/Shanghai

Completed since previous status write:

- Ran CRNN k=3 epoch-28 best checkpoint on the MTHv2 test split.
- Exported per-sample MMOCR predictions with `--save-preds`.
- Converted CRNN k=3 prediction pkl to DTLR-aligned CER/AR/CR and length buckets.
- MMOCR test metric:
  - `recog/1-N.E.D`: `0.9032`
- Converted CRNN k=3 MTHv2 test metrics:
  - samples: `10455`
  - `cer_micro`: `0.04493982775871259`
  - `micro_ar`: `0.9550601722412874`
  - `micro_cr`: `0.9562851238510235`
  - `empty_pred_rate`: `0.0003825920612147298`
  - `ins_rate`: `0.0012249516097360277`
  - `del_rate`: `0.001664438065137503`
  - `sub_rate`: `0.042050438083839056`
- Key length buckets:
  - `len=1`: samples `1331`, CER `0.29902329075882794`, empty `0.003005259203606311`
  - `len=2`: samples `1032`, CER `0.18071705426356588`, empty `0.0`
  - `3-5`: samples `1272`, CER `0.14927344782034346`, empty `0.0`
  - `6-10`: samples `579`, CER `0.12409255898366606`, empty `0.0`
  - `11+`: samples `6241`, CER `0.02970464491849722`, empty `0.0`
- Comparison against previous CRNN k=1 preliminary:
  - CRNN k=1 test CER: `0.27257511010538327`
  - CRNN k=3 test CER: `0.04493982775871259`
  - this confirms the direction-corrected protocol is much better.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/test.py configs/textrecog/crnn/crnn_mini-vgg_5e_mthv2_k3.py work_dirs/mthv2_crnn_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_28.pth --save-preds --work-dir work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530 --cfg-options test_dataloader.num_workers=0 test_dataloader.persistent_workers=False test_dataloader.batch_size=32
```

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/eval_mmocr_textrecog_predictions.py --predictions /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/best_recog_1-N.E.D_epoch_28.pth_predictions.pkl --output_json /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_metrics.json --output_cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_cases.jsonl
```

Latest relevant files:

- CRNN k=3 test eval: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530`
- CRNN k=3 converted metrics: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_metrics.json`
- CRNN k=3 converted cases: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_cases.jsonl`

Current training/evaluation status:

- All MMOCR training is ended.
- CRNN k=3 test conversion is ended.
- SVTR-tiny k=3 test conversion still needs to be run.

Next step:

1. Run MTHv2 test-set prediction export and CER/AR/CR conversion for SVTR-tiny k=3 best epoch `29`.

## Latest Update 2026-05-30 14:18 Asia/Shanghai

Completed since previous status write:

- Ran SVTR-tiny k=3 epoch-29 best checkpoint on the MTHv2 test split.
- Exported per-sample MMOCR predictions with `--save-preds`.
- Converted SVTR-tiny k=3 prediction pkl to DTLR-aligned CER/AR/CR and length buckets.
- MMOCR test metric:
  - `recog/1-N.E.D`: `0.9092`
- Converted SVTR-tiny k=3 MTHv2 test metrics:
  - samples: `10455`
  - `cer_micro`: `0.04436007966860851`
  - `micro_ar`: `0.9556399203313914`
  - `micro_cr`: `0.9568461703898339`
  - `empty_pred_rate`: `0.0016260162601626016`
  - `ins_rate`: `0.0012062500584423478`
  - `del_rate`: `0.002580814078527814`
  - `sub_rate`: `0.04057301553163835`
- Key length buckets:
  - `len=1`: samples `1331`, CER `0.2637114951164538`, empty `0.010518407212622089`
  - `len=2`: samples `1032`, CER `0.18071705426356588`, empty `0.0029069767441860465`
  - `3-5`: samples `1272`, CER `0.13562307353588726`, empty `0.0`
  - `6-10`: samples `579`, CER `0.10526315789473684`, empty `0.0`
  - `11+`: samples `6241`, CER `0.03107888116027823`, empty `0.0`
- Comparison against previous SVTR-tiny k=1 preliminary:
  - SVTR k=1 test CER: `0.06583881132939977`
  - SVTR k=3 test CER: `0.04436007966860851`
  - corrected direction improves overall test CER and should replace the k=1 preliminary result as the formal SVTR-tiny MMOCR result.
- Comparison against CRNN k=3:
  - CRNN k=3 test CER: `0.04493982775871259`
  - SVTR-tiny k=3 test CER: `0.04436007966860851`
  - SVTR-tiny k=3 is slightly better overall, but close.
- SAR note:
  - SAR valid best is only `0.1863`, far below CRNN/SVTR k=3.
  - SAR test conversion has not been run yet because the SAR validation/test pass is slow and the model is clearly weak in this setup.

Modified files in this step:

- `experiments/notes/goal_status.md`

Ended commands:

```bash
cd /home/ubuntu/mmocr
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/test.py configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348/best_recog_1-N.E.D_epoch_29.pth --save-preds --work-dir work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530 --cfg-options test_dataloader.num_workers=0 test_dataloader.persistent_workers=False test_dataloader.batch_size=64
```

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/eval_mmocr_textrecog_predictions.py --predictions /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/best_recog_1-N.E.D_epoch_29.pth_predictions.pkl --output_json /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_metrics.json --output_cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_cases.jsonl
```

Latest relevant files:

- SVTR-tiny k=3 test eval: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530`
- SVTR-tiny k=3 converted metrics: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_metrics.json`
- SVTR-tiny k=3 converted cases: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_cases.jsonl`

Current training/evaluation status:

- All MMOCR training has ended.
- CRNN k=3 and SVTR-tiny k=3 formal test conversions are complete.
- SAR test conversion is pending/not run because the model is weak and evaluation is slow.

Next step:

1. Report final MMOCR comparison status to the user.
2. If the user needs SAR in the formal table despite poor validation, run SAR epoch-5 test conversion separately.

## Latest Update 2026-05-30 14:21 Asia/Shanghai

Completed since previous status write:

- User asked whether SVTR-small should still be run after SVTR-tiny k=3 completed.
- Current formal k=3 MMOCR results:
  - CRNN k=3 test CER `0.04493982775871259`, AR `0.9550601722412874`, CR `0.9562851238510235`
  - SVTR-tiny k=3 test CER `0.04436007966860851`, AR `0.9556399203313914`, CR `0.9568461703898339`
  - SAR valid best only `0.1863` `1-N.E.D`, not a strong baseline.
- Decision:
  - Recommend running SVTR-small k=3 for the formal paper comparison if time/GPU budget allows.
  - Reason: SVTR-tiny is a useful lightweight/efficiency baseline, but small is more convincing as the representative modern SVTR comparison model.
  - Do not prioritize SVTR-base/large before small; small is the next reasonable step.
- Expected value:
  - If SVTR-small significantly beats tiny, use small as the main SVTR row and optionally keep tiny as efficiency row.
  - If SVTR-small is similar, tiny remains acceptable as a lightweight baseline, but small result prevents reviewers from arguing the comparison used only an undersized SVTR.

Modified files in this step:

- `experiments/notes/goal_status.md`

Training/evaluation command status:

- No new training was started for this question.
- All previous MMOCR training/evaluation commands have ended except optional future SAR conversion.

Latest relevant outputs:

- SVTR-tiny k=3 metrics: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_tiny_k3_epoch29_test_0530/svtr_tiny_k3_epoch29_test_metrics.json`
- CRNN k=3 metrics: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_crnn_k3_epoch28_test_0530/crnn_k3_epoch28_test_metrics.json`

Next step:

1. If user agrees, prepare an independent SVTR-small k=3 config and launch it on a free GPU.
2. Keep SVTR-tiny k=3 as the current usable formal result until SVTR-small finishes and is converted to CER/AR/CR.

## Latest Update 2026-05-30 14:23 Asia/Shanghai

Completed since previous status write:

- User requested running one SVTR-small k=3 experiment on GPU1.
- Checked GPU state:
  - GPU0: idle, `8/24576 MiB`
  - GPU1: idle, `0/24576 MiB`
- Inspected existing MMOCR SVTR configs:
  - official `svtr-small_20e_st_mj.py`
  - completed MTHv2 `svtr-tiny_30e_mthv2_k3.py`
- Created new independent MTHv2 SVTR-small k=3 config:
  - `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py`
- Config construction:
  - copied from `svtr-tiny_30e_mthv2_k3.py`
  - inserted official small encoder parameters from `svtr-small_20e_st_mj.py`:
    - `embed_dims=[96, 192, 256]`
    - `depth=[3, 6, 6]`
    - `num_heads=[3, 6, 8]`
    - `mixer_types=['Local'] * 8 + ['Global'] * 7`
  - kept MTHv2 charset and data paths.
  - kept corrected `Rot90(k=3)` in train/test pipelines.
  - default work_dir set to `work_dirs/mthv2_svtr_small_k3_full_gpu1`.
- Verified the new config contains `Rot90(k=3)` in both train/test pipelines.

Modified files in this step:

- `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py`
- `experiments/notes/goal_status.md`

Commands ended:

```bash
cp /home/ubuntu/mmocr/configs/textrecog/svtr/svtr-tiny_30e_mthv2_k3.py /home/ubuntu/mmocr/configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py
```

```bash
perl -0pi -e "s/work_dirs\/mthv2_svtr_tiny_k3_full_gpu0/work_dirs\/mthv2_svtr_small_k3_full_gpu1/g; s/load_from = None\n/load_from = None\n\n_base_.model.encoder.update(\n    dict(\n        embed_dims=[96, 192, 256],\n        depth=[3, 6, 6],\n        num_heads=[3, 6, 8],\n        mixer_types=['Local'] * 8 + ['Global'] * 7))\n/" /home/ubuntu/mmocr/configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py
```

Latest relevant config:

- `/home/ubuntu/mmocr/configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py`

Next step:

1. Launch SVTR-small k=3 full training on GPU1 in tmux.
2. Confirm process, GPU memory, and finite loss before reporting.

## Latest Update 2026-05-30 14:26 Asia/Shanghai

Completed since previous status write:

- Created SVTR-small k=3 work directory:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424`
- Launched SVTR-small k=3 full training on GPU1 in tmux:
  - tmux session: `mmocr_mthv2_svtr_small_k3_gpu1_0530`
- Confirmed tmux session exists.
- Confirmed GPU state:
  - GPU0: idle, `8/24576 MiB`
  - GPU1: active, about `5660/24576 MiB`
- Confirmed compute process:
  - PID `3510638`
  - `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`
  - about `5654 MiB`
- Confirmed training reached first logged step with finite loss:
  - epoch `1`, step `100/1316`
  - `loss_ctc=7.6328`

Modified files in this step:

- `experiments/notes/goal_status.md`

Running command:

```bash
tmux new-session -d -s mmocr_mthv2_svtr_small_k3_gpu1_0530 -c /home/ubuntu/mmocr '/bin/bash -lc "CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424 > work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424/stdout.log 2>&1"'
```

Latest relevant logs:

- SVTR-small k=3 run: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424`
- SVTR-small k=3 stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424/stdout.log`

Current training/evaluation status:

- SVTR-small k=3 is actively training on GPU1.
- No other MMOCR training/evaluation is active.

Next step:

1. Continue monitoring SVTR-small k=3 until validation results are available.
2. After it finishes, export test predictions from the best checkpoint and convert to CER/AR/CR.

## Latest Update 2026-05-30 14:44 Asia/Shanghai

1. 已完成内容

- 按 `logs/paper_results_summary.md` 现有风格新增 MMOCR 对比实验统计区块：
  - `MMOCR Baseline Comparison (MTHv2-combo)`（含已完成的 test 指标）
  - `MMOCR Ongoing / Pending Conversion`（含进行中与待换算实验）
- 已写入并统一汇总的已完成 test 对比结果：
  - CRNN `k=3`
  - SVTR-tiny `k=3`
  - CRNN `k=1`（早期方向版本）
  - SVTR-tiny `k=1`（早期方向版本）
- 表内字段已包含 `CER/AR/CR`、`recog/1-N.E.D`、`empty`、`Pred/GT len`、长度分桶 CER、checkpoint 与 result json 路径，后续不需要再手工翻日志。

2. 修改过的文件

- `/home/ubuntu/DTLR/logs/paper_results_summary.md`
- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 正在运行（GPU1）：

```bash
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424
```

- 已结束（本次未新启动）：
  - SAR full run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
  - CRNN/SVTR-tiny 的 k=1、k=3 训练与测试评估均已结束。

4. 最新日志目录

- 训练中最新目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424`
- 新增汇总表：`/home/ubuntu/DTLR/logs/paper_results_summary.md`

5. 下一步要做什么

1. 等待 SVTR-small k=3 训练结束，记录其最佳 `val recog/1-N.E.D` 与最佳 epoch。
2. 对 SVTR-small 最佳 checkpoint 跑 test 并换算 `CER/AR/CR`。
3. 将 SVTR-small test 行追加进 `MMOCR Baseline Comparison (MTHv2-combo)`，更新对比结论。

## Latest Update 2026-05-30 17:39 Asia/Shanghai

1. 已完成内容

- 确认 `SVTR-small k=3` 训练已完成（到 `epoch 30`），最佳验证为：
  - best val `recog/1-N.E.D = 0.8946` @ epoch `29`
  - 训练目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424`
- 完成 `SVTR-small k=3` test 评估：
  - test `recog/1-N.E.D = 0.9027`
  - test 目录：`/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530`
- 完成 CER/AR/CR 换算并产出：
  - `cer_micro=0.04662296737514377`（4.66）
  - `micro_ar=0.9533770326248562`（95.34）
  - `micro_cr=0.9544336702729491`（95.44）
  - 指标文件：`/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530/svtr_small_k3_epoch29_test_metrics.json`
- 已更新论文汇总表：
  - 在 `MMOCR Baseline Comparison (MTHv2-combo)` 中新增 `SVTR-small k=3` 行
  - 将 “MMOCR Ongoing / Pending Conversion” 更新为 “MMOCR Pending Conversion”，并移除已完成的 SVTR-small 运行中状态。

2. 修改过的文件

- `/home/ubuntu/DTLR/logs/paper_results_summary.md`
- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 已结束（训练）：

```bash
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424
```

- 已结束（test 评估）：

```bash
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/test.py configs/textrecog/svtr/svtr-small_30e_mthv2_k3.py work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424/best_recog_1-N.E.D_epoch_29.pth --save-preds --work-dir work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530 --cfg-options test_dataloader.num_workers=0 test_dataloader.persistent_workers=False test_dataloader.batch_size=64
```

- 已结束（指标换算）：

```bash
/home/ubuntu/miniconda3/envs/openmmlab/bin/python /home/ubuntu/DTLR/tools/eval_mmocr_textrecog_predictions.py --predictions /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530/best_recog_1-N.E.D_epoch_29.pth_predictions.pkl --output_json /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530/svtr_small_k3_epoch29_test_metrics.json --output_cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530/svtr_small_k3_epoch29_test_cases.jsonl
```

- 当前无 MMOCR 训练进程在 GPU 上运行。

4. 最新日志目录

- 最新训练日志目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424`
- 最新测试日志目录：`/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_small_k3_epoch29_test_0530`
- 最新论文汇总表：`/home/ubuntu/DTLR/logs/paper_results_summary.md`

5. 下一步要做什么

1. 按相同流程对 SAR 最佳 checkpoint 跑 test 并换算 CER/AR/CR。
2. 把 SAR 结果补入 `MMOCR Baseline Comparison (MTHv2-combo)`。
3. 统一输出一版“DTLR vs MMOCR”正式对比段落（用于论文实验节）。

## Latest Update 2026-05-30 18:55 Asia/Shanghai

1. 已完成内容

- 按用户要求在 GPU1 启动 `SVTR-L`（MTHv2, `k=3`）重跑。
- 经过启动校验，当前有效长训进程已稳定运行：
  - PID: `3536241`
  - 已出现连续训练日志与有限 loss（示例）：
    - `Epoch(train) [1][100/2631] loss_ctc=7.5191`
    - `Epoch(train) [1][500/2631] loss_ctc=6.8822`
- 当前占用：
  - GPU1 约 `6372 MiB`（训练进程）

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py`
- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 正在运行（有效长训）：

```bash
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/_debug_svtr_large_k3_failcheck
```

- 已结束（无效/中断启动尝试）：
  - `work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1850`
  - `work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1851`
  - `work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1852`
  - `work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1853`

4. 最新日志目录

- 当前有效训练日志目录：`/home/ubuntu/mmocr/work_dirs/_debug_svtr_large_k3_failcheck`
- 主日志文件：`/home/ubuntu/mmocr/work_dirs/_debug_svtr_large_k3_failcheck/20260530_185253/20260530_185253.log`

5. 下一步要做什么

1. 持续监控 `SVTR-L` 的 val `recog/1-N.E.D`（按 epoch 保存 best ckpt）。
2. 训练完成后在 test 集评估并换算 CER/AR/CR。
3. 将 `SVTR-L` 行补入 `paper_results_summary.md` 的 MMOCR 对比表。

## Latest Update 2026-05-30 18:57 Asia/Shanghai

1. 已完成内容

- 对 18:55 前后的后台拉起方式做了稳定性修正，最终采用 `setsid` 后台方式成功启动持久进程。
- 当前**有效正式长训**已确认稳定：
  - PID: `3539572`（PPID=1，脱离终端）
  - work_dir: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856`
  - 已出现首个训练步：
    - `Epoch(train) [1][100/2631] loss_ctc=7.5919`
- GPU 状态确认：
  - GPU1 训练进程 `3539572`，显存约 `6372 MiB`

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 正在运行（有效正式长训）：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856 > /home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856/stdout.log 2>&1 < /dev/null &
```

- 已结束（排错/短时进程）：
  - `_debug_svtr_large_k3_failcheck`（timeout fail-check）
  - `mthv2_svtr_large_k3_full_gpu1_0530-1850/1851/1852/1853/1855`（非稳定启动尝试）

4. 最新日志目录

- 当前有效日志目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856`
- stdout：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856/stdout.log`

5. 下一步要做什么

1. 持续监控到首轮 val 完成，记录 `best recog/1-N.E.D`。
2. 训练结束后跑 test、换算 CER/AR/CR。
3. 更新 `paper_results_summary.md` 的 SVTR-L 行并与 tiny/small 对比。

## Latest Update 2026-05-31 15:35 Asia/Shanghai

1. 已完成内容

- 按恢复规则读取并核查了 `SVTR-L` 最新有效日志：
  - `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856/stdout.log`
- 该轮训练已完整跑到 `epoch 30`，验证指标结论：
  - best val `recog/1-N.E.D = 0.0433` @ epoch `29`
  - epoch 30 val 仍为 `0.0433`
- 对比基线：
  - `SVTR-tiny k=3` best val 约 `0.9025`
  - 当前 `SVTR-L` 明显失败（非正常可比水平）。

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- `SVTR-L` 本轮训练已结束（无活跃进程）：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856 > /home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856/stdout.log 2>&1 < /dev/null &
```

4. 最新日志目录

- 最新核查日志目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856`
- 关键日志文件：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856/stdout.log`

5. 下一步要做什么

1. 暂不对该失败轮次做 test 换算（val 已证明无效）。
2. 基于 tiny/small 成功配置，重建一版 `SVTR-L` 配方（先做 1 epoch smoke）后再正式复跑。
3. 若 smoke 正常（val 不再接近 0），再启动新一轮 GPU1 正式训练。

## Latest Update 2026-05-31 15:45 Asia/Shanghai

1. 已完成内容

- 进一步排查 `SVTR-L k=3` 本轮失败原因。
- 关键证据：
  - `SVTR-L` 训练 loss 从前期到后期基本卡在高位：
    - epoch 1 step 100: `loss_ctc=7.5919`
    - epoch 10 step 100: `loss_ctc=7.5321`
    - epoch 20 step 100: `loss_ctc=6.7712`
    - epoch 30 附近仍多次在 `6.x`
  - 成功的 `SVTR-tiny/small k=3` 同数据同方向下，第 5 轮 loss 已降到约 `1.5-1.6`，第 20 轮约 `0.37`，val 已到 `0.86+`。
  - 因此该轮不是单纯 test 换算问题，也不是 val 指标读取问题，而是模型训练没有正常收敛。
- 初步根因判断：
  - 本轮 `SVTR-L` 配置不是官方 large 配方的完整迁移，而是把 large encoder 参数 graft 到 tiny/small 的 MTHv2 配方上。
  - 与官方 `svtr-large_20e_st_mj.py` 差异包括：
    - 官方 large 使用 `output_image_size=(48,160)`、`img_size=[48,160]`、`max_seq_len=40`
    - 当前失败轮使用 `output_image_size=(32,256)`、`img_size=[32,256]`、`max_seq_len=64`
    - 官方 large 使用较低 lr `2.5e-4`
    - 当前失败轮继承 tiny/small lr `5e-4`
  - 对 large 规模模型而言，上述输入几何与学习率组合很可能导致 CTC 训练不稳定/不收敛。

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- `SVTR-L k=3` 失败轮已结束：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856 > /home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856/stdout.log 2>&1 < /dev/null &
```

4. 最新日志目录

- 失败轮日志目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_0530-1856`
- 成功对照：
  - tiny: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_tiny_k3_full_gpu0_0530-0348`
  - small: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_small_k3_full_gpu1_0530-1424`

5. 下一步要做什么

1. 新建 `SVTR-L` 修正版配置：优先贴近官方 large 输入几何与 lr（`48x160`, `max_seq_len=40`, `lr=2.5e-4`），保留 MTHv2 字典和 `Rot90(k=3)`。
2. 先做 1-2 epoch smoke，看 loss 是否像 tiny/small 一样明显下降，val 是否不再长期停在 `0.0063`。
3. smoke 正常后再启动正式 30 epoch；smoke 不正常则不要继续浪费 GPU。

## Latest Update 2026-05-31 15:45 Asia/Shanghai

1. 已完成内容

- 按用户要求准备在 GPU1 重新尝试 `SVTR-L`。
- 新建修正版配置：
  - `/home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py`
- 修正点：
  - 使用官方 SVTR-L 输入几何：`output_image_size=(48,160)`, `img_size=[48,160]`
  - 使用官方 SVTR-L `max_seq_len=40`
  - 使用官方 SVTR-L 学习率：`lr=2.5e-4`
  - 保留 MTHv2 字典、MTHv2 train/val/test JSON、`Rot90(k=3)`
  - batch 仍保守设为 `32`，避免 OOM

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py`
- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 本步骤尚未启动训练，仅完成配置。

4. 最新日志目录

- 待创建 smoke 日志目录：`/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_*`

5. 下一步要做什么

1. 在 GPU1 启动 2 epoch smoke。
2. 观察 epoch 1/2 loss 与 val `recog/1-N.E.D`。
3. smoke 正常后删除 smoke 日志并启动正式 30 epoch。

## Latest Update 2026-05-31 15:46 Asia/Shanghai

1. 已完成内容

- 已在 GPU1 启动 `SVTR-L officialgeom` 2 epoch smoke。
- 已确认进程存在并占用 GPU1：
  - PID: `3677792`
  - GPU1 显存约 `5986 MiB`

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 正在运行（smoke）：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_0531-1546
```

4. 最新日志目录

- `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_0531-1546`
- stdout: `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_0531-1546/stdout.log`

5. 下一步要做什么

1. 等待 smoke 跑完 2 个 epoch。
2. 判断 loss/val 是否正常。
3. 若正常，删除 smoke 日志并启动正式 30 epoch；若不正常，停止继续长训并换下一组假设。

## Latest Update 2026-05-31 16:52 Asia/Shanghai

1. 已完成内容

- `SVTR-L officialgeom` 2 epoch smoke 已完成，结果正常，可以进入正式长训。
- 关键结果：
  - epoch 1 val `recog/1-N.E.D = 0.2712`
  - epoch 2 val `recog/1-N.E.D = 0.5971`
  - epoch 2 末段 `loss_ctc` 已降到 `2.1358`
- 与失败轮对比：
  - 失败轮 epoch 2 val 仍为 `0.0063`
  - 失败轮 loss 长期卡在 `6.x-7.x`
  - 新配置已经明显恢复学习能力。

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 已结束（smoke）：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_0531-1546
```

4. 最新日志目录

- smoke 日志目录：`/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_0531-1546`

5. 下一步要做什么

1. 在 GPU1 启动正式 30 epoch 训练。
2. 确认正式长训 PID、显存、首个 finite loss。
3. 正式长训启动稳定后删除 smoke 日志目录。

## Latest Update 2026-05-31 16:54 Asia/Shanghai

1. 已完成内容

- 已在 GPU1 启动 `SVTR-L officialgeom` 正式 30 epoch 长训。
- 已确认正式长训有正常日志与有限 loss：
  - `Epoch(train) [1][100/2631] loss_ctc=7.2362`
  - `Epoch(train) [1][200/2631] loss_ctc=6.7435`
- 已确认 GPU1 compute 进程：
  - PID: `3694852`
  - `/home/ubuntu/miniconda3/envs/openmmlab/bin/python`
  - 显存约 `5980 MiB`
- 按用户此前要求，正式长训启动后已删除本次 smoke 日志目录：
  - deleted: `/home/ubuntu/mmocr/work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_0531-1546`

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 正在运行（正式长训）：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653
```

- 已结束并已删除日志目录（smoke）：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/smoke_mthv2_svtr_large_k3_officialgeom_0531-1546
```

4. 最新日志目录

- 正式长训目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653`
- stdout: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653/stdout.log`

5. 下一步要做什么

1. 监控正式长训第 1/2 轮 val，确认走势与 smoke 一致。
2. 训练完成后跑 test 并换算 CER/AR/CR。
3. 将 SVTR-L 修正版结果追加到 `logs/paper_results_summary.md`。

## Latest Update 2026-06-01 00:02 Asia/Shanghai

1. 已完成内容

- 用户反馈 `SVTR-L officialgeom` 正式长训已跑完，已核查日志。
- 正式 30 epoch 训练完整结束。
- 最佳验证结果：
  - best val `recog/1-N.E.D = 0.8966` @ epoch `29`
  - epoch 30 val `recog/1-N.E.D = 0.8965`
- 训练明显正常收敛：
  - 后期训练 `loss_ctc` 约 `0.12-0.20`
  - 与失败轮 `loss_ctc` 长期卡在 `6.x` 完全不同。

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 已结束（正式长训）：

```bash
setsid env CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653
```

4. 最新日志目录

- 正式训练目录：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653`
- best checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653/best_recog_1-N.E.D_epoch_29.pth`

5. 下一步要做什么

1. 用 epoch 29 best checkpoint 跑 MTHv2 test。
2. 换算 `CER/AR/CR`。
3. 更新 `logs/paper_results_summary.md`。

## Latest Update 2026-05-30 18:49 Asia/Shanghai

1. 已完成内容

- 收到新指令：在 GPU1 追加运行 `SVTR-L`（MTHv2，`k=3`）。
- 新建独立训练配置（不改已有 MMOCR 配置）：
  - `/home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py`
- 配置要点：
  - 使用官方 SVTR-L 编码器规模：`embed_dims=[192,256,512]`、`depth=[3,9,9]`、`num_heads=[6,8,16]`、`Local*10 + Global*11`
  - 纵向修正使用 `Rot90(k=3)`（train/test）
  - MTHv2 charset 与 train/val/test JSON 保持一致
  - 为避免 OOM，batch 设为 `train=32, val/test=32`

2. 修改过的文件

- `/home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py`
- `/home/ubuntu/DTLR/experiments/notes/goal_status.md`

3. 正在运行或已结束的训练命令

- 本步骤尚未启动训练（仅完成配置准备）。

4. 最新日志目录

- 最新可用配置路径：`/home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3.py`
- 计划训练日志目录（下一步创建）：`/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_full_gpu1_*`

5. 下一步要做什么

1. 在 GPU1 启动 `SVTR-L k=3` 正式训练（tmux 后台）。
2. 确认 PID、显存占用和首个 finite loss。
3. 回写启动信息到 `goal_status.md`。

## Latest Update 2026-06-01 00:04 Asia/Shanghai

Completed in this step:

- Confirmed the SVTR-L official-geometry full training has finished 30 epochs.
- Best validation checkpoint:
  - `recog/1-N.E.D = 0.8966` at epoch 29
  - checkpoint: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653/best_recog_1-N.E.D_epoch_29.pth`
- Final epoch validation:
  - epoch 30 `recog/1-N.E.D = 0.8965`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended:
  - `CUDA_VISIBLE_DEVICES=1 ... tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py ... work_dir=work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653`
- Running:
  - none

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653`

Next step:

- Run MMOCR test on the epoch-29 best checkpoint, convert predictions to CER/AR/CR, and update `logs/paper_results_summary.md`.

## Latest Update 2026-06-01 00:06 Asia/Shanghai

Completed in this step:

- Ran MMOCR test for the SVTR-L official-geometry best checkpoint on MTHv2-combo test.
- Converted MMOCR predictions to the paper table metrics:
  - samples: `10455`
  - MMOCR `recog/1-N.E.D`: `0.9015`
  - CER micro: `4.84`
  - AR micro: `95.16`
  - CR micro: `95.26`
  - empty prediction rate: `0.11`
  - pred/GT length ratio: `0.999`
  - len=1/2/3-5/6-10/11+ CER: `28.10 / 19.72 / 14.66 / 10.96 / 3.43`
- Added the SVTR-L row to the MMOCR baseline table in `logs/paper_results_summary.md`.

Modified files:

- `experiments/notes/goal_status.md`
- `logs/paper_results_summary.md`

Training/evaluation commands:

- Ended:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/test.py /home/ubuntu/DTLR/experiments/configs/mmocr/svtr-large_30e_mthv2_k3_officialgeom.py work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653/best_recog_1-N.E.D_epoch_29.pth --save-preds --work-dir work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601 --cfg-options test_dataloader.num_workers=0 test_dataloader.persistent_workers=False test_dataloader.batch_size=32`
  - `/home/ubuntu/miniconda3/envs/openmmlab/bin/python /home/ubuntu/DTLR/tools/eval_mmocr_textrecog_predictions.py --predictions /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601/best_recog_1-N.E.D_epoch_29.pth_predictions.pkl --output_json /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601/svtr_large_k3_officialgeom_epoch29_test_metrics.json --output_cases /home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601/svtr_large_k3_officialgeom_epoch29_test_cases.jsonl`
- Running:
  - none

Latest log directory:

- Training: `/home/ubuntu/mmocr/work_dirs/mthv2_svtr_large_k3_officialgeom_full_gpu1_0531-1653`
- Test/eval: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601`
- Metrics file: `/home/ubuntu/mmocr/work_dirs/eval_mthv2_svtr_large_k3_officialgeom_epoch29_test_0601/svtr_large_k3_officialgeom_epoch29_test_metrics.json`

Next step:

- No need to rerun this SVTR-L experiment. For the paper comparison table, the effective MMOCR baselines currently remain CRNN `k=3`, SVTR-tiny `k=3`, SVTR-small `k=3`, and SVTR-L `k=3`; SVTR-tiny has the best MMOCR CER among these, while DTLR bias remains best overall on MTHv2-combo.

## Latest Update 2026-06-01 00:09 Asia/Shanghai

Completed in this step:

- Started a root-cause check for the poor SAR baseline run.
- Scope: inspect SAR config, training/eval logs, geometry/orientation settings, dictionary/decoder limits, and compare against working CRNN/SVTR MTHv2 configs before deciding whether to rerun.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - none
- Ended:
  - none in this step

Latest log directory:

- SAR candidate to inspect: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

- Read SAR config/logs and compare against working MMOCR baselines to identify whether SAR was run with a wrong geometry, transform order, sequence limit, or unsuitable architecture/hyperparameters.

## Latest Update 2026-06-01 00:12 Asia/Shanghai

Completed in this step:

- Inspected the existing SAR MTHv2 config and run logs:
  - config: `/home/ubuntu/mmocr/configs/textrecog/sar/sar_r31_parallel_decoder_mthv2_vertical.py`
  - run dir: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- Found the main root cause for the poor SAR result:
  - SAR train/test pipeline did **not** apply `Rot90(k=3)`.
  - It only listed rotations in `tta_pipeline`, but normal train/val/test did not use TTA.
  - Therefore SAR trained/evaluated on raw vertical images after `RescaleToHeight(height=48)`, which compresses a vertical column into a very narrow image and leaves the sequence direction incompatible with SAR's horizontal attention decoder.
- Confirmed old SAR run behavior:
  - `train_cfg.max_epochs=5`
  - validation `recog/1-N.E.D` improved only from `0.0358` to `0.1863`
  - training loss stayed around `3.x` late in training
  - validation was very slow because the config pads to width `1024`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - none
- Ended:
  - none in this step

Latest log directory:

- Broken/old SAR run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`

Next step:

- Create a corrected independent SAR MTHv2 `k=3` config with rotation in both train and test pipelines, then run a short smoke/short training before any full SAR rerun.

## Latest Update 2026-06-01 00:15 Asia/Shanghai

Completed in this step:

- Created corrected independent SAR config:
  - `/home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py`
- Verified the config parses with MMEngine.
- Verified both train and test pipelines contain:
  - conditional `Rot90(k=3)` before `RescaleToHeight`
- Checked a representative MTHv2 image:
  - original shape: `(1309, 108)`
  - after `k=3` rotation: `(108, 1309)`, i.e. horizontal line direction for SAR
- Checked first 2000 train samples after rotation + height scaling:
  - max scaled width: about `943.4`
  - p95 scaled width: about `692.7`
  - max text length: `29`
  - interpretation: `max_width=1024` and `max_seq_len=64` are not the immediate bottleneck for normal samples.

Modified files:

- `experiments/notes/goal_status.md`
- `experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py`

Training/evaluation commands:

- Running:
  - none
- Ended:
  - config parse check only; no training launched

Latest log directory:

- Old broken SAR run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300`
- Corrected config ready: `/home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py`

Next step:

- If SAR is still needed for the paper comparison, run a corrected `k=3` SAR short validation first. Do not continue or reuse the old `/home/ubuntu/mmocr/work_dirs/mthv2_sar_full_gpu1_0529-2300` result.

## Latest Update 2026-06-01 00:18 Asia/Shanghai

Completed in this step:

- Received instruction to run corrected SAR short training first, then launch full training if the short run is healthy.
- Planned short-run gate:
  - use corrected `Rot90(k=3)` SAR config
  - run 2 epochs on GPU1
  - continue to full training only if validation improves clearly over the old broken SAR best `recog/1-N.E.D = 0.1863` and training loss is finite/decreasing

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - none yet
- Ended:
  - none in this step

Latest log directory:

- Corrected config: `/home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py`

Next step:

- Check GPU state, then launch corrected SAR 2-epoch short training on GPU1.

## Latest Update 2026-06-01 00:19 Asia/Shanghai

Completed in this step:

- Checked GPU state before launching SAR:
  - GPU0 is busy with PID `3643119` using about `24024 MiB`.
  - GPU1 is free (`3 MiB`, `0%`).
- Selected GPU1 for corrected SAR short training.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - none yet
- Ended:
  - GPU status checks only

Latest log directory:

- Planned SAR short run: `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_0601-0018`

Next step:

- Launch 2-epoch corrected SAR short training on GPU1 and monitor first loss plus validation result.

## Latest Update 2026-06-01 00:20 Asia/Shanghai

Completed in this step:

- Attempted to launch SAR short training with work dir under `/home/ubuntu/mmocr/work_dirs`.
- The escalation request was rejected by the approval system before execution, so no SAR training process was started and no MMOCR log directory was created.
- Switched to a safer writable-root plan: run the same corrected SAR short training while writing logs/checkpoints under `/home/ubuntu/DTLR/logs`.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Failed before launch:
  - `CUDA_VISIBLE_DEVICES=1 ... tools/train.py ... work_dir=work_dirs/short_mthv2_sar_k3_0601-0018`
- Running:
  - none

Latest log directory:

- Planned fallback short run: `/home/ubuntu/DTLR/logs/short_mthv2_sar_k3_0601-0018`

Next step:

- Launch the corrected SAR 2-epoch short training with the log directory under `/home/ubuntu/DTLR/logs`.

## Latest Update 2026-06-01 00:21 Asia/Shanghai

Completed in this step:

- Launched corrected SAR 2-epoch short training on GPU1.
- Logs/checkpoints are being written under the DTLR writable root.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=/home/ubuntu/DTLR/logs/short_mthv2_sar_k3_0601-0018`

Latest log directory:

- `/home/ubuntu/DTLR/logs/short_mthv2_sar_k3_0601-0018`

Next step:

- Monitor early training output for finite/decreasing loss, then inspect validation after epoch 1 and epoch 2.

## Latest Update 2026-06-01 00:22 Asia/Shanghai

Completed in this step:

- Confirmed the fallback SAR short run under `/home/ubuntu/DTLR/logs` was not a valid GPU run.
- The process printed `CUDA available: False` inside the sandbox and did not reach training iterations.
- No SAR training is currently running.
- GPU1 remains free, but launching GPU training requires an escalated command; the previous escalation request was rejected by the approval/auth system before execution.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Invalid/ended before training:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=/home/ubuntu/DTLR/logs/short_mthv2_sar_k3_0601-0018`
- Running:
  - none

Latest log directory:

- Invalid sandbox/CPU attempt: `/home/ubuntu/DTLR/logs/short_mthv2_sar_k3_0601-0018`
- Corrected config ready: `/home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py`

Next step:

- Re-run the corrected SAR short training with escalated GPU access after the approval/auth issue is resolved. Do not treat `/home/ubuntu/DTLR/logs/short_mthv2_sar_k3_0601-0018` as a valid experiment.

## Latest Update 2026-06-01 00:25 Asia/Shanghai

Completed in this step:

- Received instruction to retry escalated GPU launch for corrected SAR short training.
- Prepared a fresh short-run directory to avoid confusing it with the previous invalid sandbox/CPU attempt.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - none yet
- Ended:
  - none in this step

Latest log directory:

- Planned retry short run: `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025`

Next step:

- Retry corrected SAR 2-epoch short training on GPU1 with escalated access. If escalation fails again, provide the exact manual command.

## Latest Update 2026-06-01 00:26 Asia/Shanghai

Completed in this step:

- Retried escalated GPU launch for corrected SAR short training.
- The command was rejected again by the approval/auth system before execution:
  - `Your access token could not be refreshed because your refresh token was already used. Please log out and sign in again.`
- No SAR GPU training process was started.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Failed before launch:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/short_mthv2_sar_k3_retry_0601-0025`
- Running:
  - none

Latest log directory:

- No valid new SAR GPU log directory was created.
- Corrected config ready: `/home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py`

Next step:

- User can run the provided manual short-training command directly in a terminal. After it finishes, resume by reading this status file and the short-run log, then decide whether to launch the full SAR training.

## Latest Update 2026-06-01 00:42 Asia/Shanghai

Completed in this step:

- Inspected the manually launched corrected SAR short-training log:
  - `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025/20260601_002128/20260601_002128.log`
- Confirmed this is a valid GPU run:
  - `CUDA available: True`
  - `GPU number: 1`
  - checkpoints are saved to `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025`
- Confirmed the corrected pipeline is active:
  - train/test/val pipeline includes conditional `Rot90(k=3)`.
- Latest observed training progress:
  - epoch 1 reached `2000/5261` iterations.
  - loss is finite and generally decreasing from about `6.59` at iter 100 to about `4.51` at iter 2000.
- GPU check shows GPU1 active at about `96%` utilization and `22030 MiB` memory, consistent with SAR training.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running externally/manual:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/short_mthv2_sar_k3_retry_0601-0025`

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025`

Next step:

- Let short training continue through epoch 1 validation and ideally epoch 2 validation. Decide on full SAR training only after seeing validation `recog/1-N.E.D`; target is to clearly exceed the old broken SAR best `0.1863`.

## Latest Update 2026-06-01 03:24 Asia/Shanghai

Completed in this step:

- Inspected the completed corrected SAR short-training run:
  - log: `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025/20260601_002128/20260601_002128.log`
  - checkpoint: `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025/best_recog_1-N.E.D_epoch_2.pth`
- Confirmed it was a valid GPU run with the corrected `Rot90(k=3)` pipeline.
- Short-run validation results:
  - epoch 1: `recog/1-N.E.D = 0.1690`
  - epoch 2: `recog/1-N.E.D = 0.4173`
- Compared with old broken SAR run:
  - old best val `recog/1-N.E.D = 0.1863` at epoch 5
  - corrected SAR reaches `0.4173` by epoch 2, so the direction fix is effective and the run is worth extending.
- Training loss was finite and decreased from about `6.59` early epoch 1 to around `2.90` near the end of epoch 2.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended/manual short run:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options train_cfg.max_epochs=2 default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/short_mthv2_sar_k3_retry_0601-0025`
- Running:
  - none for SAR after short run completed

Latest log directory:

- Short SAR run: `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025`

Next step:

- Launch corrected SAR 30-epoch full training on GPU1. Once the formal run is confirmed started, remove the short-run log directory per the user's cleanup instruction.

## Latest Update 2026-06-01 11:03 Asia/Shanghai

Completed in this step:

- Launched corrected SAR 30-epoch full training on GPU1.
- Confirmed valid GPU execution:
  - `CUDA available: True`
  - `GPU number: 1`
  - checkpoint directory: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`
- Confirmed corrected `Rot90(k=3)` train/val/test pipeline is active.
- First training progress:
  - epoch 1 iter `100/5261`
  - loss: `6.1157`
  - memory: `18828 MiB`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_k3_full_gpu1_0601`
- Ended:
  - corrected SAR short run at `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025`

Latest log directory:

- Full SAR run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Delete the short-run directory `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025` per cleanup instruction, then continue monitoring the full SAR run.

## Latest Update 2026-06-01 11:04 Asia/Shanghai

Completed in this step:

- Deleted the short SAR run directory after formal full training started:
  - removed `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025`
- Formal corrected SAR long training remains active in the managed session.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_k3_full_gpu1_0601`
- Ended/removed:
  - short run `/home/ubuntu/mmocr/work_dirs/short_mthv2_sar_k3_retry_0601-0025`

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Continue monitoring the formal SAR run through epoch 1 validation. If validation is healthy, let it continue to 30 epochs.

## Latest Update 2026-06-01 11:20 Asia/Shanghai

Completed in this step:

- Read current experiment summary and latest available aggregate result table:
  - `logs/paper_results_summary.md` (Last updated: 2026-06-01)
- Wrote a full paper first draft based on completed code paths and finished experiments:
  - `experiments/notes/paper_draft_v1.md`
- Draft positioning:
  - unified pretraining + head reconstruction + decode calibration pipeline
  - paper-style narrative already aligned with current reproducible metrics in repository logs
  - experiment section intentionally kept at medium detail (can be expanded later)

Modified files:

- `experiments/notes/paper_draft_v1.md`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running in this step:
  - none newly launched by this step
- Ended in this step:
  - none

Latest log directory / result source:

- `logs/paper_results_summary.md`
- (for current ongoing MMOCR long run context) `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Produce `paper_draft_v2` with:
  - abstract/title refinement for submission style,
  - explicit method module naming consistency,
  - tightened claim wording for CCF B/C review tolerance,
  - and a compact experiment protocol subsection (without overlong implementation detail).

## Latest Update 2026-06-01 11:19 Asia/Shanghai

Completed in this step:

- Revised `experiments/notes/paper_draft_v1.md` in place based on user feedback.
- Removed the overly colloquial discussion sentence:
  - `UniVCP 的关键价值在于“系统性收益”而非单模块刷分`
- Strengthened the paper story around a cautious but defensible method contribution:
  - structure-aware query-based localization pretraining,
  - character-head reconstruction / mapped initialization,
  - CTC blank/nonblank calibration.
- Added a related-work subsection for detection-style structural priors.
- Added a method subsection explaining how character-box supervision is used as a pretraining signal, not as a separate two-stage inference pipeline.
- Fixed a title wording issue after review.

Modified files:

- `experiments/notes/paper_draft_v1.md`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running in this step:
  - none newly launched by this step
- Ended in this step:
  - none

Latest log directory / result source:

- `logs/paper_results_summary.md`
- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601` remains the latest ongoing MMOCR run context from previous status.

Next step:

- Continue polishing the paper draft directly in place unless the user asks for a separate versioned file.
- For method claims, keep the detection-style contribution framed as "structure-aware localization pretraining inspired by query-based detection", not as a wholly new detector.

## Latest Update 2026-06-01 12:34 Asia/Shanghai

Completed in this step:

- Confirmed the full MTHv2 stage-1 pretraining run has completed:
  - log directory: `logs/mthv2_full_stage1_det_0531-1258`
  - final checkpoint: `logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth`
  - final saved epoch checkpoint: `logs/mthv2_full_stage1_det_0531-1258/checkpoint0005.pth`
- Verified this is the corrected detection-style stage-1 run, not the earlier bad CTC run:
  - command: `main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_det_0531-1258 -c config/MTHV2_stage1.py --save_log`
  - config has `mode_chr=False`
  - training log contains detection losses: `train_loss_ce`, `train_loss_bbox`, `train_loss_giou`
  - no CTC-only loss pattern like the earlier bad run
- Final epoch-5 training metrics:
  - `train_loss`: `3.6403`
  - `train_class_error`: `2.8232`
  - `train_loss_ce`: `0.0442`
  - `train_loss_bbox`: `0.2067`
  - `train_loss_giou`: `0.2490`
- Compared with trusted MTH1000+MTH1200 stage-1 baseline qualitatively:
  - trusted baseline final epoch-6 `train_loss`: `3.5682`
  - trusted baseline final epoch-6 `train_class_error`: `3.0956`
  - new MTHv2 full stage-1 is numerically close on training losses and slightly lower final class error, but cannot be judged useful until box diagnostics are run.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended:
  - `main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --output_dir logs/mthv2_full_stage1_det_0531-1258 -c config/MTHV2_stage1.py --save_log`
- Running in this step:
  - none newly launched yet

Latest log directory:

- `logs/mthv2_full_stage1_det_0531-1258`

Next step:

- Run MTH1000 validation box diagnostic for `logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth` and compare it to `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`.
- Only if the diagnostic is competitive should this checkpoint be used for head reconstruction / finetuning.

## Latest Update 2026-06-01 12:39 Asia/Shanghai

Completed in this step:

- Ran MTH1000 validation box diagnostic for the completed full MTHv2 stage-1 checkpoint.
- First attempt inside default sandbox failed because CUDA was not visible and `MSDeformAttn` fell back to unsupported CPU execution:
  - failure: `RuntimeError: Not implemented on the CPU`
- Re-ran the same diagnostic on GPU successfully.
- New diagnostic output:
  - directory: `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601`
  - summary: `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601/summary.json`
  - records: `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601/records.json`
  - images: `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601/images`
- Full MTHv2 stage-1 diagnostic metrics on 100 MTH1000-valid samples:
  - `avg_blank_ratio_full`: `0.8416`
  - `avg_pred_nonblank_count`: `142.6`
  - `avg_gt_len`: `7.49`
  - `real_gt_box_rate`: `0.98`
- Trusted MTH1000+MTH1200 stage-1 baseline on the same 100-sample diagnostic:
  - directory: `debug_vis/mth1000_mth1200_stage1_on_mth1000_valid_0513`
  - `avg_blank_ratio_full`: `0.9547`
  - `avg_pred_nonblank_count`: `40.79`
  - `avg_gt_len`: `7.49`
  - `real_gt_box_rate`: `0.98`
- Initial interpretation:
  - the completed full MTHv2 stage-1 is valid and learned column-localized boxes,
  - but it is much more nonblank-active than the trusted baseline (`142.6` vs `40.79` predicted nonblank queries for the same average GT length),
  - so it should be treated as a risky / weakly useful stage-1 checkpoint until downstream head reconstruction proves otherwise.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Completed diagnostic on GPU:
  - `MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/diagnose_boxes.py -c config/MTHV2_stage1.py --dataset_file mth1000 --checkpoint logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth --split valid --device cuda:0 --num_workers 0 --num_samples 100 --viz_topk 40 --show_gt_boxes --output_dir debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601 --options mth1000_root=tkhmth2200_mth1000_dtlr mth1000_raw_root=TKHMTH2200/MTH1000 mth1000_use_char_boxes=True num_classes=6727`
- Running in this step:
  - none

Latest log / diagnostic directory:

- training: `logs/mthv2_full_stage1_det_0531-1258`
- diagnostic: `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601`

Next step:

- Do not claim the full-MTHv2 stage-1 is better than the trusted baseline from training loss alone.
- If continuing, run a controlled head-reconstruction smoke/full run from `logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth` and compare validation CER, empty prediction rate, and short-text buckets against `logs/mthv2_mth1000mth1200tkh_full_0528-0957`.

## Latest Update 2026-06-01 12:45 Asia/Shanghai

Completed in this step:

- Decided the correct next step is controlled classification-head reconstruction, not direct full finetuning.
- Re-read the previous MTHv2 head reconstruction command:
  - baseline head run: `logs/mthv2_mth1000mth1200tkh_head_0528-0003`
  - old command used `--resume logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth --new_class_embedding --smart_mapping`
- For the full-MTHv2 stage-1 checkpoint, the equivalent setup should use:
  - `--resume logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth`
  - `--new_class_embedding --smart_mapping`
  - `--path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl`
- Rationale:
  - the stage-1 checkpoint already used the MTHv2 union charset (`num_classes=6727`),
  - but head reconstruction is still needed to switch from detection-style stage-1 into CTC recognition finetuning,
  - and the downstream validation result is needed because box diagnostic showed nonblank over-activation.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running in this step:
  - none yet
- Ended in this step:
  - none

Latest log / diagnostic directory:

- training: `logs/mthv2_full_stage1_det_0531-1258`
- diagnostic: `debug_vis/mthv2_full_stage1_det_on_mth1000_valid_0601`

Next step:

- Run a 1-step head-reconstruction smoke from `logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth`.
- If the smoke passes, launch the normal 3-epoch MTHv2 head reconstruction run and compare it against `logs/mthv2_mth1000mth1200tkh_head_0528-0003`.

## Latest Update 2026-06-01 13:17 Asia/Shanghai

Completed in this step:

- Attempted the first 1-step MTHv2 head-reconstruction smoke from the completed full-MTHv2 stage-1 checkpoint.
- The run failed before training due to a class-count mismatch:
  - `config/MTHV2_dtlr.py` default `num_classes=6700`
  - full-MTHv2 stage-1 checkpoint / charset has `6727` classes
  - classifier keys were skipped during checkpoint load
  - then `--smart_mapping` tried to index class `6700` in a size-`6700` classifier
- Failure:
  - `IndexError: index 6700 is out of bounds for dimension 0 with size 6700`
- Failed smoke log directory:
  - `logs/mthv2_full_stage1_head_smoke_0601`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Failed:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth --new_class_embedding --smart_mapping --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --output_dir logs/mthv2_full_stage1_head_smoke_0601 -c config/MTHV2_dtlr.py --save_log --start_epoch 1 --options batch_size=1 lr=1e-4 epochs=2 eval_epoch=999 max_iterations=2 max_optimizer_steps=1`
- Running:
  - none

Latest log / diagnostic directory:

- failed smoke: `logs/mthv2_full_stage1_head_smoke_0601`
- stage-1 source: `logs/mthv2_full_stage1_det_0531-1258`

Next step:

- Re-run the smoke with explicit `--options num_classes=6727 ...` so the model classifier shape matches the full-MTHv2 stage-1 checkpoint before smart mapping.

## Latest Update 2026-06-01 13:24 Asia/Shanghai

Completed in this step:

- Re-ran the full-MTHv2 stage-1 head-reconstruction smoke with explicit `num_classes=6727`.
- Confirmed the previous class-count failure was fixed:
  - checkpoint load reported `<All keys matched successfully>` before head reconstruction,
  - no `IndexError` from smart mapping.
- The run then entered full validation before the intended 1-step training, so it was not a useful smoke.
- Stopped the validation-only smoke process to avoid wasting GPU0.
- Confirmed process `3986311` is gone and GPU0 is free again.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Started then stopped:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth --new_class_embedding --smart_mapping --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --output_dir logs/mthv2_full_stage1_head_smoke_0601_num6727 -c config/MTHV2_dtlr.py --save_log --start_epoch 1 --options num_classes=6727 batch_size=1 lr=1e-4 epochs=2 eval_epoch=999 max_iterations=2 max_optimizer_steps=1`
- Terminated:
  - `kill -TERM 3986311`
- Running:
  - no DTLR head-reconstruction process
  - MMOCR SAR remains active on GPU1 from previous work

Latest log / diagnostic directory:

- failed first smoke: `logs/mthv2_full_stage1_head_smoke_0601`
- validation-entered second smoke: `logs/mthv2_full_stage1_head_smoke_0601_num6727`
- stage-1 source: `logs/mthv2_full_stage1_det_0531-1258`

Next step:

- Yes, run classification-head reconstruction next.
- Use the normal 3-epoch head reconstruction command with explicit `num_classes=6727`.
- Treat it as a controlled candidate run because the stage-1 box diagnostic suggests nonblank over-activation.

## Latest Update 2026-06-01 13:39 Asia/Shanghai

Completed in this step:

- Created a concise repository map:
  - `PROJECT_MAP.md`
- Included only key directories, important training/evaluation scripts, config locations, data/log locations, trusted baselines, and tests.
- Verified the file length:
  - `87 PROJECT_MAP.md`
  - under the requested 200-line limit.
- Applied the user's context-protection rule during inspection:
  - unknown or potentially large command output was byte-capped with `head -c`.

Modified files:

- `PROJECT_MAP.md`
- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running in this step:
  - none
- Ended in this step:
  - none

Latest log / result source:

- `PROJECT_MAP.md`
- `experiments/notes/goal_status.md`

Next step:

- Continue from the latest experiment status if requested:
  - run the controlled MTHv2 direct CTC finetune / head-adaptation comparison from `logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth`.

## Latest Update 2026-06-01 14:56 Asia/Shanghai

Completed in this step:

- Confirmed the formal full-MTHv2 stage-1 -> MTHv2 head reconstruction run completed.
- Log directory:
  - `logs/mthv2_fullstage1pre_mthv2_head_0601`
- Source stage-1 checkpoint:
  - `logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth`
- Best / final checkpoint files exist:
  - `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint.pth`
  - `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth`
- Command used:
  - `finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth --new_class_embedding --smart_mapping --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_head_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-4 epochs=3 eval_epoch=1 max_iterations=10000`
- Validation results:
  - epoch 0 CER: `0.1687470099455089`
  - epoch 1 CER: `0.1578794820103037`
  - epoch 2 CER: `0.15283326830434354`
  - best checkpoint is epoch 2.
- Compared against previous MTHv2 head baseline:
  - previous log: `logs/mthv2_mth1000mth1200tkh_head_0528-0003`
  - previous best epoch-2 CER: `0.14526833428705468`
  - new head is worse by about `0.00756` absolute CER.
- Interpretation:
  - the full-MTHv2 stage-1 checkpoint is usable for CTC head reconstruction,
  - but this head result does not beat the old MTH1000+MTH1200 stage-1 -> MTHv2 head baseline,
  - consistent with the earlier box diagnostic warning that full-MTHv2 stage-1 had stronger nonblank over-activation.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended:
  - formal full-MTHv2 stage-1 head reconstruction, output at `logs/mthv2_fullstage1pre_mthv2_head_0601`
- Running in this step:
  - none newly launched

Latest log directory:

- `logs/mthv2_fullstage1pre_mthv2_head_0601`

Next step:

- Do not claim the full-MTHv2 stage-1 head is better than the old MTHv2 head baseline.
- If continuing this branch, either:
  - run a direct no-head-rebuild CTC finetune from `logs/mthv2_full_stage1_det_0531-1258/checkpoint.pth` for a fair comparison, or
  - run full finetune from `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth` only as a candidate, not as the mainline.

## Latest Update 2026-06-01 13:45 Asia/Shanghai

Completed in this step:

- Re-checked SAR after user reported the short run was done.
- Confirmed corrected SAR short run had already completed earlier and was used to start the formal long run.
- Current formal SAR long-run status:
  - log: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/20260601_110115/20260601_110115.log`
  - epoch 1 validation: `recog/1-N.E.D = 0.1521`
  - epoch 2 training finished and epoch 2 validation is in progress
  - latest observed epoch 2 validation progress: `400/685`
  - GPU1 memory: about `22032 MiB`
- Note: epoch 1 of the formal long run is weaker than the earlier short run's epoch 2 result (`0.4173`), so wait for epoch 2 validation before judging the long run.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - corrected SAR 30-epoch full training on GPU1, work dir `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`
- Ended:
  - corrected SAR short run, already deleted per cleanup rule after full run started

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Read epoch 2 validation result once it finishes. If epoch 2 remains far below the short-run `0.4173`, reassess whether to continue SAR full training or restart from the short checkpoint.

## Latest Update 2026-06-01 15:31 Asia/Shanghai

Completed in this step:

- Checked whether the corrected SAR full training was stuck.
- Current time: `2026-06-01 15:30 CST`.
- SAR full-run log status:
  - latest log line is still epoch 2 validation `400/685` at `2026-06-01 13:44:19`
  - log file modification time is also `13:44:19`
  - no epoch 2 validation result was written
- GPU/process status:
  - GPU1 utilization is `0%`, but about `22032 MiB` remains allocated
  - `nvidia-smi --query-compute-apps` reports PID `3954753` with process name `[Not Found]`
  - `ps -fp 3954753` cannot find the process, and `/proc/3954753` does not exist
- Interpretation:
  - the SAR full training is stuck/abnormally dead, not merely slow validation
  - GPU1 has stale CUDA memory from a dead or unreachable process

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Stuck/abnormal:
  - corrected SAR full training in `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`
- Running normally:
  - none confirmed for SAR

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Do not keep waiting. Clear the stale GPU1 allocation, then restart/resume SAR from `epoch_2.pth` or restart the full run with a safer validation setting such as fewer validation workers / no persistent workers.

## Latest Update 2026-06-01 15:35 Asia/Shanghai

Completed in this step:

- Received instruction to clear the stuck SAR GPU1 state and continue from epoch 2.
- Planned recovery path:
  1. stop the stuck/held SAR training session if still attached
  2. verify GPU1 memory is released; if not, clear stale GPU1 allocation
  3. resume from `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/epoch_2.pth`
  4. use safer validation settings: `val_dataloader.num_workers=0`, `val_dataloader.persistent_workers=False`, `test_dataloader.num_workers=0`, `test_dataloader.persistent_workers=False`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Stuck/abnormal:
  - SAR full run in `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`, stuck at epoch 2 val `400/685`
- Running recovery:
  - starting now

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Stop/clear the stuck GPU1 state, then resume SAR from `epoch_2.pth` with safer validation dataloader settings.

## Latest Update 2026-06-01 16:00 Asia/Shanghai

Completed in this step:

- Adopted the new rule: future training should be launched through `tmux` so it is not tied to the Codex tool session.
- Confirmed the previous interrupted full finetune had no saved checkpoint, so relaunched from the head checkpoint instead of trying to resume the incomplete run.
- Started a new tmux-backed full finetune session:
  - tmux session: `dtlr_mthv2_full_ft_0601`
  - output directory: `logs/mthv2_fullstage1pre_mthv2_full_tmux_0601`
  - source checkpoint: `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth`
- Confirmed startup:
  - `<All keys matched successfully>`
  - epoch `0` has started
  - early CTC loss is normal, around `0.77~0.91` in the first few logged steps

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running in tmux session `dtlr_mthv2_full_ft_0601`:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_full_tmux_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000`

Latest log directory:

- `logs/mthv2_fullstage1pre_mthv2_full_tmux_0601`

Next step:

- Let the tmux run continue without frequent polling.
- Later check `logs/mthv2_fullstage1pre_mthv2_full_tmux_0601/info.txt` for epoch `0` validation CER and compare against `logs/mthv2_mth1000mth1200tkh_full_0528-0957`.

## Latest Update 2026-06-01 15:57 Asia/Shanghai

Completed in this step:

- Checked suspected interruption of `logs/mthv2_fullstage1pre_mthv2_full_0601`.
- Confirmed no active `finetuning.py` process was found from the current shell.
- Latest log line in `info.txt` stops at:
  - epoch `0`
  - step `3160/42088`
  - average CTC loss `0.6061`
  - max memory `14010 MiB`
- No traceback/error line was found in the visible log tail.
- No checkpoint was saved; epoch `0` validation did not run.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended/interrupted before validation:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_full_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000`

Latest log directory:

- `logs/mthv2_fullstage1pre_mthv2_full_0601`

Next step:

- Relaunch the same full finetune in a persistent shell/nohup or tmux-style background command so it is not tied to the Codex tool session.

## Latest Update 2026-06-01 15:43 Asia/Shanghai

Completed in this step:

- Monitored the full finetune candidate past `2000` training steps.
- Current run remains healthy:
  - epoch `0`
  - observed progress around `2010/42088`
  - average CTC loss about `0.6104`
  - max observed memory about `14010 MiB`
- No evidence of the previous high-loss failure pattern.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_full_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000`

Latest log directory:

- `logs/mthv2_fullstage1pre_mthv2_full_0601`

Next step:

- Continue to the epoch `0` validation point and compare the first valid CER with the old full-MTHv2 baseline.

## Latest Update 2026-06-01 15:39 Asia/Shanghai

Completed in this step:

- Monitored the full finetune candidate through the first `1000+` training steps.
- Current run remains healthy:
  - epoch `0`
  - observed progress around `1040/42088`
  - average CTC loss improved to about `0.65`
  - max observed memory about `12831 MiB`
- Reminder for continuation:
  - although the loader displays `42088` batches, `finetuning.py` uses `max_iterations=10000` as a per-epoch sample cap, so each epoch should stop after roughly `5000` optimizer steps with `batch_size=2`.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_full_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000`

Latest log directory:

- `logs/mthv2_fullstage1pre_mthv2_full_0601`

Next step:

- Continue monitoring until epoch `0` validation finishes; use that CER as the first decision point.

## Latest Update 2026-06-01 15:38 Asia/Shanghai

Completed in this step:

- Cleared the stuck SAR GPU1 state.
- Found real orphan SAR worker/training PIDs holding `/dev/nvidia1`:
  - `3968395 3968491 3968523 3968555 3968587 3968619`
- Terminated them with `kill -TERM`.
- Verified GPU1 is clean:
  - `GPU1 memory used = 0 MiB`
  - no compute apps remain in `nvidia-smi --query-compute-apps`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended/cleared:
  - stuck SAR full run orphan processes from `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`
- Running:
  - none after cleanup

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Resume SAR from `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/epoch_2.pth` with safer dataloader settings for validation/test: `num_workers=0`, `persistent_workers=False`.

## Latest Update 2026-06-01 15:39 Asia/Shanghai

Completed in this step:

- First resume attempt failed before launch because MMOCR `tools/train.py --resume` is a boolean flag and does not accept a checkpoint path argument.
- No training process was started by this failed command.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Failed before launch:
  - `... tools/train.py ... --resume /home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/epoch_2.pth ...`
- Running:
  - none

Latest log directory:

- recovery target: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`

Next step:

- Retry with MMEngine-style config overrides: `resume=True` and `load_from=/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/epoch_2.pth`.

## Latest Update 2026-06-01 15:38 Asia/Shanghai

Completed in this step:

- Checked the running full finetune candidate after launch.
- Current run is healthy:
  - epoch `0`
  - observed progress around `770/42088`
  - average CTC loss around `0.67~0.70`
  - max observed memory about `12627 MiB`
- This is not the earlier broken high-loss run; the loss scale is consistent with a resumed CTC finetuning branch.

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_full_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000`

Latest log directory:

- `logs/mthv2_fullstage1pre_mthv2_full_0601`

Next step:

- Wait for epoch `0` validation, then compare valid CER against `logs/mthv2_mth1000mth1200tkh_full_0528-0957`.

## Latest Update 2026-06-01 15:45 Asia/Shanghai

Completed in this step:

- User decided the full-MTHv2 stage-1 head result is close enough to try downstream full finetuning.
- Decision:
  - proceed with full finetune from `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth`
  - treat it as a candidate branch, not a replacement for the old MTHv2 mainline yet.
- Baseline to compare:
  - old full run: `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
  - old full checkpoint: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`
  - old head CER baseline: `0.14526833428705468`
  - new head CER: `0.15283326830434354`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- About to launch:
  - full finetune candidate from `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth`

Latest log directory:

- source head: `logs/mthv2_fullstage1pre_mthv2_head_0601`

Next step:

- Launch `logs/mthv2_fullstage1pre_mthv2_full_0601` with 12 epochs, `lr=1e-5`, `batch_size=2`, `max_iterations=10000`, and explicit `num_classes=6727`.

## Latest Update 2026-06-01 15:36 Asia/Shanghai

Completed in this step:

- Launched full finetune candidate from the full-MTHv2 stage-1 head checkpoint.
- Output directory:
  - `logs/mthv2_fullstage1pre_mthv2_full_0601`
- Source checkpoint:
  - `logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth`
- Confirmed checkpoint loading:
  - `<All keys matched successfully>`
- Confirmed training started normally:
  - epoch `0`
  - early loss around `0.14` to `0.66`, not the earlier bad CTC loss explosion
  - max observed memory in startup output: about `10377 MiB`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `/home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth_combo --num_workers 0 --resume logs/mthv2_fullstage1pre_mthv2_head_0601/checkpoint_best_regular.pth --new_class_embedding --smart_mapping --resume_finetuning --path_old_charset logs/mthv2_full_stage1_det_0531-1258/charset.pkl --save_log --output_dir logs/mthv2_fullstage1pre_mthv2_full_0601 -c config/MTHV2_dtlr.py --options num_classes=6727 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000`

Latest log directory:

- `logs/mthv2_fullstage1pre_mthv2_full_0601`

Next step:

- Monitor epoch 0 validation.
- Compare first validation CER against the old full baseline trajectory in `logs/mthv2_mth1000mth1200tkh_full_0528-0957`.

## Latest Update 2026-06-01 15:36 Asia/Shanghai

Completed in this step:

- Resumed corrected SAR training from epoch 2 checkpoint with safer validation/test dataloaders.
- Successful resume details:
  - checkpoint loaded: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/epoch_2.pth`
  - log dir: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`
  - log confirms: `resumed epoch: 2, iter: 10522`
  - val/test dataloaders now use `num_workers=0`, `persistent_workers=False`
- Confirmed training continues after resume:
  - epoch 3 iter `100/5261`
  - loss: `3.1440`
  - GPU1 active at about `100%`, memory about `19722 MiB`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Running:
  - `CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options resume=True load_from=/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/epoch_2.pth default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False`
- Ended/abandoned due to val hang:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Latest log directory:

- Active resumed run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`
- Previous stuck run: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601`

Next step:

- Monitor the resumed run through epoch 3 validation. If validation completes without hanging, let the 30-epoch SAR training continue.

## Latest Update 2026-06-01 16:01 Asia/Shanghai

Completed in this step:

- Rechecked user report that GPU1/SAR is stuck again.
- Confirmed the active resumed SAR run is stuck:
  - active log: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval/20260601_153434/20260601_153434.log`
  - last log line: epoch 3 training `1300/5261` at `2026-06-01 15:47:11`
  - current time checked: `2026-06-01 16:00 CST`
  - GPU1 utilization: `0%`, memory still allocated
- Found SAR orphan PIDs from the resumed run:
  - `4037201 4037202 4037265 4037297 4037329 4037361`
- Important diagnosis:
  - this hang happened during training, not validation
  - previous safe settings only changed val/test dataloaders
  - likely remaining trigger is `train_dataloader.num_workers=8` with `persistent_workers=True`

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Stuck/abnormal:
  - `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`
- Running normally:
  - DTLR full finetune on GPU0 is separate; do not kill it

Latest log directory:

- stuck SAR resume: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`

Next step:

- Kill only SAR orphan PIDs, then resume again from `epoch_2.pth` with train/val/test dataloaders all set to `num_workers=0`, `persistent_workers=False`.

## Latest Update 2026-06-01 16:02 Asia/Shanghai

Completed in this step:

- Killed the second stuck SAR orphan PID group:
  - `4037201 4037202 4037265 4037297 4037329 4037361`
- Verified GPU1 is free again:
  - GPU1 memory used about `3 MiB`
  - only GPU0 DTLR process remains active

Modified files:

- `experiments/notes/goal_status.md`

Training/evaluation commands:

- Ended/cleared:
  - stuck SAR resumed run `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`
- Running:
  - no SAR process after cleanup

Latest log directory:

- cleared stuck SAR resume: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`

Next step:

- Start a second safe resume from `epoch_2.pth`, this time with train/val/test dataloaders all set to `num_workers=0` and `persistent_workers=False`.

## Latest Update 2026-06-01 16:04 Asia/Shanghai

Completed in this step:

- Confirmed SAR on GPU1 had repeated the same hang pattern in the previous resume run:
  - log stopped at `2026-06-01 15:47:11` around epoch 3 iteration 1300.
  - GPU1 was at 0% utilization while holding about 19722 MiB.
  - orphan SAR/MMOCR worker processes were present under PPID 1.
- Cleared only the stuck SAR/MMOCR GPU1 processes; did not touch the GPU0 DTLR run.
- Restarted SAR from the completed epoch-2 checkpoint with all dataloader workers disabled.
- Confirmed the new run is alive:
  - GPU1 utilization is 100%.
  - managed session output reached epoch 3 iteration 200/5261.

Modified files:

- `experiments/notes/goal_status.md`

Training commands:

- Ended/cleared stuck SAR resume on GPU1:
  - old work dir: `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_safeval`
  - reason: hung during epoch 3 training with GPU idle and orphan worker processes.
- Running SAR all-workers=0 resume on GPU1:

```bash
CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib /home/ubuntu/miniconda3/envs/openmmlab/bin/python tools/train.py /home/ubuntu/DTLR/experiments/configs/mmocr/sar_r31_parallel_decoder_mthv2_k3.py --cfg-options resume=True load_from=/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601/epoch_2.pth default_hooks.checkpoint.save_best=recog/1-N.E.D default_hooks.checkpoint.rule=greater default_hooks.checkpoint.max_keep_ckpts=1 work_dir=work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_allworkers0 train_dataloader.num_workers=0 train_dataloader.persistent_workers=False val_dataloader.num_workers=0 val_dataloader.persistent_workers=False test_dataloader.num_workers=0 test_dataloader.persistent_workers=False
```

Latest log directory:

- `/home/ubuntu/mmocr/work_dirs/mthv2_sar_k3_full_gpu1_0601_resume_e2_allworkers0/20260601_160150`

Next step:

- Continue monitoring the all-workers=0 SAR resume through epoch 3 validation. If it hangs again with workers disabled, stop treating SAR as a stable long-run baseline in this environment and record the failure mode.

## Latest Update 2026-06-02 10:30 Asia/Shanghai

Completed in this step:

- Launched full-MTHv2 stage-1 query-budget experiment on GPU0 in tmux.
- The run starts from the trusted MTH1000+MTH1200 stage-1 checkpoint rather than training full-MTHv2 from scratch.
- Early log confirms the trusted checkpoint loaded successfully and detection training has started.

Training command:

```bash
tmux new-session -d -s dtlr_qbudget_mthv2_gpu0_0602 "cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python main_synthetic.py --device cuda:0 --dataset_file mth_combo --num_workers 2 --pretrain_model_path logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth --new_class_embedding --smart_mapping --path_old_charset logs/mth1000_mth1200_stage1_0512-1755/charset.pkl --save_log --output_dir logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602 -c config/MTHV2_stage1_query_budget.py --options num_classes=6700"
```

Latest log directory:

- `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602`

Next step:

- After stage-1 checkpoint is available, run MTH1000 valid box diagnostic before any head reconstruction. Compare against `debug_vis/mth1000_mth1200_stage1_on_mth1000_valid_0513/summary.json`, especially predicted nonblank count, blank ratio, and box quality.

## Latest Update 2026-06-03 CHDAC Data Preparation

Completed in this step:

- Confirmed raw CHDAC data is available at `data/CHDAC`.
- Added a reproducible preparation script for CHDAC polygon column annotations:
  - `tools/prepare_chdac_dtlr.py`
- Generated DTLR-style single-column data:
  - `data/chdac_dtlr`

Generated dataset summary:

- Page-level split seed: `42`
- Page splits: train `800`, valid `100`, test `100`
- Column samples: train `39291`, valid `5968`, test `4755`
- Total column samples: `50014`
- Skipped annotations: `2` empty transcriptions
- Unique chars: `10364`

Next step:

- If using CHDAC for recognition experiments, load it through the MTH1000-style dataset path with `mth1000_root=chdac_dtlr`, `mth1000_raw_root=CHDAC`, and `mth1000_image_ext=jpg`.

## Latest Update 2026-06-03 Query-Budget Stage-1 Completion

Completed in this step:

- `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602` finished all 6 stage-1 epochs.
- Final checkpoint:
  - `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/checkpoint.pth`
- Ran MTH1000 valid box diagnostic:
  - `debug_vis/mthv2_stage1_qbudget_from_mth1000mth1200_on_mth1000_valid_0603`

Diagnostic result:

- avg predicted nonblank count: `43.11`
- avg GT length: `7.49`
- avg blank ratio: `0.9521`
- real GT box rate: `0.98`

Comparison:

- Trusted MTH1000+MTH1200 stage-1 baseline predicted nonblank count: `40.79`
- Failed full-MTHv2 stage-1 predicted nonblank count: `142.6`
- Interpretation: query-budget continuation removes the full-MTHv2 over-activation problem and is close to the trusted baseline, but it is not clearly better than the trusted baseline by box count alone.

Next step:

- If continuing, run MTHv2 head reconstruction from this checkpoint and require early validation CER to beat the old MTHv2 head baseline (`0.14526833428705468` at epoch 2) before full finetuning.

## Latest Update 2026-06-03 Query-Budget MTHv2 Head Reconstruction Launch

Launched in tmux:

- Session: `dtlr_qbudget_mthv2_head_0603`
- Output: `logs/mthv2_qbudgetstage1pre_mthv2_head_0603`
- Source checkpoint: `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/checkpoint.pth`
- Source charset: `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl`
- Dataset/config: `mth_combo`, `config/MTHV2_dtlr.py`
- Key options: `num_classes=6727`, `batch_size=2`, `lr=1e-4`, `epochs=3`, `eval_epoch=1`, `max_iterations=10000`

Decision rule:

- Continue to full finetuning only if early validation CER beats the old MTHv2 head baseline `0.14526833428705468` at epoch 2.

## Latest Update 2026-06-03 Query-Budget MTHv2 Head Reconstruction Completion

Completed:

- Run: `logs/mthv2_qbudgetstage1pre_mthv2_head_0603`
- Best checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth`
- Source checkpoint: `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/checkpoint.pth`
- Dataset/config: `mth_combo`, `config/MTHV2_dtlr.py`
- Key options: `num_classes=6727`, `batch_size=2`, `lr=1e-4`, `epochs=3`, `eval_epoch=1`, `max_iterations=10000`

Validation CER by epoch:

- epoch 0: `0.15521017329137315`
- epoch 1: `0.14871916177468655`
- epoch 2: `0.14544023603979653`

Comparison:

- Old MTHv2 head baseline epoch-2 CER: `0.14526833428705468`
- Full-MTHv2 stage-1 head epoch-2 CER: `0.15283326830434354`
- Query-budget head is much better than the full-MTHv2 over-activated branch, but still slightly worse than the old MTH1000+MTH1200 stage-1 head baseline by about `0.000172` absolute CER.

Decision:

- Under the current standard of requiring improvement over the old MTH1000+MTH1200 baseline, do not proceed to full finetuning from this query-budget head by default.
- The result is useful as evidence that query-budget fixes the full-MTHv2 over-activation failure mode, but not yet useful as a replacement mainline.

## Latest Update 2026-06-03 Query-Budget MTHv2 Full Finetune Launch

Launched as a candidate branch despite the query-budget head being slightly worse than the old head baseline, because the gap is very small and full finetuning may change the trajectory.

Launched in tmux:

- Session: `dtlr_qbudget_mthv2_full_0603`
- Output: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- Source head checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth`
- Source charset: `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl`
- Dataset/config: `mth_combo`, `config/MTHV2_dtlr.py`
- Key options: `num_classes=6727`, `batch_size=2`, `lr=1e-5`, `epochs=12`, `eval_epoch=1`, `max_iterations=10000`

Launch check:

- Checkpoint load reported `<All keys matched successfully>`.
- Training entered CTC full finetuning on GPU0.

Decision rule:

- Compare early validation CER against old full MTHv2 baseline trajectory and current trusted full result `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`.
- Keep it only if validation CER shows a plausible path to beat the old full baseline; otherwise treat it as a useful negative/near-miss ablation for the paper.

## Latest Update 2026-06-03 Query-Budget MTHv2 Full Finetune Completion

Completed:

- Run: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- Best checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth`
- Final checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint.pth`

Validation CER by epoch:

- epoch 0: `0.11822557932137827`
- epoch 1: `0.12044717928196699`
- epoch 2: `0.10834695743309848`
- epoch 3: `0.10711328798946732`
- epoch 4: `0.10767763679584931`
- epoch 5: `0.1024624169269506`
- epoch 6: `0.10359242330433224`
- epoch 7: `0.10127716468336462`
- epoch 8: `0.14689929218654876`
- epoch 9: `0.3068244873715812`
- epoch 10: `0.22137397198915923`
- epoch 11: `0.18417224677094474`

Comparison:

- Old MTHv2 full baseline best valid CER: `0.11397798822246911` at `logs/mthv2_mth1000mth1200tkh_full_0528-0957`
- Query-budget full best valid CER: `0.10127716468336462`
- Absolute valid CER improvement: about `0.01270`
- Relative valid CER improvement: about `11.1%`

Interpretation:

- This candidate branch is clearly useful by validation CER and is now the strongest MTHv2 full-finetune validation result observed so far.
- Later epochs degrade badly after epoch 7, so use `checkpoint_best_regular.pth`, not the final checkpoint.

Next required reporting:

- Run clean CTC error analysis on valid/test.
- Run validation decode-bias sweep and apply selected calibration to test.
- Report CER/AR/CR, empty prediction rate, pred/GT length ratio, and length buckets before updating the paper result table.

## Latest Update 2026-06-03 Query-Budget MTHv2 Test Clean Metrics

Completed test clean micro evaluation for:

- Run: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- Checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth`
- Result file: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_clean_0603.json`

Metrics:

- Samples: `10455`
- CER micro: `3.83`
- AR micro: `96.17`
- CR micro: `96.29`
- Empty pred: `2.89`
- Pred/GT length ratio: `0.982`
- Len=1/2/3-5/6-10/11+ CER: `31.56 / 23.16 / 17.92 / 11.62 / 1.98`

Comparison:

- Old MTHv2 clean test: CER `4.47`, AR `95.53`, CR `95.71`.
- Old MTHv2 bias test: CER `3.90`, AR `96.10`, CR `96.37`.
- Query-budget clean already beats the old clean result and slightly beats the old bias result by CER, but old bias still has slightly higher CR and lower empty-pred rate.

Updated:

- `logs/paper_results_summary.md`
- `logs/paper_results_summary.csv`
- `experiments/notes/mthv2_qbudget_full_0603_analysis.md`

## Latest Update 2026-06-03 Query-Budget MTHv2 Valid Clean Metrics

Completed valid clean micro evaluation for:

- Run: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- Checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth`
- Result file: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_valid_clean_0603.json`

Metrics:

- Samples: `10948`
- CER micro: `4.37`
- AR micro: `95.63`
- CR micro: `95.75`
- Empty pred: `2.67`
- Pred/GT length ratio: `0.980`
- Len=1/2/3-5/6-10/11+ CER: `23.89 / 20.13 / 16.65 / 11.03 / 2.63`

Comparison:

- Old MTHv2 clean valid: CER `5.20`, AR `94.80`, CR `95.03`.
- Old MTHv2 bias valid: CER `4.56`, AR `95.44`, CR `95.82`.
- Query-budget clean valid already beats the old clean and old bias validation CER, but old bias still has slightly higher CR.

Updated:

- `logs/paper_results_summary.md`
- `logs/paper_results_summary.csv`
- `experiments/notes/mthv2_qbudget_full_0603_analysis.md`

Next:

- Run qbudget validation decode-bias sweep, then apply the selected bias to qbudget test.

## Latest Update 2026-06-03 Query-Budget MTHv2 Bias Metrics

Completed validation decode-bias sweep and test-bias evaluation for:

- Run: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- Checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/checkpoint_best_regular.pth`
- Validation sweep: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/decode_bias_sweep_valid_0603.json`
- Test result: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/micro_test_bias_b-20_nb08_0603.json`

Selected validation setting:

- Bias: `blank=-2.0`, `nonblank=0.8`
- Valid CER/AR/CR: `3.76 / 96.24 / 96.45`
- Valid empty pred: `0.56`
- Valid Pred/GT length ratio: `0.997`

Test metrics:

- Samples: `10455`
- CER micro: `3.31`
- AR micro: `96.69`
- CR micro: `96.90`
- Empty pred: `0.89`
- Pred/GT length ratio: `0.997`
- Len=1/2/3-5/6-10/11+ CER: `27.95 / 19.48 / 14.86 / 10.46 / 1.72`

Comparison:

- Old MTHv2 bias test: CER `3.90`, AR `96.10`, CR `96.37`.
- Query-budget bias test: CER `3.31`, AR `96.69`, CR `96.90`.
- This is now the best MTHv2-combo result in the current paper table.

Updated:

- `logs/paper_results_summary.md`
- `logs/paper_results_summary.csv`
- `experiments/notes/mthv2_qbudget_full_0603_analysis.md`
