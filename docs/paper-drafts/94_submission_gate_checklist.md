# Submission Gate Checklist for SAQT

本文档用于判断 SAQT 草稿是否达到 ICDAR / CCF-B 正会投稿前的最低证据闭环。结论以当前工作区文件和日志为准，不以叙事完整度替代实验证据。

## Gate A: 任务与范围

Status: pass.

- 论文聚焦古籍竖排单列/行级识别。
- 正文不讨论页面级版面分析、整页检测、文本列检测或阅读顺序预测。
- 推理输入为裁剪后的单列图像，输出为字符序列。

Authoritative evidence:

- `docs/paper-drafts/00_title_abstract.md`
- `docs/paper-drafts/01_introduction.md`
- `docs/paper-drafts/03_method.md`
- `docs/paper-drafts/93_cross_section_consistency_review.md`
- `docs/paper-drafts/90_method_code_consistency.md`

## Gate B: 主结果

Status: pass for current draft; needs final rerun before submission.

Current paper-facing results:

- MTHv2 qbudget-count001: AR/CR `96.75/97.00` with development-set calibrated bias. The original qbudget branch remains a controlled reference at `96.69/96.90`.
- HDRC qbudget-localization-query variant: AR/CR `93.44/94.36` with development-set calibrated bias. This is the current paper-facing HDRC main result, but it must be described as variant-level evidence rather than a pure query-budget ablation.
- Original HDRC charset-aware mainline: AR/CR `90.70/91.80` with validation-calibrated bias. This remains the controlled reference for charset adaptation and head/full training-stage comparisons.
- Baselines: adapted CRNN, SVTR, ABINet, SAR under unified AR/CR protocol.

Authoritative evidence:

- `logs/paper_results_summary.md`
- `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_bias_b-20_nb08_0608.json`
- `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/decode_bias_sweep_valid_0608.json`
- `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_bias_b-20_nb04_0527.json`
- `logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json`

Remaining action:

- Before final submission, rerun or at least reformat all final result JSONs using `docs/EXPERIMENT_POSTPROCESS.md` and `tools/format_ctc_result_row.py`.

## Gate C: Structure-Learning Ablation

Status: pass for MTHv2 lower-bound evidence.

The paper claims that character-box supervision provides useful localization-supervised query learning. A same-architecture no-localization CTC control has now produced clean and validation-protocol calibrated MTHv2 test results.

Minimum acceptable evidence:

- Dataset: at least MTHv2; preferably MTHv2 and HDRC.
- Compare:
  - SAQT with character-box structure learning.
  - matched CTC recognition training without character-box structure learning.
- Report test AR/CR under the same clean and validation-calibrated decoding protocol.

Current risk:

- The result is very weak and should be interpreted as a conservative lower-bound control, not as a pure causal estimate of the entire character-box supervision effect. For stronger cross-dataset evidence, repeat the control on HDRC or add another module-level ablation.

Prepared plan:

- `docs/paper-drafts/92_structure_learning_ablation_plan.md`

2026-06-05 02:30 status check:

- `logs/mthv2_no_structure_ctc_full_0605` has not been created yet.
- GPU0 is occupied by PID `1010003`; the queued no-structure run should not be relaunched unless the waiter is confirmed failed.

2026-06-05 02:36 status check:

- tmux session `mthv2_no_structure_ctc_wait_0605` exists.
- Waiter PID `1148725` is still waiting for CHDAC PID `1010003` to exit before launching `logs/mthv2_no_structure_ctc_full_0605`.
- No structure-learning ablation result is paper-ready yet.

2026-06-05 02:58 status check:

- CHDAC blocking process PID `1010003` has exited.
- `logs/mthv2_no_structure_ctc_full_0605` has been created and the no-structure CTC run has started on GPU0.
- Current process PID `1148725` is using GPU memory and writing training logs; the run is at epoch 0 and has not produced validation or test AR/CR.
- At this checkpoint, Gate C was not paper-ready until the run finished and clean/calibrated test AR/CR were generated under the planned postprocess protocol.

2026-06-05 03:08 status check:

