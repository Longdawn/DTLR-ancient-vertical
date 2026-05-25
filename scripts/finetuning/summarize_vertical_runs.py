#!/usr/bin/env python3
import json
from pathlib import Path

RUNS = [
    "mth1000_vertical_scratch_e30",
    "mth1000_vertical_hinit_e30",
    "mth1000_vertical_dapt_phase1_e20",
    "mth1000_vertical_dapt_phase2_e30",
]


def load_rows(log_path: Path):
    rows = []
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def pick_metric(row, keys):
    for k in keys:
        if k in row:
            return row[k]
    return None


def summarize_one(run_name: str):
    log_path = Path("logs") / run_name / "log.txt"
    if not log_path.exists():
        return {
            "run": run_name,
            "status": "missing_log",
        }

    rows = load_rows(log_path)
    if not rows:
        return {
            "run": run_name,
            "status": "empty_log",
        }

    metric_keys = ["test_cer_oracle_direction", "test_cer"]
    blank_keys = ["test_blank_pred_ratio_unscaled"]

    valid = []
    for r in rows:
        cer = pick_metric(r, metric_keys)
        if cer is not None:
            valid.append((cer, r))

    if valid:
        best_cer, best_row = min(valid, key=lambda x: x[0])
    else:
        best_cer, best_row = None, rows[-1]

    last_row = rows[-1]

    return {
        "run": run_name,
        "status": "ok",
        "epochs_logged": len(rows),
        "best_epoch": best_row.get("epoch"),
        "best_cer": pick_metric(best_row, metric_keys),
        "best_blank": pick_metric(best_row, blank_keys),
        "last_epoch": last_row.get("epoch"),
        "last_cer": pick_metric(last_row, metric_keys),
        "last_blank": pick_metric(last_row, blank_keys),
    }


def main():
    print("run\tstatus\tepochs\tbest_epoch\tbest_cer\tbest_blank\tlast_epoch\tlast_cer\tlast_blank")
    for run in RUNS:
        s = summarize_one(run)
        print(
            f"{s.get('run')}\t{s.get('status')}\t{s.get('epochs_logged','-')}\t"
            f"{s.get('best_epoch','-')}\t{s.get('best_cer','-')}\t{s.get('best_blank','-')}\t"
            f"{s.get('last_epoch','-')}\t{s.get('last_cer','-')}\t{s.get('last_blank','-')}"
        )


if __name__ == "__main__":
    main()
