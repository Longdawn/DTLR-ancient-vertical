#!/usr/bin/env bash
set -euo pipefail

WAIT_PID="${1:?usage: $0 <stage1_pid>}"
ROOT="/home/ubuntu/DTLR"
STAGE1_DIR="logs/mth1000_mth1200_stage1_vmsr_safe_0516-2346"
CHAIN_LOG="${ROOT}/logs/auto_start_vmsr_head_after_stage1_0517.log"

cd "${ROOT}"

{
  echo "[$(date '+%m/%d %H:%M:%S')] waiting for stage1 pid ${WAIT_PID}"
  while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -qx "${WAIT_PID}"; do
    sleep 300
  done

  echo "[$(date '+%m/%d %H:%M:%S')] stage1 pid ${WAIT_PID} exited"

  if [[ ! -s "${STAGE1_DIR}/checkpoint.pth" ]]; then
    echo "[$(date '+%m/%d %H:%M:%S')] missing ${STAGE1_DIR}/checkpoint.pth; abort"
    exit 1
  fi

  TS="$(date +%m%d-%H%M)"
  OUT_DIR="logs/mth1000mth1200vmsrpre_mth1000ft_head_${TS}"
  echo "[$(date '+%m/%d %H:%M:%S')] starting head finetune -> ${OUT_DIR}"

  /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py \
    --device cuda:0 \
    --dataset_file mth1000 \
    --num_workers 0 \
    --resume "${STAGE1_DIR}/checkpoint.pth" \
    --new_class_embedding \
    --smart_mapping \
    --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl \
    --save_log \
    --output_dir "${OUT_DIR}" \
    -c config/MTH1000_dtlr.py \
    --options \
      mth1000_root=tkhmth2200_mth1000_dtlr \
      mth1000_raw_root=TKHMTH2200/MTH1000 \
      num_classes=6700 \
      batch_size=2 \
      lr=1e-4 \
      epochs=3 \
      eval_epoch=1 \
      max_iterations=10000

  echo "[$(date '+%m/%d %H:%M:%S')] head finetune finished"
} >> "${CHAIN_LOG}" 2>&1