- PID `1148725` is still running on GPU0.
- `logs/mthv2_no_structure_ctc_full_0605/info.txt` is still in epoch 0 training and no `checkpoint_best_regular.pth` or AR/CR JSON exists yet.
- Because this control intentionally starts without localization-supervised query learning, it should be interpreted as a lower-bound no-localization CTC control if the result is very weak.

2026-06-05 03:11 status check:

- PID `1148725` remains active and `info.txt` is still being updated.
- The run is at epoch 0 around step `2810/42088`; no validation row, checkpoint, or postprocess JSON exists yet.

2026-06-05 03:15 status check:

- PID `1148725` remains active on GPU0 and continues writing `logs/mthv2_no_structure_ctc_full_0605/info.txt`.
- The run is still in epoch 0 around step `3680/42088`; no `checkpoint_best_regular.pth`, validation row, or postprocess AR/CR JSON exists yet.
- At this checkpoint, Gate C was not paper-ready.

2026-06-05 03:23 status check:

- PID `1148725` remains active on GPU0.
- The run has reached epoch 0 validation and created `logs/mthv2_no_structure_ctc_full_0605/epoch_0`.
- This was only the first validation pass; no final checkpoint selection, clean/test JSON, validation bias sweep, or calibrated test AR/CR existed yet at this checkpoint.

2026-06-05 03:36 status check:

- PID `1148725` remains active on GPU0 and is training epoch 1.
- Epoch 0 validation completed and wrote `logs/mthv2_no_structure_ctc_full_0605/log.txt`.
- Epoch 0 validation is extremely weak: `cer_oracle_direction=83.197218`, `test_blank_pred_ratio_unscaled=0.0`, `test_loss=1515.7451`.
- `checkpoint_best_regular.pth` exists, but it is only the best checkpoint among completed early epochs and is not final paper evidence. No clean/test JSON, validation bias sweep, or calibrated test AR/CR exists yet.
- The observed epoch 0 behavior supports treating this run as a conservative no-structure lower-bound control unless later epochs recover substantially.

2026-06-05 09:45 status check:

- PID `1148725` remains active on GPU0 and is training epoch 11 in `logs/mthv2_no_structure_ctc_full_0605`.
- Completed validation rows through epoch 10 remain blank-collapse dominated: epoch 1--9 show `test_blank_pred_ratio_unscaled=1.0`, and epoch 10 remains near all-blank with `test_blank_pred_ratio_unscaled=0.9999994925602013`.
- At this checkpoint, the run had not produced final clean/test JSON, validation bias sweep, or calibrated test AR/CR.

2026-06-06 clean-postprocess status check:

- Training completed and clean postprocess finished for `logs/mthv2_no_structure_ctc_full_0605/checkpoint_best_regular.pth`.
- Clean valid artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_valid_clean_0606.json`, AR/CR `0.0057/0.0057`.
- Clean test artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0606.json`, AR/CR `0.0019/0.0019`.
- At this checkpoint, validation decode-bias sweep had started on GPU0 and was writing `logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0606.out`; the sweep completed in the final status check below.
- Interpretation should remain conservative: under the current training budget and same architecture family, the no-localization CTC control collapses to near-empty prediction, supporting the practical need for localization-supervised query learning, but not a pure causal estimate of the full gap.

2026-06-06 final postprocess status check:

- Validation decode-bias sweep completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0606.json`
  - selected bias: `blank=-2.0`, `nonblank=0.4`
  - valid AR/CR: `0.14/0.37`
- Fixed-bias test completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_b-20_nb04_0606.json`
  - test AR/CR: `0.11/0.16`
  - empty prediction rate: `98.78`
- Gate C is now usable for the paper as a MTHv2 no-localization lower-bound control.

## Gate D: Charset-Adaptation Ablation

Status: pass for HDRC.

Purpose:

- Test whether character-table-aware classifier initialization is better than random target classifier initialization when adapting the model to HDRC.

Smart-mapping reference:

- Head: `logs/mth1000mth1200pre_hdrcft_head_0527-1530`
- Full: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`
- Test bias result: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_test_bias_b-20_nb04_0527.json`

Random-head control:

- Head reconstruction: `logs/hdrc_charset_random_head_visible1_0605`
- Full-model recognition: `logs/hdrc_charset_random_full_visible1_0605`
- Final random-head clean test AR/CR: `81.01/81.41`
- Final random-head validation-protocol bias test AR/CR: `82.72/83.97`
- Smart charset-aware reference clean test AR/CR: `89.99/90.33`
- Smart charset-aware reference validation-protocol bias test AR/CR: `90.70/91.80`

