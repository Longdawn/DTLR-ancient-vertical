# SAQT Project Guide

This repository is for SAQT vertical ancient text recognition experiments. It
retains some DTLR/DINO-compatible module, config, data, and log names for
checkpoint reproducibility.

## Long-Term Project Rules

- This project is vertical ancient-book text recognition.
- Scope is single-column / line-level recognition only.
- Do not frame the project as page-level layout analysis, full-page detection, reading-order prediction, or document layout parsing.
- Prefer Chinese when answering the user unless they explicitly request another language.
- Before modifying code, configs, training logic, evaluation logic, or experiment scripts, read `docs/CODEX_HANDOFF.md` first.
- Long training must be launched in `tmux`; do not run long training in a foreground Codex exec session.
- Report experiments with CER/AR/CR and length-bucket metrics. A result is not paper-ready if it only has training loss or a single aggregate CER.
- For recognition experiments, include short-text behavior when available: `len=1`, `len=2`, `len=3-5`, `len=6-10`, `len>=11`, empty prediction rate, and pred/GT length ratio.
- Keep `experiments/notes/goal_status.md` updates sparse: update only for launches, validation results, training completion, failures, or major result/file changes.
- Commands with unknown or potentially large output must be byte-capped, for example `2>&1 | head -c 4000`.

## Core Entry Points

- `main_synthetic.py`: stage-1 detection pretraining.
- `finetuning.py`: head reconstruction and full MTH1000 finetuning.
- `tools/diagnose_boxes.py`: box diagnostic on validation splits.
- `evaluation.py`: standalone evaluation path when needed.

## Data And Config Conventions

- Paper-facing MTHv2 config: `config/SAQT_MTHV2.py`
- Paper-facing HDRC config: `config/SAQT_HDRC.py`
- Legacy vertical line finetuning config: `config/MTH1000_dtlr.py`
- Best real stage-1 config: `config/MTH1000_MTH1200_stage1.py`
- Ancient synthetic best-size config: `config/SynthVerticalAncient100k_stage1_bestcfg.py`
- Processed line datasets usually live under `data/*_dtlr`; this suffix is a
  compatibility data-format name, not the paper-facing method name.
- Logs always live under `logs/`
- Box diagnostics always live under `debug_vis/`

## Trusted Mainline Baselines

- Best real stage-1 checkpoint:
  - `logs/mth1000_mth1200_stage1_0512-1755/checkpoint.pth`
- Best head reconstruction from real stage-1:
  - `logs/mth1000mth1200pre_mth1000ft_head_0513-2057/checkpoint_best_regular.pth`
- Best full finetuning mainline:
  - `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth`
  - Best observed CER: about `0.1510`

Use these as the default comparison points unless the user explicitly changes the baseline.

## Experiment Rules

- Do not judge an experiment by training loss alone.
- For finetuning, prioritize:
  - best validation CER
  - len=1 / len=2 behavior
  - empty-string rate
  - whether short-text improvements trade off against long-text regression
- For stage-1 pretraining, require a box diagnostic before recommending head reconstruction or full finetuning.
- Compare new stage-1 checkpoints against the trusted real stage-1 baseline on MTH1000 valid.
- Treat blank collapse and nonblank over-activation as different failure modes.

## Stage-1 Iteration Budget Rule

For `main_synthetic.py` stage-1 runs, total optimization budget is controlled by:

- `len(train_loader) * epochs`

Do not assume `max_iterations` will stop the run early. In this project, stage-1 detection training has repeatedly ignored `max_iterations` in practice.

## Change Discipline

- Do not silently alter shared baseline configs when creating a new experiment.
- Prefer adding a new config file or explicit `--options` override.
- When proposing a launch command, provide one full command line.
- When comparing runs, use exact log paths and exact checkpoint paths.
- Do not delete logs, datasets, or checkpoints unless the user explicitly asks.

## Synthetic Data Notes

- Low-resolution stage-1 synthetic runs can look numerically stable but transfer poorly.
- A synthetic stage-1 checkpoint should not be used downstream unless its MTH1000 valid box diagnostic is competitive with the trusted real stage-1 baseline.
