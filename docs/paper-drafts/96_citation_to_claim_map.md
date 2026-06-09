# Citation-to-Claim Map

本文档记录当前中文草稿中引用与正文 claim 的对应关系。状态说明：

- `mapped`: 引用已在正文中承担明确论证功能，但 BibTeX 元数据仍需逐条核验。
- `needs_metadata_verification`: 需要用一级来源核验作者、题名、venue、年份、DOI/arXiv。
- `needs_claim_verification`: 需要进一步确认原文是否准确支撑当前 claim。

## Current Inline Citations

| Citation marker in draft | Draft location | Claim supported | Status | Next action |
| --- | --- | --- | --- | --- |
| Shi et al., 2017 | `01_introduction.md`; `02_related_work.md` | CRNN 将卷积特征、序列建模和 CTC 结合为端到端文本识别器，是无分割序列识别的重要基线。 | mapped; seed_bibtex_added | `references_seed.bib` 已加入，最终提交前仍需按 LNCS 样式复核。 |
| Shi et al., 2016 | `01_introduction.md`; `02_related_work.md` | RARE 类方法通过空间变换/校正处理不规则场景文本。 | mapped; seed_bibtex_added; metadata_verified | 已补 IEEE/CVPR DOI `10.1109/CVPR.2016.452`，页码 4168--4176。 |
| Shi et al., 2018 | `02_related_work.md` | ASTER 类方法通过图像校正改善不规则文本识别。 | mapped; seed_bibtex_added | `references_seed.bib` 已加入；正文年份应与最终引用键统一。 |
| Baek et al., 2019 | `01_introduction.md`; `02_related_work.md` | 场景文本识别可被拆解为 transformation、feature extraction、sequence modeling、prediction 等模块；训练和测试协议影响公平比较。 | mapped; seed_bibtex_added; metadata_verified | 已补 ICCV DOI `10.1109/ICCV.2019.00481`；页码按 CVF open-access 条目保留 4715--4723。 |
| Fang et al., 2021 | `01_introduction.md`; `02_related_work.md` | ABINet 使用视觉与语言建模提升场景文本识别。 | mapped; seed_bibtex_added | `references_seed.bib` 已加入。 |
| Bautista and Atienza, 2022 | `01_introduction.md`; `02_related_work.md` | PARSeq 将文本识别建模为 permutation/autoregressive sequence 相关框架，代表 Transformer/语言建模方向。 | mapped; seed_bibtex_added; metadata_verified | 已核验 Springer ECCV 2022 DOI、页码 178--196；正文已避免把 PARSeq 写成外部语言模型。 |
| Du et al., 2022 | `01_introduction.md`; `02_related_work.md` | SVTR 从视觉建模角度混合局部与全局特征，是当前场景文本识别强基线之一。 | mapped; seed_bibtex_added | `references_seed.bib` 已加入。 |
| Carion et al., 2020 | `02_related_work.md` | DETR 将目标检测表述为基于 object queries 的集合预测。 | mapped; seed_bibtex_added; metadata_verified | 已补 Springer ECCV DOI `10.1007/978-3-030-58452-8_13`，页码 213--229。 |
| Zhang et al., 2022/2023 | `02_related_work.md` | DINO/DINO-style detection transformer 改进 DETR 式查询检测。 | mapped; seed_bibtex_added | 已核对为 DINO: DETR with Improved DeNoising Anchor Boxes，ICLR 2023；正文引用年份应统一为 Zhang et al., 2023。 |
| Baena et al., 2024 | `02_related_work.md` | Detection-based text line recognition 将字符实例预测用于文本行识别，启发本文查询式结构监督。 | mapped; seed_bibtex_added | 已核对为 General Detection-based Text Line Recognition / DTLR，arXiv:2409.17095。 |
| Diao et al., 2023 | `02_related_work.md` | 中文识别研究中有利用汉字结构、部件或偏旁信息缓解大字符表和低频字问题的工作。 | mapped; seed_bibtex_added | 已核对为 IJCAI 2023 RZCR。 |
| Zeng et al., 2022 | `02_related_work.md` | 中文字符识别可利用笔画、偏旁或结构分解信息。 | mapped; seed_bibtex_added | 已核对为 STAR arXiv:2210.08490。 |
| Graves et al., 2006 | `02_related_work.md` | CTC 通过边缘化所有可折叠为目标序列的路径训练无对齐序列模型。 | mapped; seed_bibtex_added | `references_seed.bib` 已加入。 |
| Lombardi and Marinai, 2020 | `01_introduction.md`; `02_related_work.md` | 历史文档分析与识别是文档图像分析的重要方向，退化、载体、数据集和任务设置会影响识别系统。 | mapped; seed_bibtex_added | 已核对 Journal of Imaging / DOI，需最终 LNCS 样式复核。 |
| Antonacopoulos et al., 2013 | `01_introduction.md`; `02_related_work.md` | 历史书籍识别是 ICDAR 长期关注的评测任务，真实馆藏中的字体、退化和版式差异会影响 OCR 系统。 | mapped; seed_bibtex_added | 已核对 ICDAR 2013 / DOI，最终提交前按 LNCS 样式复核页码和会议名。 |
| Tang et al., 2020 | `01_introduction.md`; `02_related_work.md` | 中文历史文档 digitization 中字符分割/字符定位与识别相关，MTHv2 包含大量中文历史文档字符实例。 | mapped; seed_bibtex_added; metadata_verified | 已核验 IEEE BigData 2020 DOI 与页码 1924--1930。 |
| Wu et al., 2020 | `01_introduction.md`; `02_related_work.md` | 中文历史文档中字符级检测/定位是重要问题，支持本文将字符位置作为训练期结构监督的背景动机。 | mapped; seed_bibtex_added | 已核对 Pattern Recognition / DOI，最终提交前按 LNCS 样式复核。 |
| Saini et al., 2019 | `04_experimental_setup.md` | HDRC 来源于 ICDAR 2019 Historical Document Reading Challenge on Large Structured Chinese Family Records。 | mapped; seed_bibtex_added | 已核对 ICDAR 2019 / DOI / 页码，最终提交前按 LNCS 样式复核。 |
| Ma et al., 2024 | `01_introduction.md`; `02_related_work.md` | 中文历史文档存在独特版式和阅读模式，影响 OCR 系统；本文仅用该引用支撑领域困难，不将任务扩展为阅读顺序预测。 | mapped; seed_bibtex_added | 已核对 AAAI proceedings 页面。 |