Completion requirements:

1. `logs/hdrc_charset_random_head_visible1_0605/checkpoint_best_regular.pth` exists. **Done.**
2. Launch matched full-model recognition training without `--smart_mapping`. **Done.**
3. Produce clean valid/test JSON. **Done.**
4. Run validation decode-bias sweep. **Done.**
5. Apply selected bias to test. **Done.**
6. Add AR/CR comparison table to `05_results_analysis.md` only after test results exist. **Done.**

Final artifacts:

- `logs/hdrc_charset_random_full_visible1_0605/micro_valid_clean_0605.json`
- `logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.json`
- `logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.json`
- `logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_b-12_nb10_0605.json`

Interpretation:

- This closes the HDRC charset-adaptation evidence gate.
- The claim should remain scoped to HDRC / target-charset mismatch, not generalized to all datasets.

Matched full-model recognition command template:

```bash
tmux new-session -d -s hdrc_charset_random_full_visible1_0605 'cd /home/ubuntu/DTLR && CUDA_VISIBLE_DEVICES=1 MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python finetuning.py --device cuda:0 --dataset_file mth1000 --num_workers 0 --resume logs/hdrc_charset_random_head_visible1_0605/checkpoint_best_regular.pth --new_class_embedding --resume_finetuning --path_old_charset data/tkhmth2200_mth1000_mth1200_charset.pkl --save_log --output_dir logs/hdrc_charset_random_full_visible1_0605 -c config/MTH1000_dtlr.py --options mth1000_root=hdrc_dtlr mth1000_raw_root=HDRC mth1000_image_ext=jpg num_classes=6700 batch_size=2 lr=1e-5 epochs=12 eval_epoch=1 max_iterations=10000'
```

Postprocess plan:

- `docs/paper-drafts/91_hdrc_charset_adaptation_postprocess_plan.md`

## Gate E: Query Activation Budget Ablation

Status: pass with scoped interpretation.

Completed:

- MTHv2 w/o query budget vs w/ query budget is available in `logs/paper_results_summary.md`.
- HDRC qbudget-localization-query variant completed final AR/CR postprocess:
  - clean test AR/CR: `91.50/91.64`
  - development-set calibrated test AR/CR: `93.44/94.36`
  - selected bias: `blank=-2.0`, `nonblank=1.0`

HDRC follow-up history:

- HDRC qbudget-localization-query head reconstruction finished in `logs/hdrc_qbudget_head_0607` with best clean valid CER `19.34`, better than the HDRC head-reconstruction clean valid CER `20.56`.
- HDRC qbudget-localization-query full-model recognition training ran in `logs/hdrc_qbudget_full_0607` on GPU0; epoch 1 clean valid CER is `9.60`, better than the existing HDRC main clean valid CER `13.44`.
- 2026-06-07 04:12 status check: `log.txt` still contains only epoch 0 and epoch 1 validation records; `info.txt` is updating in epoch 2 around step `4720/12142`; GPU0 remains highly occupied. Final AR/CR postprocess must wait.
- 2026-06-07 04:17 status check: epoch 2 valid CER is `15.42`, marked not best; epoch 1 remains best at `9.60`. Training has continued into epoch 3. Final AR/CR postprocess must still wait.
- 2026-06-07 04:36 status check: `info.txt` is still updating in epoch 3 around step `4170/12142`; GPU0 remains occupied by this run. No `micro_valid_clean_0607.json`, `micro_test_clean_0607.json`, `decode_bias_sweep_valid_0607.json`, or fixed-bias test JSON exists yet. The run is not ready for paper evidence or postprocess.
- 2026-06-07 04:38 status check: epoch 3 is still training around step `4630/12142`; `log.txt` still has validation rows only through epoch 2. GPU0 remains occupied and no final AR/CR JSON exists.
- 2026-06-07 05:04 status check: run was early-stopped after epoch 2/3 validation regression; forced postprocess completed on the epoch-1 best checkpoint. Final artifacts exist:
  - `logs/hdrc_qbudget_full_0607/micro_valid_clean_0607.json`
  - `logs/hdrc_qbudget_full_0607/micro_test_clean_0607.json`
  - `logs/hdrc_qbudget_full_0607/decode_bias_sweep_valid_0607.json`
  - `logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json`
