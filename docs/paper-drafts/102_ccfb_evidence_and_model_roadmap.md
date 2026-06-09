# CCF-B Evidence and Model Roadmap

Date: 2026-06-08

## Current Judgment

SAQT is now a plausible CCF-B-level submission candidate if it is framed conservatively and supported by the current evidence table. It is not yet a polished submission package. The strongest version is not "DTLR applied to ancient text", but a structure-aware query transfer framework for single-column vertical ancient text recognition:

- character-localization supervision teaches detection-style queries to carry character evidence and vertical ordering;
- sorted queries become a CTC recognition sequence rather than final detection outputs;
- charset-aware classifier adaptation handles target charset changes;
- full recognition finetuning is necessary after classifier-head reconstruction;
- a lightweight expected-count auxiliary loss gives a modest MTHv2 improvement, but is not yet a universal cross-dataset module.

The current evidence is enough for a conservative "method + ablation + baseline comparison" story on MTHv2 and HDRC. It is not enough for strong SOTA, broad robustness, or universal module claims.

## Evidence Already Usable

| Evidence | Current status | Paper use |
| --- | --- | --- |
| Main MTHv2 result | qbudget-count001 calibrated AR/CR `96.75/97.00`, CER `3.25`; original qbudget calibrated AR/CR `96.69/96.90`, CER `3.31` | main result |
| Main HDRC result | qbudget-localization-query calibrated AR/CR `93.44/94.36`, CER `6.56`; original HDRC calibrated AR/CR `90.70/91.80`, CER `9.30` | main result |
| Adapted scene-text baselines | CRNN/SVTR/ABINet/SAR on MTHv2 and HDRC | baseline comparison |
| Localization-supervised query learning | MTHv2 no-localization CTC collapses to `0.11/0.16` AR/CR after calibration | lower-bound structural control |
| Query activation budget | MTHv2 calibrated AR/CR improves from `96.10/96.37` to `96.69/96.90`; HDRC qbudget-localization-query variant reaches `93.44/94.36` | MTHv2 single-factor evidence plus HDRC variant evidence |
| Charset-aware classifier adaptation | HDRC random-head `82.72/83.97` vs charset-aware `90.70/91.80` | target-charset adaptation evidence |
| Classification-head reconstruction vs full-model recognition training | MTHv2 `93.83/95.03` vs `96.69/96.90`; HDRC `85.97/89.72` vs `90.70/91.80` | recognition-stage evidence |
| Expected-count auxiliary loss | MTHv2 qbudget clean CER `3.83 -> 3.67`, calibrated CER `3.31 -> 3.25`; HDRC count001 failed | optional MTHv2-positive auxiliary ablation, not a universal core module |

## Remaining Weak Points

1. Query activation budget has finalized MTHv2 single-factor evidence and HDRC qbudget-localization-query variant evidence. The HDRC result must be interpreted carefully because the candidate checkpoint also includes extra localization-supervised query learning, so it is not a pure query-budget ablation.
2. The no-localization control is very weak. This is useful as a lower-bound control, but the paper must not claim the entire gap is a pure causal effect of character boxes.
3. Expected-count is MTHv2-positive but HDRC-negative. It should be written as a lightweight sequence-length regularizer that can help in the MTHv2 setting, not as the central contribution.
4. Results are single-run. Avoid "stable", "robust", "significant", "SOTA", or broad generalization claims.
5. Citation metadata, figure QA, and LaTeX build QA are still submission-level debts.

## Module Screening Result

| Candidate module | Evidence | Decision |
| --- | --- | --- |
| Query-budget localization queries | MTHv2 and HDRC positive under final postprocess | Keep as a main SAQT design element. |
| Charset-aware classifier adaptation | HDRC random-head control is much worse | Keep as a method module and ablation. |
| Full recognition finetuning | Head-only is worse on MTHv2 and HDRC | Keep as a method stage. |
| CTC expected-count auxiliary loss `0.01` | MTHv2 positive, HDRC negative | Use as optional MTHv2 ablation; do not overclaim. |
| Decode calibration | Strong and consistent, but validation-selected postprocess | Keep in experimental protocol; describe carefully. |
| LGQ adapter / activation gating | Smoke validation worse than baseline | Do not include. |
| SQR / sorted CTC refiner | 1000-step probes negative | Stop. |
| DCTC-lite Viterbi alignment | 1000-step probe negative | Stop. |
| Glyph prototype auxiliary | 1000-step positive, 2000-step regressed, combination negative | Internal weak signal only. |
| Blank-cap | Negative | Stop. |
| MSR-v2 resize policy | valid CER `0.130381` vs base `0.118792` | Stop; gains are not explained by simple resize. |
| Length-balanced sampling | Sampler support fixed and smoke verified; no real CER yet | Next feasible probe, but not paper evidence yet. |

## Immediate Next Experiment

The only low-risk next experiment worth running is the matched MTHv2 length-balanced sampling probe. It tests whether the remaining short-column weakness is partly a data distribution issue. It is not a core architecture contribution, but a positive result could support an optional "short-column-aware training" paragraph or a small ablation.

See also `docs/paper-drafts/103_recent_method_scan_and_experiment_queue.md`
for the broader recent-method scan and module triage.

Current technical status:

- Code support added in `datasets/MTHCombo.py`: MTHCombo now exposes flattened `samples`.
- Config added: `config/MTHV2_dtlr_length_balance_probe.py`.
- Unit test added: `tests/test_mth_combo_dataset.py`, verifying flattened
  `samples` exposure without changing child-dataset index routing.