## Claim Coverage Gaps

| Draft claim area | Current status | Needed evidence |
| --- | --- | --- |
| 古籍/历史文档数字化的重要性 | Mostly covered | 已补 Lombardi and Marinai 2020、Antonacopoulos et al. 2013、Tang et al. 2020、Ma et al. 2024；投稿前仍可视篇幅补 digital humanities 引用，但已不再是硬缺口。 |
| 竖排古籍相较场景文本的困难 | Mostly covered | 已补中文历史文档字符分割、字符检测和阅读组织相关引用，包括 Tang et al. 2020、Wu et al. 2020、Ma et al. 2024。 |
| HDRC 数据集或 PAGE-XML 来源 | Covered in draft; needs final style check | 已在 `04_experimental_setup.md` 补入 Saini et al., 2019；最终英文稿需确认数据集名称、challenge 名称和引用格式一致。 |
| AR/CR 指标定义 | Under-cited or protocol-defined | 若 AR/CR 来自 OCR/HTR 传统评测，应补引用；若是本文统一协议，应在实验设置中明确公式即可。 |
| DTLR/Detection-based TLR 与 SAQT 的关系 | Needs verification | 需要准确引用 DTLR 原论文，并避免把本文写成页面级检测或完整 detection-recognition pipeline。 |

## Minimum Reference Tasks Before Submission

1. 将正文作者-年份引用改成目标模板要求的数字引用，或在中文草稿中保留作者-年份、英文定稿再统一替换。
2. 将 `references_seed.bib` 中的 seed 条目逐条按 LNCS/BibTeX 样式复核，包括页码、DOI、会议/期刊全称和年份。
3. 对 `needs_claim_verification` 条目阅读全文或至少核验摘要和方法部分，确保 claim 不错引。
4. 若最终 Introduction 继续强调“保护性数字化”的人文价值，可再补 1 篇 digital humanities 引用；当前 OCR/历史文档技术动机已具备基本引用支撑。
5. `references.bib` 已由 seed BibTeX 生成；最终提交前仍需逐条核验 LNCS 样式，并确保参考文献只包含正文实际引用条目。
