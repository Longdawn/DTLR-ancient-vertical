# Current Decision and Launch State

Date: 2026-06-08

This note is the short operational answer to the current project question:
whether the present code and experiments are enough for a CCF-B submission, what
still needs to be tested, and what model changes should or should not be opened.

## Current CCF-B Judgment

SAQT is a credible CCF-B submission candidate if the paper is framed as a
focused method for cropped vertical ancient single-column recognition. The
current evidence is not broad enough for SOTA, robustness, or universal-module
claims, but it is enough for a conservative method paper with two main datasets,
unified recognition baselines, and module ablations.

The defensible contribution is:

1. character-localization information learning for detection-style queries;
2. vertical query sorting and query-to-CTC sequence conversion;
3. charset-aware classifier adaptation for target character-set mismatch;
4. classifier-head reconstruction followed by full-model recognition training;
5. optional expected-count auxiliary on MTHv2 only;
6. development-set fixed blank/nonblank calibration as evaluation protocol.

## Evidence That Is Already Strong Enough

| Claim | Evidence | Decision |
| --- | --- | --- |
| SAQT beats the adapted STR baselines under the current protocol | MTHv2 qbudget-count001 calibrated AR/CR `96.75/97.00`; HDRC qbudget-localization-query calibrated AR/CR `93.44/94.36` | Use as main result, no SOTA wording. |
| Character-localization learning is practically needed for the current query-to-CTC path | MTHv2 no-localization calibrated AR/CR `0.11/0.16` | Use as lower-bound control only. |
| Query activation budget helps | MTHv2 single-factor `96.10/96.37 -> 96.69/96.90`; HDRC variant `93.44/94.36` | Use MTHv2 as ablation and HDRC as variant-level evidence. |
| Charset-aware classifier adaptation matters on target charset mismatch | HDRC random-head `82.72/83.97` vs charset-aware `90.70/91.80` | Use as strong HDRC module evidence. |
| Full recognition training is needed after head reconstruction | MTHv2 `93.83/95.03 -> 96.69/96.90`; HDRC `85.97/89.72 -> 90.70/91.80` | Use as pipeline evidence. |
| Expected-count can help | MTHv2 `96.69/96.90 -> 96.75/97.00`; HDRC count branch failed | Keep optional and MTHv2-scoped. |

## What Is Still Missing Before Submission

The main remaining work is submission QA, not a new architecture branch:

1. final reference verification;
2. final LaTeX/Overleaf compile check;
3. figure/table consistency check;
4. one final reproducible postprocess pass for all paper-facing JSON rows if time permits;
5. optional length-balanced sampling probe only if tmux execution becomes available.

Completed static QA:

- `docs/paper-drafts/tools/verify_result_tables.py` checks 31 paper-facing
  result rows against their JSON metric artifacts.
- Latest run: `checked_rows=31`, `warnings=0`, `failures=0`.

## Experiment Launch State

Current GPU check:

- GPU0: idle, `8 MiB / 24576 MiB`, utilization `0%`.
- GPU1: idle, `0 MiB / 24576 MiB`, utilization `0%`.
- No active `finetuning.py`, `main_synthetic.py`, `torchrun`, CTC eval, or decode sweep process was found.

Attempted next experiment:

```bash
tmux new-session -d -s dtlr_mthv2_length_balance_v2_16000_0608 'cd /home/ubuntu/DTLR && logs/mthv2_length_balance_v2_resume_1000_0608/run_length_balance_probe_0608.sh'
```

Result:

- Sandbox `tmux ls` failed with `Operation not permitted`.
- Escalated tmux launch was rejected by the execution environment.
- Because project rules require long training in `tmux`, the run was not started.
- Do not replace this with foreground, `nohup`, or another workaround unless the user explicitly changes the long-training rule.

## Next Experiment If tmux Becomes Available

Run the MTHv2 length-balanced sampling probe on physical GPU0:

```bash
tmux new-session -d -s dtlr_mthv2_length_balance_v2_16000_0608 'cd /home/ubuntu/DTLR && logs/mthv2_length_balance_v2_resume_1000_0608/run_length_balance_probe_0608.sh'
```

Why this is first:

- It targets the remaining MTHv2 short-column weakness without changing the model.
- Code support and smoke verification already exist.
- It is low-risk compared with opening another architecture branch.

Keep criterion:

- Validation CER must beat `logs/mthv2_base_resume_1000_0607` at `0.11879202286282202`.
- Empty prediction rate should not rise materially.
- Long-column performance should not regress enough to offset short-column gains.

If it passes:

- Postprocess clean valid/test.
- Run validation decode-bias sweep.
- Apply fixed bias to test.
- Only then consider adding it as an optional training ablation.

If it fails:

- Keep it internal.
- Do not replace it with a generic backbone swap.
- Proceed with the existing conservative SAQT paper.

## Module Changes To Avoid Now

| Candidate | Decision |
| --- | --- |
| Generic backbone replacement | Avoid; weakly tied to the SAQT contribution and costly. |
| SQR / sorted CTC refiner | Stop; matched probes were negative. |
| DCTC-lite / Viterbi alignment | Stop; negative and more complex. |
| Blank probability cap | Stop; worsened validation CER. |
| LGQ activation-gated adapter, first setting | Stop; smoke validation CER `14.8588%`, worse than head-only. |
| Glyph prototype auxiliary | Keep internal; evidence is unstable. |
| CHDAC as a main dataset | Do not use now; current result is too weak and dilutes the story. |

## Paper Handling

The cleanest paper story is:

- use MTHv2 and HDRC as main datasets;
- compare against adapted scene-text recognition models under unified AR/CR;
- present direct and calibrated decoding side by side;
- keep calibration as protocol;
- call HDRC qbudget result a qbudget-localization-query variant, not a pure ablation;
- write expected-count as optional and MTHv2-positive only.

This is enough to continue toward a CCF-B submission package. It is not enough
to mark the whole project complete, because final submission QA and optional
length-balanced evidence are still open.
