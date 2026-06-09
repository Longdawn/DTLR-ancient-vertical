# ICDAR / CCF-B Readiness Audit

## Verdict

当前草稿已经具备一篇文档识别方向会议论文的基本叙事：问题设定清楚，方法主线明确，MTHv2 和 HDRC 上有主结果，并且与多种经竖排输入适配的场景文本识别方法进行了统一 AR/CR 比较。结果部分已改为“直接解码结果 + 开发集固定校准补充”的写法，并把主结果段中对各训练模块独立贡献的暗示降级为整体框架比较，降低了审稿人将主要收益归因于未分离模块的风险。当前 paper-facing 主结果为 MTHv2 qbudget-count001 的 `96.75/97.00` AR/CR，以及 HDRC qbudget-localization-query 的 `93.44/94.36` AR/CR。2026-06-05 已完成 HDRC 随机分类头对照：random-head calibrated test AR/CR 为 `82.72/83.97`，charset-aware calibrated test AR/CR 为 `90.70/91.80`。2026-06-06 已完成 MTHv2 无字符定位学习 CTC 对照：clean test AR/CR 为 `0.00/0.00`，开发集校准 test AR/CR 为 `0.11/0.16`。2026-06-07 已完成 MTHv2 和 HDRC 的 classification-head reconstruction vs full-model recognition training：MTHv2 head-reconstruction/full-recognition calibrated test AR/CR 为 `93.83/95.03` vs `96.69/96.90`，HDRC 为 `85.97/89.72` vs `90.70/91.80`。该 head/full 对照使用旧 qbudget 和 HDRC mainline 分支，是受控识别阶段证据，不应与当前主结果分支混淆。同日完成 HDRC qbudget-localization-query 变体后处理：clean test AR/CR 为 `91.50/91.64`，开发集校准 test AR/CR 为 `93.44/94.36`。LGQ query-to-CTC adapter smoke 已完成但为内部负结果：`logs/mthv2_lgq_adapter_smoke_0607` 的验证 CER 为 `14.8588%`，弱于 MTHv2 qbudget head-only 起点，因此不进入正文。当前版本已从“内部初稿”推进到“具备 CCF-B 投稿潜力的论文草稿”，但直接投稿仍有风险：query budget 的单因素消融主要在 MTHv2 上闭合，HDRC 结果应按 qbudget-localization-query 变体解释；expected-count 只在 MTHv2 上形成正向证据；参考文献和图表仍需投稿级审校。

## 已闭合证据

