# CCF-B Gap and Model Modification Plan

Date: 2026-06-06
Last updated: 2026-06-07

## Current Verdict

当前版本已经具备 CCF-B 投稿潜力，但还不建议不加整理地直接定稿提交。SAQT 已经有主结果、竖排适配场景文本识别基线、MTHv2 query budget 消融、MTHv2 no-localization lower-bound control、HDRC 字符表适配消融，以及 HDRC head reconstruction vs full finetuning 消融。当前主要风险不再是核心证据链缺失，而是 query budget 的跨数据集覆盖不足，以及论文图表、引用和英文稿还需要投稿级审校。

2026-06-07 补充判断：论文叙事应继续使用“字符定位学习 / character-localization learning”，不要把核心贡献写成通用预训练。当前方法的独立性主要来自 query-to-CTC 识别桥接、query activation budget 和字符表感知分类器适配，而不是来自替换 backbone。

因此，当前最现实的目标不是再换一个大 backbone，而是在 DTLR 的 query-based 框架上形成一个更清晰的自有模型：

- 字符定位监督只作为训练信号，不作为推理输出。
- query-to-CTC 转换是识别核心，而不是沿用检测结果后处理。
- query activation budget 控制过量 nonblank query。
- charset-aware classifier adaptation 处理古籍数据集字符表变化。
- validation-fixed blank/nonblank calibration 只作为轻量推理补充。

## Evidence That Is Already Useful

### Main Results

- MTHv2-combo-qbudget:
  - clean AR/CR: `96.17/96.29`
  - validation-fixed bias AR/CR: `96.69/96.90`
  - artifact: `logs/mthv2_qbudgetstage1pre_mthv2_full_0603`
- HDRC:
  - clean AR/CR: `89.99/90.33`
  - validation-fixed bias AR/CR: `90.70/91.80`
  - artifact: `logs/mth1000mth1200pre_hdrcft_full_0527-1732`

### Baselines

MTHv2 and HDRC both include multiple vertical-input-adapted scene text recognizers:

- CRNN
- SVTR-tiny / SVTR-small / SVTR-L
- ABINet / ABINet-vision
- SAR
- MASTER
- RobustScanner
- PaddleOCR SVTRv2 on MTHv2

The strongest adapted MTHv2 baseline remains close to SAQT, so the paper should avoid SOTA-style language. The fair claim is: under the current unified AR/CR protocol, SAQT is higher than the included vertical-input-adapted recognition baselines.

### Closed Module Evidence

- Query activation budget:
  - MTHv2 only.
  - w/o qbudget bias AR/CR: `96.10/96.37`
  - w/ qbudget bias AR/CR: `96.69/96.90`
  - usable as an internal module ablation, not cross-dataset proof.
- Charset-aware classifier adaptation:
  - HDRC closed.
  - random-head bias AR/CR: `82.72/83.97`
  - charset-aware bias AR/CR: `90.70/91.80`
  - usable as target-charset mismatch evidence.
- Head reconstruction vs full finetuning:
  - HDRC closed.
  - head-only bias AR/CR: `85.97/89.72`
  - full-finetuning bias AR/CR: `90.70/91.80`
  - usable as target-domain adaptation evidence.
- MTHv2 head reconstruction vs full finetuning:
  - status: running postprocess as of 2026-06-07.
  - tmux session: `mthv2_headonly_eval_0607`
  - checkpoint: `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/checkpoint_best_regular.pth`
  - script: `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/run_headonly_eval_0607.sh`
  - purpose: add the same AR/CR protocol used by the final paper tables; do not cite until clean/sweep/fixed-bias JSON files exist.

## Closed Gate C Evidence

Run:

- `logs/mthv2_no_structure_ctc_full_0605`

Purpose:

- Same architecture family, no character-box localization learning, line-level CTC only.
- This is a conservative no-localization lower-bound control, not a perfect causal estimate of character boxes.

Current status:

- Training finished on 2026-06-05.
- Validation during training collapsed to near-all-blank after epoch 1.
- GPU0 postprocess started on 2026-06-06 in tmux session `mthv2_noloc_postprocess_0606`.
- Clean valid/test postprocess has completed:
  - valid artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_valid_clean_0606.json`
  - test artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0606.json`
  - clean valid AR/CR: `0.0057/0.0057`
  - clean test AR/CR: `0.0019/0.0019`
  - both splits have near-100% empty prediction rate.
- Validation decode-bias sweep completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0606.json`
  - selected bias: `blank=-2.0`, `nonblank=0.4`
  - valid AR/CR: `0.1369/0.3654`
- Fixed-bias test completed:
  - artifact: `logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_b-20_nb04_0606.json`
  - test AR/CR: `0.1141/0.1562`
  - empty prediction rate: `98.7757`

Interpretation:

- This supports the practical need for character-localization query learning under the current training budget.
- It should be written as a conservative lower-bound no-localization control.
- Do not claim the entire gap is the pure causal effect of character boxes.

## Modules Worth Keeping as Paper Contributions

### 1. Query-Based Character-Localization Learning

This is the core DTLR-derived part, but the paper should not present it as generic pretraining. The precise contribution is:

- character boxes supervise query localization during training;
- query geometry is reused only to sort the recognition sequence;
- inference still outputs text directly through CTC.

Required evidence:

- Gate C no-localization control on MTHv2.
- Optional stronger evidence: repeat no-localization control on HDRC.

### 2. Query Activation Budget

Code location:

- `models/dino/dino.py`
  - `compute_query_budget_loss`
  - `loss_labels`
  - `query_budget_loss_coef`

Why it is credible:

- It directly targets over-activated queries in fixed-query detection-style recognizers.
- Existing MTHv2 result improves both clean and calibrated AR/CR.

Risk:

- Only MTHv2 ablation is closed.
- HDRC qbudget ablation would make the module much stronger.

Minimum next experiment:

- HDRC w/o qbudget vs w/ qbudget, same charset-aware finetuning protocol.
- Detailed launch and interpretation plan:
  - `docs/paper-drafts/100_hdrc_qbudget_ablation_plan.md`
  - Important caveat: using `logs/mthv2_stage1_qbudget_from_mth1000mth1200_gpu0_0602/checkpoint.pth` introduces an additional MTHv2 character-localization learning stage, so the comparison must be described as a qbudget-localization-query variant unless a perfectly matched no-qbudget checkpoint is trained.

### 3. Charset-Aware Classifier Adaptation

Code location:

- `finetuning.py`
  - `--new_class_embedding`
  - `--smart_mapping`
  - `--path_old_charset`

Why it is credible:

- It handles a real ancient-text problem: datasets share many characters but differ in rare and collection-specific characters.
- HDRC random-head control is now closed and clearly weaker.

Risk:

- It is an initialization/adaptation strategy, not an inference module.
- Do not overstate as general transfer learning.

### 4. Validation-Fixed CTC Calibration

Code location:

- `util/ctc_decoding.py`
- `tools/sweep_ctc_decode_bias.py`

Why it is useful:

- It gives consistent gains in MTHv2 and HDRC.
- It is lightweight and does not use external text.

Risk:

- Reviewers may see it as decode-time tuning.
- Keep it as a supplementary inference protocol, not a main method contribution.

## Modules Not Worth Making Central

### SGQ Short Query CE

Code/config:

- `config/MTHV2_dtlr_sgq_short_ce.py`
- `models/dino/dino.py`
  - `compute_short_query_ce_loss`
  - `loss_short_gt_ce`

Evidence:

- `experiments/notes/mthv2_sgq_short_ce_summary_0529.md`

Result:

- Clean inference reduces short empty/deletion but worsens overall and short CER.
- Calibrated inference improves overall valid CER, but len=1/2 CER is still worse than calibrated baseline.

Decision:

- Do not use as a main module for the paper.
- It can remain as a negative/diagnostic experiment if needed.

### Glyph Prototype Fusion

Code hooks exist:

- `use_glyph_prototype_head`
- `glyph_proto_fuse_coef`

Current risk:

- Existing handoff notes record negative prototype fusion behavior.
- It adds complexity and may not align with current strongest failure mode.

Decision:

- Do not spend the next GPU slot on this unless a new, very specific prototype design is proposed.

### Count-Only / Presence Losses

Logs exist for several count/presence variants:

- `logs/mth1000_count_guided_0518-1920`
- `logs/mth1000_csaq_count_only_0525`
- `logs/mth1000_realmain_shortboost_presence_0524-*`

Risk:

- These were targeted at short-text empty prediction, but the current paper main metrics are AR/CR and the strongest mainline is already qbudget + calibration.

Decision:

- Do not make them central unless rerun under MTHv2/HDRC final protocol.

## Best Next Architecture-Level Modification

The most defensible “our own model” modification is not a new backbone. It is a cleaner query-to-CTC bridge:

### Proposed Module: Localization-Guided Query-to-CTC Adapter

Current behavior in `models/dino/dino.py::loss_CTC`:

1. Sort queries by predicted vertical box coordinate.
2. Apply sigmoid to class logits.
3. Build blank probability from residual probability mass.
4. Insert blank-only positions between query positions.
5. Train with CTC.

Possible modification:

- Add a learnable query activation head that predicts whether a sorted query should contribute nonblank evidence.
- Use activation logits to gate blank/nonblank logits during CTC conversion.
- Couple it with a query count/budget loss so expected active queries tracks transcription length without forcing exact alignment.

Code status:

- Basic hooks already exist in `models/dino/dino.py`:
  - `use_query_activation_head`
  - `apply_activation_gating`
  - `compute_query_count_loss`
  - `use_activation_gating`
- Existing CSAQ count-only evidence on MTH1000 was negative: count consistency alone did not produce usable CTC recognition. Therefore the next model change should not be presented as a count-loss contribution. If pursued, it should be redesigned as a query-to-CTC adapter and validated under the final MTHv2/HDRC protocol.
- Detailed design note:
  - `docs/paper-drafts/101_query_to_ctc_adapter_design.md`

Why this is better than changing backbone:

- It directly modifies the part that makes DTLR into a recognizer.
- It is specific to vertical single-column recognition.
- It can be ablated cleanly:
  - baseline SAQT
  - SAQT + activation-gated query-to-CTC adapter
  - optionally w/o qbudget

Minimum experiment:

- MTHv2 full finetune from the same qbudget head checkpoint.
- Enable:
  - `use_query_activation_head=True`
  - `use_activation_gating=True`
  - `query_count_loss_coef > 0`
  - conservative `activation_gate_blank_coef` / `activation_gate_nonblank_coef`
- Evaluate with the same clean/bias protocol.

Risk:

- This may hurt because activation logits are not directly supervised by character boxes during CTC finetuning unless carefully initialized.
- A one-epoch smoke plus validation sample check should precede full training.

## Experiment Priority

### Required Before Claiming A Strong CCF-B Submission

1. Add one more module-consistency experiment, preferably HDRC query budget ablation under the final AR/CR protocol.
2. Finish final citation verification, figure typography/layout checks, and Overleaf/LNCS compile QA.
3. Incorporate MTHv2 head-only AR/CR only if the running postprocess completes cleanly; otherwise keep the HDRC head/full result as the main training-stage evidence.

### Strongly Recommended

3. HDRC query budget ablation.
4. MTHv2 head-only vs full-finetuning AR/CR evaluation if cross-dataset training-stage consistency is needed.

### Optional Model Improvement

5. Activation-gated query-to-CTC adapter on MTHv2.
6. If useful on MTHv2, repeat on HDRC.

## Submission Judgment

Current state:

- Has CCF-B submission potential if claims are kept conservative.
- Not ideal for immediate final submission because query budget is not replicated on HDRC, and the paper still needs final citation/figure/template QA.

After Gate C + one additional module ablation:

- The paper can be positioned as a DTLR-derived but distinct SAQT model for vertical ancient-text recognition, with enough internal evidence for CCF-B consideration.
