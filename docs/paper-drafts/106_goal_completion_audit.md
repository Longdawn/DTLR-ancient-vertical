# Goal Completion Audit

Date: 2026-06-08

This document audits the current state against the active project objective:
judge whether the current code and comparison experiments can support a CCF-B
paper, identify missing experiments and possible DTLR modifications, shape the
work into our own SAQT paper, and use GPU0 only if experiments are needed.

## Verdict

Status: not complete, but substantially advanced.

The repository now contains enough verified evidence and draft material for a
credible conservative CCF-B submission candidate. It is not yet a final
submission package because local LaTeX compilation is unverified, references
still need final primary-source/style review, and the optional length-balanced
probe cannot currently be launched due to tmux permission restrictions.

## Requirement-by-Requirement Audit

| Requirement from objective | Current evidence | Status | Notes |
| --- | --- | --- | --- |
| Judge whether current code and comparison experiments are enough for CCF-B | `104_ccfb_submission_risk_matrix.md`; `105_current_decision_and_launch_state.md`; `94_submission_gate_checklist.md` | Satisfied for current decision-making | Judgment is conservative: CCF-B candidate, not SOTA/broad robustness. |
| Base the judgment on actual code and experiments, not vague opinion | `90_method_code_consistency.md`; `97_experiment_evidence_inventory.md`; `logs/paper_results_summary.md`; `docs/paper-drafts/tools/verify_result_tables.py` | Satisfied | 31 paper-facing result rows pass JSON artifact consistency check. |
| Identify experiments still needed | `104_ccfb_submission_risk_matrix.md`; `103_recent_method_scan_and_experiment_queue.md`; `105_current_decision_and_launch_state.md` | Satisfied | Next experiment is MTHv2 length-balanced sampling; HDRC no-localization and weaker expected-count are lower priority. |
| Identify modules/architectures worth changing | `103_recent_method_scan_and_experiment_queue.md`; `104_ccfb_submission_risk_matrix.md`; `105_current_decision_and_launch_state.md` | Satisfied | Keep SAQT query-to-CTC, charset adaptation, query budget; avoid generic backbone swaps, SQR/refiner, DCTC-lite, blank cap, LGQ first setting. |
| Turn DTLR into our own paper-facing model | `03_method.md`; `90_method_code_consistency.md`; `102_ccfb_evidence_and_model_roadmap.md`; LaTeX `sections/03_method.tex` | Mostly satisfied | SAQT story is code-backed: localization-supervised queries, vertical sorting, CTC conversion, charset adaptation, full recognition training, optional expected-count. |
| Write the paper draft | `docs/paper-drafts/*.md`; `docs/paper-drafts/latex/main.tex`; `latex/sections/*.tex`; Overleaf zip | Mostly satisfied | Chinese draft and English LNCS skeleton exist; final prose/format QA remains. |
| Use GPU0 only if experiments are needed | `105_current_decision_and_launch_state.md`; launch history in roadmap docs | Satisfied so far | GPU checks and attempted tmux launch were GPU0-oriented. No GPU1 experiment was launched in this phase. |
| Do not run long training outside tmux | `105_current_decision_and_launch_state.md` | Satisfied | Length-balanced probe was not launched because tmux is blocked; no foreground/nohup workaround used. |

## Evidence Already Strong Enough for the Paper

| Claim | Evidence | Paper handling |
| --- | --- | --- |
| SAQT is competitive under the current protocol | MTHv2 qbudget-count001 calibrated AR/CR `96.75/97.00`; HDRC qbudget-localization-query calibrated AR/CR `93.44/94.36`; adapted STR baselines in `logs/paper_results_summary.md` | Main result, no SOTA wording. |
| Character-localization learning is practically needed by this query-to-CTC path | MTHv2 no-localization calibrated AR/CR `0.11/0.16` | Lower-bound control only. |
| Query activation budget helps | MTHv2 single-factor `96.10/96.37 -> 96.69/96.90`; HDRC qbudget-localization-query variant `93.44/94.36` | MTHv2 ablation plus HDRC variant-level evidence. |
| Charset-aware classifier adaptation helps target charset mismatch | HDRC random-head `82.72/83.97` vs charset-aware `90.70/91.80` | Strong HDRC module evidence. |
| Full recognition training is needed after classifier-head reconstruction | MTHv2 `93.83/95.03 -> 96.69/96.90`; HDRC `85.97/89.72 -> 90.70/91.80` | Pipeline evidence on two datasets. |
| Expected-count is useful only as a scoped optional term | MTHv2 `96.69/96.90 -> 96.75/97.00`; HDRC count branch failed | Optional MTHv2-positive auxiliary only. |

## Current Static QA

| Check | Command / evidence | Result |
| --- | --- | --- |
| Result table vs JSON artifacts | `/home/ubuntu/miniconda3/envs/DTLR/bin/python docs/paper-drafts/tools/verify_result_tables.py` | `checked_rows=31`, `warnings=0`, `failures=0` |
| LaTeX citations vs BibTeX | Static grep/sort comparison recorded in `94_submission_gate_checklist.md` | 19 cite keys, 19 bib keys, no missing or unused entries |
| BibTeX synchronization | `cmp` between `references_seed.bib`, `references.bib`, and `latex/references.bib` | synchronized after DOI update |
| Figure synchronization | SHA-256 for Figure 1 and Figure 2 PDFs | source PDFs match LaTeX PDFs |
| Overleaf zip synchronization | SHA-256 for inner and outer zip | hashes match |
| LaTeX package static QA | `/home/ubuntu/miniconda3/envs/DTLR/bin/python docs/paper-drafts/tools/verify_latex_package.py` | citation, BibTeX, graphics, figure-hash, zip-hash, and placeholder checks pass with `failures=0` |

2026-06-08 update: after a prose/protocol wording pass that downgraded blank/nonblank calibration from model contribution wording to fixed development-set decoding-protocol wording, both static checks were re-run. `verify_result_tables.py` reports `checked_rows=31`, `warnings=0`, `failures=0`; `verify_latex_package.py` reports `warnings=0`, `failures=0`, with synchronized Overleaf zip hash `54c534e0e856f3c7f4312eaf92c1f5c148b656a62363a9d2eb8768fdd28ec479`.

## Open Debts

1. Local LaTeX compilation is not verified because `pdflatex` and `bibtex` are not installed in the current environment.
2. Final reference verification is improved but not fully closed; several entries are standard conference/arXiv entries without DOI/page fields by nature or by current source availability.
3. Figure sizing and typography must still be checked in the final LNCS layout.
4. The MTHv2 length-balanced sampling probe is technically ready but not run because `tmux` is blocked by the execution environment.
5. The final paper should still avoid strong words such as SOTA, robust, universal, significant, or broad generalization.

## Next Concrete Actions

1. Compile `docs/paper-drafts/latex/main.tex` in Overleaf or a TeX environment with Springer LNCS support.
2. If tmux becomes available, launch only the MTHv2 length-balanced sampling probe on GPU0:

```bash
tmux new-session -d -s dtlr_mthv2_length_balance_v2_16000_0608 'cd /home/ubuntu/DTLR && logs/mthv2_length_balance_v2_resume_1000_0608/run_length_balance_probe_0608.sh'
```

3. If the probe finishes, use the standard postprocess path before adding any result to the paper.
4. If the probe cannot run, proceed with the current conservative SAQT story and focus on formatting, references, and final prose.

## Completion Decision

Do not mark the active goal complete yet. The core technical judgment and paper
story are in place, but final compile QA and optional experiment execution
remain unverified or externally blocked.
