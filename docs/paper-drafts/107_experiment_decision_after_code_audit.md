# Experiment Decision After Code Audit

Date: 2026-06-08

This note focuses only on experiments and model evidence. It does not revise
paper prose. The purpose is to decide, from the current DTLR code and existing
artifacts, whether SAQT already has enough evidence for a conservative CCF-B
submission and which DTLR-side modifications are still worth running.

## Current Judgment

The current code and experiments are enough for a conservative CCF-B submission
candidate, provided the paper claims are scoped to vertical ancient
single-column recognition and avoid SOTA or broad robustness wording. The
paper-facing model should be SAQT: localization-supervised queries converted
into a sorted CTC recognizer, with charset-aware classifier adaptation and
full-model recognition finetuning.

The main remaining work is not to add a generic backbone or another large
recognizer. The remaining experimental work should be limited to targeted
controls that close reviewer questions.

## Paper-Facing Evidence

| Evidence item | Artifact | Result | Decision |
| --- | --- | --- | --- |
| MTHv2 main result | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608` | calibrated test AR/CR `96.75/97.00`, CER `3.25` | Main MTHv2 result. |
| HDRC main result | `logs/hdrc_qbudget_full_0607` | calibrated test AR/CR `93.44/94.36`, CER `6.56` | Main HDRC result; call it qbudget-localization-query variant. |
| MTHv2 qbudget ablation | `logs/mthv2_mth1000mth1200tkh_full_0528-0957` vs `logs/mthv2_qbudgetstage1pre_mthv2_full_0603` | calibrated AR/CR `96.10/96.37 -> 96.69/96.90` | Use as query-budget evidence. |
| MTHv2 expected-count auxiliary | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603` vs `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608` | calibrated AR/CR `96.69/96.90 -> 96.75/97.00` | Optional MTHv2-only module, not central contribution. |
| HDRC charset-aware adaptation | `logs/hdrc_charset_random_full_visible1_0605` vs `logs/mth1000mth1200pre_hdrcft_full_0527-1732` | calibrated AR/CR `82.72/83.97 -> 90.70/91.80` | Strong module evidence. |
| Full finetuning after head reconstruction | MTHv2 head/full and HDRC head/full rows in `logs/paper_results_summary.md` | MTHv2 `93.83/95.03 -> 96.69/96.90`; HDRC `85.97/89.72 -> 90.70/91.80` | Strong pipeline evidence. |
| Character-localization information learning | `logs/mthv2_no_structure_ctc_full_0605` | calibrated AR/CR `0.11/0.16` | Use as conservative lower-bound control only. |

## Current Code Modules

| Module in code/config | Main files | Current evidence | Paper decision |
| --- | --- | --- | --- |
| Query budget / localization-query learning | `models/dino/dino.py`, qbudget stage-1 configs | Positive on MTHv2; HDRC variant positive but not single-factor | Keep as SAQT core. |
| CTC expected-count auxiliary | `ctc_count_loss_coef` in configs; criterion in `models/dino/dino.py` | MTHv2 positive; HDRC count001 regressed | Optional MTHv2 ablation only. |
| Charset-aware classifier adaptation | `finetuning.py` smart mapping path and HDRC random-head control | Strong HDRC gain | Keep as core adaptation component. |
| Query sequence refiner / sorted CTC refiner | `QuerySequenceRefiner`, `use_query_sequence_refiner`, `use_sorted_ctc_refiner` | SQR valid CER `0.146524`; sorted CTC refiner `0.142689`; matched base `0.118792` | Stop. |
| DCTC-lite / Viterbi alignment | `ctc_viterbi_loss_coef`, `compute_ctc_viterbi_alignment_loss` | valid CER `0.120219`, worse than matched base | Stop. |
| Glyph prototype auxiliary | `use_glyph_prototype_head`, `glyph_proto_aux_loss_coef` | 1000-step positive `0.112549`, 2000-step regressed `0.116865`, count+proto negative `0.121235` | Internal only; not paper-ready. |
| Blank cap / blank regularization | `config/MTHV2_dtlr_blankcap.py` | valid CER `0.122598`, worse than matched base | Stop. |
| MSR-v2 resize/sampling policy | `config/MTHV2_dtlr_msr_v2_probe.py` | valid CER `0.130381`, worse than matched base | Stop. |
| LGQ activation-gated adapter | `use_query_activation_head`, `use_query_count_loss`, `use_activation_gating` | smoke valid CER `0.148588`, worse than head-only | Stop current setting; redesign only with a new mechanism. |

## Queue To Run If tmux/CUDA Are Available

The prepared queue is in `logs/paper_experiment_queue_0608/`.

| Priority | Queue item | Run dir | Why run | Keep criterion |
| --- | --- | --- | --- | --- |
| 1 | MTHv2 length-balanced sampling | `logs/mthv2_length_balance_v2_resume_1000_0608` | Tests short-column weakness without changing architecture | valid CER below `0.118792`; no clear long-column regression. |
| 2 | HDRC no-localization control | `logs/hdrc_no_structure_ctc_full_0608` | Extends structure-learning lower-bound evidence beyond MTHv2 | Use as lower-bound control; not expected to be competitive. |
| 3 | MTHv2 count003 | `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count003_0608` | Tests whether weaker expected-count preserves MTHv2 gain | test-bias CER at or below `0.0325` to compete with count001. |
| 4 | HDRC count003 | `logs/hdrc_qbudget_full_ctc_count003_0608` | Tests whether weaker expected-count avoids HDRC count001 regression | test-bias CER at or below `0.0656`; otherwise internal only. |

Audit command:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python tools/audit_paper_experiment_queue.py
```

Machine-readable audit command:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python tools/audit_paper_experiment_queue.py --format json
```

CCF-B readiness audit command:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python tools/audit_ccfb_readiness.py --format markdown
```

This audit reads the metric JSON artifacts directly and reports:

- current CCF-B verdict;
- evidence type for paper-facing claims;
- paper-facing modules that can be written as SAQT components;
- code references and experiment artifacts for each paper-facing module;
- main paper-claim evidence status;
- open experiment debts and keep criteria;
- protocol risks and mitigation wording;
- modules that should not be continued for this paper, including negative
  result evidence.

Current readiness verdict from existing artifacts:

```text
CCF-B_CANDIDATE_WITH_OPEN_EXPERIMENT_DEBT
```

Launch command when tmux and CUDA are available:

```bash
tmux new-session -d -s dtlr_paper_exp_queue_0608 'cd /home/ubuntu/DTLR && logs/paper_experiment_queue_0608/run_gpu0_priority_queue_0608.sh'
```

## What Not To Do Next

Do not open a generic backbone replacement branch for this paper. It would be
expensive, weakly tied to the current SAQT contribution, and would create a new
baseline burden.

Do not keep tuning SQR, sorted CTC refiner, DCTC-lite, blank cap, MSR-v2, or the
first LGQ adapter setting. They have matched negative evidence.

Do not make CHDAC a main dataset in the current paper. The best current CHDAC
calibrated AR/CR is `66.87/68.73`, which weakens the story rather than
strengthening it.

## Practical Submission Path

1. Use MTHv2 and HDRC as the two main datasets.
2. Use AR/CR as the main paper metrics, with CER kept in internal tables and
   audit files.
3. Present direct decoding and validation-protocol calibrated decoding without
   overstating calibration as a model contribution.
4. Use expected-count only as an optional MTHv2-positive regularizer.
5. If one more experiment can run, run the queue above in priority order; stop
   when either the first useful strengthening result is obtained or the queue
   produces only internal controls.