1. 主任务定义已收敛到古籍竖排单列识别，不涉及页面级版面分析、阅读顺序预测或整页检测。
2. 主实验包含 MTHv2 和 HDRC 两个数据集，正文只报告 AR 和 CR。
3. 与 CRNN、SVTR、ABINet、SAR 等经竖排输入适配的场景文本识别方法进行了统一比较。
4. 已补充 query activation budget 在 MTHv2 上的消融结果。
5. 已补充 blank/nonblank CTC 校准的结果分析，并明确其不是语言模型或核心训练机制。
6. 相关工作中的主要占位引用已替换为作者-年份引用，并已新增 `96_citation_to_claim_map.md` 记录引用与正文 claim 的对应关系；`references_seed.bib` 已包含当前正文主要引用的 BibTeX seed，`references.bib` 已生成。HDRC 数据集引用、历史书籍识别引用和中文历史文档字符检测引用均已补入正文，但最终 LNCS 样式和元数据复核尚未完成。
7. Figure 1 的框架图设计稿和 SVG 初版已给出，可用于后续视觉审校和 LaTeX 整合。
8. Figure 2 的主结果对比图已根据现有 AR/CR 数据生成，源数据、绘图脚本和 SVG 均已保存；本轮已将其从非零基线柱图改为点图，降低高分区间比较的视觉夸张风险。
9. 已新增 `97_experiment_evidence_inventory.md`，将正文结果与已有日志文件对应起来，并标记哪些结果仍不能进入投稿正文。
10. 已新增 `98_icdar_style_brief.md`，记录 ICDAR 投稿格式和录用论文写作风格对本文的直接约束。
11. 已新增 `94_submission_gate_checklist.md`，将投稿前证据闭环拆为任务范围、主结果、字符定位学习消融、字符表适配消融、query budget、两阶段训练、引用和图表八个 gate。
12. 已新增 `93_cross_section_consistency_review.md`，确认新增历史文档引用没有改变本文的单列识别任务边界，并记录后续英文稿需要遵守的范围约束。
13. 已新增 `90_method_code_consistency.md`，核对 Method 中的查询排序、CTC 转换和字符表适配描述与 `models/dino/dino.py`、`finetuning.py`、`engine.py` 的实现一致。
14. 已新增 `92_structure_learning_ablation_plan.md`，给出 Gate C 字符定位学习消融的最小可执行方案和 postprocess 要求。
15. 已新增 `91_hdrc_charset_adaptation_postprocess_plan.md`，给出 Gate D 随机分类头 full-model recognition training 完成后的 clean/test/sweep/bias 后处理命令和文件判定标准。
16. 已新增 `latex/` 英文 LNCS 草稿骨架，包含 `main.tex`、分章节 `sections/*.tex`、本地 `references.bib` 和 `figures/*.pdf`。该目录可作为 Overleaf 项目根目录上传，并已打包为 `saqt_lncs_overleaf_draft.zip`。
17. 已完成 MTHv2 no-localization lower-bound control：clean test AR/CR `0.00/0.00`，开发集校准 test AR/CR `0.11/0.16`。该结果已写入中英文实验章节。
18. 已完成 HDRC classification-head reconstruction vs full-model recognition training：head-reconstruction bias test AR/CR `85.97/89.72`，full-recognition bias test AR/CR `90.70/91.80`。该结果已写入中英文实验章节。
19. 已完成 MTHv2 classification-head reconstruction vs full-model recognition training：head-reconstruction bias test AR/CR `93.83/95.03`，full-recognition bias test AR/CR `96.69/96.90`。该结果已写入中英文实验章节，使识别训练阶段消融不再只依赖 HDRC。

## 仍未闭合的硬债务

### 1. 字符定位学习消融已闭合，但解释必须保守

当前 MTHv2 no-localization control 已回答以下问题：

- 无字符定位学习，仅使用行级 CTC 训练时，MTHv2 的 AR/CR 是多少？
- 使用字符定位监督后，在相同训练协议下达到怎样的识别表现？

`logs/mthv2_no_structure_ctc_full_0605` 是无字符定位学习、仅行级 CTC 的 conservative lower-bound control。其 clean test AR/CR 为 `0.00/0.00`，开发集校准 test AR/CR 为 `0.11/0.16`。这说明在当前训练预算和同一 architecture family 下，缺少字符定位学习时 query-to-CTC 表示无法形成可用识别序列。正文应将其表述为“当前预算下的无定位学习下界对照”，而不是将全部差距解释为字符框监督的纯粹因果收益。若时间允许，在 HDRC 上重复该对照会进一步增强跨数据集说服力，但不再是最小投稿门槛。

### 2. 字符表适配消融已闭合于 HDRC

已补充目标字符表变化时的对比：

- 随机初始化目标分类头。
- 共享字符继承 + 新字符初始化。

HDRC random-head full-model recognition training 已完成，路径为 `logs/hdrc_charset_random_full_visible1_0605`。开发集校准 `blank=-1.2, nonblank=1.0` 后，random-head test AR/CR 为 `82.72/83.97`；对应 smart charset-aware full-model recognition training 在同一 HDRC test 上为 `90.70/91.80`。该结果支持字符表感知初始化在 HDRC 目标字符表变化场景中的作用。正文仍应将其表述为目标域证据，而非跨数据集充分验证。