- Smoke verified:
  - output: `logs/mthv2_length_balance_smoke_0608`
  - log contains `Using length-balanced WeightedRandomSampler`
  - raw train length counts: `1=9006`, `2=7785`, `3-5=10310`, `6-10=8279`, `11+=48796`
  - effective sampling distribution: `1=0.2347`, `2=0.1352`, `3-5=0.1343`, `6-10=0.0719`, `11+=0.4238`
- Launch status: a real tmux launch was attempted again on 2026-06-08 after
  confirming GPU0 was idle, but the sandbox could not connect to the tmux
  socket and the escalated retry was rejected by the execution environment.
  Therefore the probe remains technically ready but has no real validation CER.
- Latest operational note: `docs/paper-drafts/105_current_decision_and_launch_state.md`
  records the current GPU0 idle check, the rejected tmux launch, and the rule
  that this run should not be started through foreground or `nohup` workaround.

Run command when tmux execution is available:

```bash
tmux new-session -d -s dtlr_mthv2_length_balance_v2_16000_0608 'cd /home/ubuntu/DTLR && logs/mthv2_length_balance_v2_resume_1000_0608/run_length_balance_probe_0608.sh'
```

Decision rule:

- Compare against `logs/mthv2_base_resume_1000_0607` valid CER `0.11879202286282202`.
- If valid CER improves and blank ratio does not rise materially, promote to a longer MTHv2 run.
- If overall CER worsens or only short buckets improve at clear long-column cost, keep it as internal analysis.
- Do not add to `logs/paper_results_summary.md` without clean/test, validation-bias sweep, and fixed-bias test postprocess.

## Completed HDRC QBudget-Localization Variant

Completed head stage:

- `logs/hdrc_qbudget_head_0607`
- GPU: physical GPU0 only
- initialization checkpoint: `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/checkpoint.pth`
- reference charset: `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/charset.pkl`
- best clean valid CER: `19.34`, better than the HDRC head-only clean valid CER `20.56`

Completed full run:

- `logs/hdrc_qbudget_full_0607`
- tmux session: `hdrc_qbudget_full_0607`
- GPU: physical GPU0 only
- checkpoint source: `logs/hdrc_qbudget_head_0607/checkpoint_best_regular.pth`
- status: early-stopped after epoch 2/3 validation regression. Epoch 1 remains the best checkpoint with clean valid CER `9.60%`.
- postprocess: completed with `FORCE_POSTPROCESS=1` on 2026-06-07.
- clean test: AR/CR `91.50/91.64`, CER `8.50`.
- development-set calibrated test: bias `-2.0/1.0`, AR/CR `93.44/94.36`, CER `6.56`.

Paper wording if successful:

- Safe: "the qbudget-localization query variant also improves HDRC under the same downstream protocol."
- Unsafe: "query budget alone causes the HDRC improvement."

## LGQ Adapter Smoke Result

The best "our own model" direction is not a backbone swap. Replacing ResNet or adding a generic Transformer block would be easy to dismiss as engineering. The distinctive technical point in SAQT is the query-to-CTC bridge:

1. queries are learned with character-localization supervision;
2. predicted boxes provide vertical ordering;
3. sorted query logits are converted into a CTC sequence;
4. blank/nonblank behavior determines whether the sequence under-decodes or over-activates.

The most defensible module is therefore a Localization-Guided Query-to-CTC Adapter.

Minimal version:

- add a query activation head on decoder query features;
- sort activation logits with the same vertical order as query logits;
- use activation to adjust blank/nonblank logits before CTC;
- keep CTC as the main objective;
- optionally use a very weak count regularizer, but do not present count loss as the contribution.

Recommended first config:

```python
use_query_activation_head = True
query_activation_init_bias = -4.0
use_activation_gating = True
activation_gate_blank_coef = 0.10
activation_gate_nonblank_coef = 0.10
use_query_count_loss = True
query_count_loss_coef = 0.001
query_count_short_weight = 1.0
```

Current implementation status:

- Experiment config added: `config/MTHV2_dtlr_lgq_adapter.py`
- Smoke command recorded in `docs/paper-drafts/101_query_to_ctc_adapter_design.md`
- Shared model code is unchanged; the config uses existing hooks in `models/dino/dino.py`.
- CPU-side verification on 2026-06-07 passed: `tests/test_query_activation_module.py` ran 7 tests successfully and `config/MTHV2_dtlr_lgq_adapter.py` compiled.
- GPU smoke completed on physical GPU0: `logs/mthv2_lgq_adapter_smoke_0607`.
- Smoke result: no fatal shape/key error and checkpoints were written, but validation CER is `14.8588%` with blank ratio `0.989749`, worse than the MTHv2 qbudget head-only starting point at about `8.56%` validation CER.
- Decision: do not continue this LGQ setting to a full run, and do not include it in the current paper body.

Minimum validation for any future adapter revision:

- smoke on MTHv2 qbudget head checkpoint;
- require no blank-collapse;
- compare against MTHv2 qbudget full baseline `96.69/96.90`;
- include only if it improves or gives a clear diagnostic. If it hurts, keep it internal.

## Submission Strategy

HDRC qbudget-localization-query has succeeded as a variant-level result:

- include it as additional target-domain evidence;
- keep claim strength medium;
- do not describe it as a pure query-budget ablation;
- proceed to citation, figure, and LaTeX QA.

The LGQ adapter smoke under the first activation-gating configuration is now a negative internal result. A future adapter revision would need a different gate initialization, weaker blank/nonblank shifts, or a warm-up schedule before it is worth a full run.

The paper is currently viable as a conservative CCF-B submission candidate, not yet a polished submission package.
