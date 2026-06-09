# ICDAR / CCF-B Style Brief

## Sources Checked

2026-06-05 重新核对以下来源；官方页面用于投稿要求，Springer proceedings 只用于观察论文组织方式。

- ICDAR 2026 official call for papers: `https://icdar2026.org/index.php/call-for-paper/`
- ICDAR 2026 official paper submission instruction: `https://icdar2026.org/index.php/paper-submission-instruction/`
- ICDAR 2026 official FAQ: `https://icdar2026.org/index.php/paper-faq/`
- ICDAR 2026 official reviewing guidelines: `https://icdar2026.org/index.php/reviewing-guidelines/`
- ICDAR 2025 official submission page: `https://www.icdar2025.com/submission`
- ICDAR 2024 Springer proceedings, Part I: `https://link.springer.com/book/10.1007/978-3-031-70543-4`
- ICDAR 2024 Springer proceedings, Part V: `https://link.springer.com/book/10.1007/978-3-031-70549-6`
- ICDAR 2024 Springer proceedings, Part III: `https://link.springer.com/book/10.1007/978-3-031-70552-6`
- ICDAR 2023 Springer proceedings: `https://link.springer.com/book/10.1007/978-3-031-41676-7`

这些来源用于判断会议格式、论文结构和写作风格；录用论文只能作为风格参考，不能替代本文实验要求。

## Venue-Level Requirements

1. ICDAR 2026 conference paper 使用 Springer LNCS 模板，采用双盲审稿。
2. Regular paper 最多 17 页，包含图、表和参考文献；不符合页数、LNCS 格式或匿名要求会被 desk reject。
3. ICDAR 2026 FAQ 明确不接收 supplementary material，因此关键消融、数据集统计、主图和主要协议说明必须进入正文或正文可见表格，不能依赖附录补救。
4. Author response 只能纠正事实错误或补充 reviewer 要求的信息，不应作为新增算法、定理或实验的渠道；reviewing guidelines 也提醒审稿人不要把 rebuttal 当作作者承诺补实验的通道。因此结构学习、字符表适配等硬消融必须在投稿前完成。
5. 因此本文最终英文版应按 LNCS 组织：Abstract, Introduction, Related Work, Method, Experiments, Conclusion, References，并在 17 页内保留足够的实验与消融空间。
6. 当前中文草稿的章节结构基本匹配 LNCS 论文，但参考文献、图注、公式编号和图表版式仍需转为最终模板格式。

## Writing Pattern Observed in ICDAR Papers

ICDAR 文档分析/识别论文的常见写法不是单纯介绍模型，而是围绕可复核任务协议展开：

1. 摘要一般包含任务场景、具体困难、方法关键机制、实验范围和核心结果。
2. Introduction 通常先说明文档任务价值，再缩小到明确问题设定，随后指出现有方法在该设定下的不足。
3. Method 需要把模块写成可审查的机制链：输入/输出、监督信号、训练目标、推理过程。
4. Experiments 通常要给出数据集规模、划分、评价指标、基线协议和消融；方法论文尤其依赖消融来证明每个贡献。
5. 结果分析应避免泛泛说“效果好”，而要说明在什么协议、什么对比范围下更好，以及哪些结论仍未被充分分离。
6. ICDAR 2024 proceedings 显示正会论文竞争具有选择性，144 篇 full papers 从 263 篇投稿中录用；这类论文通常把数据集规模、baseline protocol、核心消融和失败边界放在正文中，而不是只给主表。
7. ICDAR 2024 Part V 中的识别类论文题目和目录结构也说明，CTC-based Transformer、implicit character-aided learning 等方法贡献通常需要在正文实验中回答“相对于直接序列训练/无辅助信息是否有效”。这与 SAQT 的 Gate C 结构学习消融和 Gate D 字符表适配消融是同一类审稿问题。

## SAQT-Specific Writing Checklist

后续每章修订应按以下检查项执行，而不是继续做表层润色：

1. Abstract 必须同时回答四件事：古籍竖排单列识别为什么难，SAQT 的核心机制是什么，字符框在训练和推理中的角色有什么不同，实验在哪些数据集和指标下验证。
2. Introduction 的故事线应保持为“古籍数字化价值 -> 单列识别任务 -> 无分割识别的不足 -> 字符结构监督的训练期使用 -> 字符表适配”。不要把问题扩展到版面分析或阅读顺序预测。
3. Related Work 应按 work cluster 组织：场景文本识别、查询/检测式识别、中文历史文档识别、CTC 与指标。每个 cluster 要写清楚它能解决什么，以及本文为什么还需要结构感知查询。
4. Method 每个模块都要写清楚输入、监督、训练目标和推理时是否存在。特别是字符框监督和字符表适配都不能被写成测试阶段额外输入。
5. Experiments 的表述要优先服务可复核性：数据集规模、字符表、baseline 适配、模型选择、AR/CR 公式、校准协议必须清楚；代码路径、日志路径和过细的数据转换细节应留在 evidence/audit 文件中。
6. Results 只能围绕 AR/CR 主指标展开。当前正文不报告 CER、空预测率、预测/真实长度比或长度分桶，因此这些诊断指标不应进入摘要、引言贡献或结果分析正文。
7. Claim 强度必须和证据一致。主结果可以写“高于本文比较的竖排适配基线”；结构学习、字符表适配和 query budget 的独立效果只有在对应消融完成后才能写成强贡献。

## Implications for SAQT

当前 SAQT 草稿的故事方向是合适的：古籍竖排单列识别不同于常规场景文本识别，SAQT 将字符框监督用作结构学习信号，而不是推理阶段的检测输出。这个叙事能与 ICDAR 文档识别方向对齐。

以 ICDAR/CCF-B 正会标准看，当前版本仍缺少一项关键“贡献拆解”：

1. 若贡献一是结构感知查询学习，就需要无结构学习 / 仅 CTC 训练的对照。
2. 字符表感知分类器适配已在 HDRC 上补充随机目标分类头对照；该结论应保持为目标域证据。
3. 若 query activation budget 是方法组件，就需要至少说明它目前只在 MTHv2 上完成消融，或继续补 HDRC。
4. 若 blank/nonblank 校准被写入摘要或贡献，应保持轻量推理校准的定位，不能包装成主要方法贡献。
5. 如果 Gate C 的 no-structure CTC 从零训练结果很弱，应在正文中称为 lower-bound no-structure control，而不是把全部差距解释为字符框监督的纯粹因果收益。

## Revision Targets

为使本文更接近 ICDAR/CCF-B 投稿版本，下一轮应按以下顺序推进：

1. 先补结构学习实验债务，再强化结论措辞；由于无 supplementary，Gate C 不能留到附录。
2. 将所有强 claim 降级到当前证据能支撑的范围，例如“在当前比较范围内优于”而不是“SOTA”。
3. 在实验设置中保留数据集规模、划分、字符表大小和基线适配协议，避免过多数据加工细节。
4. 结果分析围绕 AR/CR 主指标展开，不引入论文正文不打算报告的诊断指标。
5. 生成可核验 BibTeX，并建立 citation-to-claim 对应关系。