- Because the candidate checkpoint also includes extra MTHv2 localization-supervised query learning, it should not be reported as a pure query-budget-only causal ablation.

Paper handling:

- Current draft may present query budget as an MTHv2-supported single-factor module result.
- HDRC result may be presented as a qbudget-localization-query variant under the same downstream protocol.

## Gate F: Head Reconstruction vs Full-Model Recognition

Status: pass for MTHv2 and HDRC.

Current evidence:

- HDRC head-reconstruction checkpoint has been evaluated under the same clean/bias AR/CR protocol and compared with the full-model recognition checkpoint.
- MTHv2 head-reconstruction checkpoint has also been evaluated under the same clean/bias AR/CR protocol and compared with the full-model recognition checkpoint.

Completed MTHv2 evidence:

- Head-only clean test AR/CR: `93.00/93.42`
- Head-reconstruction validation-protocol bias test AR/CR: `93.83/95.03`
- Full-model recognition clean test AR/CR: `96.17/96.29`
- Full-model recognition validation-protocol bias test AR/CR: `96.69/96.90`
- Artifacts:
  - `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_clean_0607.json`
  - `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/decode_bias_sweep_valid_0607.json`
  - `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_bias_bm08_nb10_0607.json`

Completed HDRC evidence:

- Head-only clean test AR/CR: `82.28/82.68`
- Head-reconstruction validation-protocol bias test AR/CR: `85.97/89.72`
- Full-model recognition clean test AR/CR: `89.99/90.33`
- Full-model recognition validation-protocol bias test AR/CR: `90.70/91.80`
- Artifacts:
  - `logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_clean_0607.json`
  - `logs/mth1000mth1200pre_hdrcft_head_0527-1530/decode_bias_sweep_valid_0607.json`
  - `logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_bias_b-20_nb04_0607.json`

Paper handling:

- This supports keeping full-model recognition training in the SAQT pipeline.
- The claim can now say this trend is observed on both evaluated datasets, while still avoiding broad claims about all ancient-text datasets.

## Gate G: References

Status: partial pass.

Completed:

- `96_citation_to_claim_map.md` maps current inline citations to claims.
- `references_seed.bib` contains BibTeX seed entries for the main current citations.
- `references.bib` has been generated from the seed BibTeX for LaTeX integration.
- Introduction now includes historical document / Chinese historical document citations for domain motivation.
- Added historical book recognition and Chinese historical character detection references: Antonacopoulos et al. 2013 and Wu et al. 2020.
- Experimental setup now cites HDRC via ICDAR 2019 Historical Document Reading Challenge.
- 2026-06-05 citation-key check: LaTeX contains 19 cite keys, all 19 are present in `latex/references.bib`, and no unused BibTeX entries remain.
- PARSeq and HRCenterNet BibTeX metadata have been updated with verified DOI/page fields.
- 2026-06-08 citation metadata pass: RARE, Baek et al. ICCV 2019, and DETR entries were updated with verified DOI fields in `references_seed.bib`, `references.bib`, and `latex/references.bib`.

Remaining:

- Verify every entry against primary sources.
- Optionally add one digital-humanities reference if the final Introduction keeps a broad cultural-preservation motivation.
- Convert inline citations to the final venue format.

## Gate H: Figures

Status: partial pass.

Completed:

- `figures/figure1_saqt_overview.svg`
- `figures/figure1_saqt_overview.pdf`
- `figures/figure2_main_results.svg`
- `figures/figure2_main_results.pdf`
- `95_figure_audit.md` records figure QA status and remaining publication-layout checks.
- Figure 2 has been revised from non-zero-baseline bars to a point comparison plot to avoid visually exaggerating high-score differences.

Remaining:

- Final typography, line width, and sizing against LNCS layout.
- English figure labels and captions for final submission.

## Gate I: LNCS / Overleaf Draft

Status: partial pass; Overleaf package synchronized with current main results.

Completed:

- `latex/main.tex`
- `latex/sections/*.tex`
- `latex/references.bib`
- `latex/figures/*.pdf`
- `saqt_lncs_overleaf_draft.zip`
- PDF figure exports are copied into the LaTeX draft directory and referenced with project-root-relative paths.
- The LaTeX draft now includes the completed MTHv2 no-localization lower-bound table.
- 2026-06-08 sync check:
  - `latex/sections/00_abstract.tex` and `latex/sections/05_results.tex` use the current paper-facing MTHv2 qbudget-count001 result `96.75/97.00` and HDRC qbudget-localization-query result `93.44/94.36`.
  - `latex/figures/figure1_saqt_overview.pdf` matches `figures/figure1_saqt_overview.pdf` by SHA-256.
  - `latex/figures/figure2_main_results.pdf` matches `figures/figure2_main_results.pdf` by SHA-256.
  - `latex/saqt_lncs_overleaf_draft.zip` and `saqt_lncs_overleaf_draft.zip` match by SHA-256 and contain the refreshed Figure 1 and Figure 2 PDFs.
  - LaTeX citation-key static check found 19 cite keys, all present in `latex/references.bib`, with no unused BibTeX entries.
  - LaTeX static reference check found no missing graphics, no missing table/figure refs, and no unreferenced table/figure labels.
- 2026-06-08 result-table static check:
  - Script: `docs/paper-drafts/tools/verify_result_tables.py`
  - Command: `/home/ubuntu/miniconda3/envs/DTLR/bin/python docs/paper-drafts/tools/verify_result_tables.py`
  - Result: `checked_rows=31`, `warnings=0`, `failures=0`.
  - Scope: main results, adapted STR baselines, query budget, expected-count, HDRC qbudget-localization-query, no-localization, charset adaptation, and head/full training-stage rows.
- 2026-06-08 LaTeX package static check:
  - Script: `docs/paper-drafts/tools/verify_latex_package.py`
  - Command: `/home/ubuntu/miniconda3/envs/DTLR/bin/python docs/paper-drafts/tools/verify_latex_package.py`
  - Result: `cite_keys=19`, `bib_keys=19`, `missing_cites=0`, `unused_bib=0`, `graphics_refs=2`, `missing_graphics=0`, `unresolved_placeholders=0`, `failures=0`.
  - Scope: citation closure, BibTeX synchronization, figure references, Figure 1/2 PDF hashes, inner/outer Overleaf zip hash, and unresolved placeholder scan.
- 2026-06-08 prose/protocol wording pass:
  - Updated the abstract, introduction, results, and conclusion in both the Chinese draft and LNCS draft to keep blank/nonblank calibration framed as a fixed development-set decoding protocol rather than a core model contribution.
  - Refreshed `latex/saqt_lncs_overleaf_draft.zip` after the text edits and copied it to the parent `saqt_lncs_overleaf_draft.zip`.
  - Re-ran `verify_result_tables.py`: `checked_rows=31`, `warnings=0`, `failures=0`.
  - Re-ran `verify_latex_package.py`: `cite_keys=19`, `bib_keys=19`, `missing_cites=0`, `unused_bib=0`, `graphics_refs=2`, `missing_graphics=0`, `unresolved_placeholders=0`, `warnings=0`, `failures=0`, `zip_sha256=54c534e0e856f3c7f4312eaf92c1f5c148b656a62363a9d2eb8768fdd28ec479`.

Remaining:

- Local compilation has not been verified because `pdflatex` is not installed in the current environment; `which pdflatex` returned no executable.
- Final submission still requires Springer `llncs.cls`, final BibTeX verification, and optional additional module-consistency evidence.

## Current Submission Verdict

Has ICDAR / CCF-B submission potential, but not ready for final direct submission without additional QA.

Minimum path to "basically submittable":

1. Keep Gate C claims conservative and framed as a MTHv2 lower-bound control.
2. Keep HDRC qbudget-localization-query framed as variant-level evidence, not a pure query-budget ablation.
3. Finalize references and, if space permits, add one digital-humanities citation for the cultural-preservation motivation.
4. Verify figure sizing, LaTeX compilation, and final result table consistency.

The HDRC qbudget-localization-query result makes the submission substantially safer. Remaining risk is now mainly presentation/protocol QA rather than missing core module evidence.