### 3. 两数据集上的模块一致性不足

当前 query budget 的单因素消融仍只在 MTHv2 上闭合。`logs/hdrc_qbudget_full_0607` 已完成 epoch-1 best checkpoint 的 forced postprocess：clean test AR/CR 为 `91.50/91.64`，开发集校准 test AR/CR 为 `93.44/94.36`，优于 HDRC 主线的 `89.99/90.33` 和 `90.70/91.80`。该实验使用 qbudget-localization 查询表示适配 HDRC；由于它同时包含额外定位监督查询学习差异，正文应称为 qbudget-localization-query variant，而不是纯粹的 query-budget 单因子因果消融。相比之下，classification-head reconstruction vs full-model recognition training 已在 MTHv2 和 HDRC 上闭合，可作为识别训练阶段的双数据集证据。

### 4. 图表仍需投稿前审校

当前已有两张图的初版：

- Figure 1: SAQT overview，文件为 `figures/figure1_saqt_overview.svg`。
- Figure 2: main comparison，文件为 `figures/figure2_main_results.svg`。

这两张图已经可以支撑当前草稿阅读，图表 QA 记录见 `95_figure_audit.md`。本轮已为两张图生成 PDF 版本，并复制到 `latex/figures/` 供 Overleaf 直接引用。投稿前仍需按目标模板统一字体、字号、线宽和双栏宽度，并确认英文版正文中的图注与图内标签一致。

### 5. 参考文献尚未形成投稿级 BibTeX

正文已有作者-年份引用，已建立初版 citation-to-claim map，并已生成 `references_seed.bib` 和 `references.bib`。本轮已补充 Antonacopoulos et al. 2013 与 Wu et al. 2020，用于加强历史书籍识别和中文历史文档字符定位背景。投稿前还需要：

- 每条引用按一级来源复核元数据、页码、DOI 和 venue 字段。
- 对 `needs_claim_verification` 条目阅读全文或核验方法/摘要，确认当前正文没有错引或过度引用。

### 6. ICDAR 写法已接近，但证据密度仍可增强

ICDAR 方法论文通常会将实验拆为主结果、基线比较和模块消融。当前 SAQT 草稿已有主结果、场景文本识别基线比较、MTHv2 query budget 消融、HDRC qbudget-localization-query 变体、MTHv2 no-localization lower-bound control、HDRC 字符表适配消融，以及 MTHv2/HDRC classification-head reconstruction vs full-model recognition training 消融。继续润色可以改善可读性，但若要提高正会把握，下一阶段应优先做投稿级引用、图表和 LaTeX 审校，而不是继续扩写叙事。

## 建议补跑实验优先级

1. 可选加强：HDRC no-localization control，或重新设计 MTHv2 上 activation-gated query-to-CTC adapter。当前第一版 LGQ smoke 为负结果，不建议直接 full run。
2. 投稿整理：最终 BibTeX 复核、图表字体/线宽/图注 QA、英文 LaTeX 编译检查。

## 当前投稿判断

- 直接投稿 ICDAR / CCF-B 正会：已有投稿潜力，但不建议按当前状态直接定稿提交。
- 当前最小证据链：主结果、竖排适配 STR 基线、MTHv2 query budget、MTHv2 no-localization lower-bound、HDRC charset adaptation、MTHv2/HDRC head-vs-full training-stage ablation 均已具备。
- HDRC qbudget-localization-query 结果已经可用，并补强了目标域结果；完成最终 BibTeX、英文版图注与模板排版后，可进入相对稳妥的投稿版本。正文仍需保守说明它是变体级证据，不是 query budget 的纯单因素消融。

最新 gate 判定见 `94_submission_gate_checklist.md`。当前主要风险不再是 Gate C 未闭合，而是模块证据跨数据集覆盖不足和投稿级工程整理尚未完成。
