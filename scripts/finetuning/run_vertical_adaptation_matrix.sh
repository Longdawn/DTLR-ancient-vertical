#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# User-tunable environment
CONDA_ENV="${CONDA_ENV:-DB}"
USE_CONDA="${USE_CONDA:-1}"
PYTHON_BIN="${PYTHON_BIN:-}"
DRY_RUN="${DRY_RUN:-1}"    # 1: print only, 0: execute
START_FROM="${START_FROM:-all}"  # all|scratch|hinit|dapt1|dapt2
GPU_IDS="${GPU_IDS:-0,1}"  # e.g. 0 for single card, 0,1 for dual card

# Horizontal-pretrained checkpoint (can be overridden)
HORIZ_CKPT="${HORIZ_CKPT:-logs/mth1000_bidirectional_overnight/checkpoint_best_regular.pth}"
DAPT1_CKPT="logs/mth1000_vertical_dapt_phase1_e20/checkpoint_best_regular.pth"

if [[ -n "$PYTHON_BIN" ]]; then
  PY_CMD=("$PYTHON_BIN")
elif [[ "$USE_CONDA" == "1" ]] && command -v conda >/dev/null 2>&1; then
  PY_CMD=(conda run -n "$CONDA_ENV" python)
elif [[ -x "DTLR/bin/python" ]]; then
  PY_CMD=(DTLR/bin/python)
else
  PY_CMD=(python)
fi

run_or_echo() {
  local -a cmd=("$@")
  echo "[CMD] ${cmd[*]}"
  if [[ "$DRY_RUN" == "0" ]]; then
    "${cmd[@]}"
  fi
}

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "[ERROR] missing file: $path" >&2
    exit 1
  fi
}

run_finetune() {
  local out_dir="$1"
  shift
  local -a extra=("$@")
  local gpu_count=0
  IFS=',' read -r -a gpu_list <<< "$GPU_IDS"
  gpu_count="${#gpu_list[@]}"
  local device_arg="cuda"
  local -a launch_prefix=()
  local -a runner_cmd=("${PY_CMD[@]}")

  if [[ "$gpu_count" -le 1 ]]; then
    device_arg="cuda:0"
    if [[ "$gpu_count" -eq 1 ]]; then
      launch_prefix=(env CUDA_VISIBLE_DEVICES="${gpu_list[0]}")
    fi
  else
    launch_prefix=(env CUDA_VISIBLE_DEVICES="$GPU_IDS")
    runner_cmd+=( -m torch.distributed.run --nproc_per_node="$gpu_count" )
  fi

  local -a base=(
    "${launch_prefix[@]}"
    "${runner_cmd[@]}" finetuning.py
    --device "$device_arg"
    --dataset_file mth1000
    --num_workers 2
    --new_class_embedding
    --output_dir "$out_dir"
    -c config/MTH1000_vertical.py
  )

  run_or_echo "${base[@]}" "${extra[@]}"
}

# 1) scratch baseline
if [[ "$START_FROM" == "all" || "$START_FROM" == "scratch" ]]; then
  run_finetune "logs/mth1000_vertical_scratch_e30" \
    --options epochs=30 eval_epoch=2 lr=1e-4 auto_lr_patience=2
fi

# 2) horizontal->vertical direct finetune
if [[ "$START_FROM" == "all" || "$START_FROM" == "hinit" ]]; then
  require_file "$HORIZ_CKPT"
  run_finetune "logs/mth1000_vertical_hinit_e30" \
    --resume "$HORIZ_CKPT" \
    --options epochs=30 eval_epoch=2 lr=1e-4 auto_lr_patience=2
fi

# 3) vertical domain-adaptive stage-1 (continued pretraining style)
if [[ "$START_FROM" == "all" || "$START_FROM" == "dapt1" ]]; then
  require_file "$HORIZ_CKPT"
  run_finetune "logs/mth1000_vertical_dapt_phase1_e20" \
    --resume "$HORIZ_CKPT" \
    --options epochs=20 eval_epoch=2 lr=5e-5 auto_lr_patience=2
fi

# 4) vertical domain-adaptive stage-2 finetune
if [[ "$START_FROM" == "all" || "$START_FROM" == "dapt2" ]]; then
  if [[ "$DRY_RUN" == "0" ]]; then
    require_file "$DAPT1_CKPT"
  fi
  run_finetune "logs/mth1000_vertical_dapt_phase2_e30" \
    --resume "$DAPT1_CKPT" \
    --options epochs=30 eval_epoch=2 lr=1e-4 auto_lr_patience=2
fi

echo ""
echo "Done. DRY_RUN=$DRY_RUN"
echo "GPU_IDS=$GPU_IDS"
echo "Tip: after runs, summarize metrics with:"
echo "  ${PY_CMD[*]} scripts/finetuning/summarize_vertical_runs.py"
