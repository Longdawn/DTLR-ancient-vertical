# DTLR Change Log

中文说明：
这份文档用于梳理原始 DTLR 的代码逻辑，以及当前针对横竖统一识别所做的增量修改。
目标是把“原本有什么、现在加了什么、为什么这么加”记录清楚，方便后续继续改模型、写论文和做实验复现。

## 1. Original Project Logic

中文说明：
原始 DTLR 不是传统的直接序列识别模型，而是“先检测字符 query，再按顺序转成序列做 CTC”。
也就是说，它的本质是 detection-based recognition。

DTLR is a detection-based text line recognition framework built on top of DINO / Deformable DETR.

The original pipeline is:

1. Build a DINO-style detector with a CNN backbone and deformable transformer.
2. Predict per-query character class logits and per-query boxes.
3. During pretraining, optimize the detector with detection losses.
4. During finetuning, convert the ordered query predictions into a sequence and optimize with CTC loss.

In other words, recognition is implemented as:

- `pred_logits`: per-query character scores
- `pred_boxes`: per-query boxes
- sort queries by geometry
- convert sorted logits to a CTC-compatible sequence
- compute `CTCLoss`

The core entrypoint is [finetuning.py](/home/ubuntu/DTLR/finetuning.py).

中文说明：
`finetuning.py` 是当前最核心的训练入口，真实数据的微调几乎都从这里进。


## 2. Original Main Modules

中文说明：
这一节记录原项目本来有哪些主要模块，方便和新增模块做对照。

### 2.1 Training / Entrypoints

中文说明：
训练相关脚本的职责分工如下。

- [finetuning.py](/home/ubuntu/DTLR/finetuning.py)
  - parses config and CLI args
  - builds model / dataset / optimizer
  - loads checkpoints
  - runs line-level CTC finetuning

- [engine.py](/home/ubuntu/DTLR/engine.py)
  - `train_one_epoch()`: detection-style training loop
  - `train_one_epoch_CTC()`: line-recognition finetuning loop
  - `evaluate_CTC()`: evaluation loop for CTC-based finetuning
  - `compute_wer()`: converts predictions to sequence-level metrics

- [evaluation.py](/home/ubuntu/DTLR/evaluation.py)
  - standalone evaluation script used in the original repo

### 2.2 Model

中文说明：
模型主体都在 `models/dino/dino.py`，其中既包含 DINO 主体，也包含 CTC 相关的 loss 逻辑。

- [models/dino/dino.py](/home/ubuntu/DTLR/models/dino/dino.py)
  - `DINO`: backbone + transformer + classification / box prediction heads
  - `SetCriterion`: computes detection losses and CTC loss
  - `build_dino()`: assembles model, criterion, postprocessor

### 2.3 Dataset

中文说明：
`MTH1000.py` 是我们后续古籍 line-level 微调最重要的数据入口。

- [datasets/MTH1000.py](/home/ubuntu/DTLR/datasets/MTH1000.py)
  - line-level dataset for `mth1000_dtlr`
  - provides image + text labels + dummy boxes for CTC finetuning


## 3. Original Losses

中文说明：
原始项目里，检测损失和识别损失是分层组织的。检测阶段主要是 DINO 的标准损失，微调阶段核心是 `loss_CTC`。

### 3.1 Detection Losses

中文说明：
下面这些是原始 DINO / DETR 风格损失。

In the original DINO path, the main losses are:

- `loss_ce`
- `loss_bbox`
- `loss_giou`
- `cardinality_error`

Optional / auxiliary losses:

- `loss_mask`
- `loss_dice`
- auxiliary decoder losses: `*_0`, `*_1`, ...
- intermediate encoder loss: `*_interm`
- DN losses: `loss_ce_dn`, `loss_bbox_dn`, `loss_giou_dn`, etc.

### 3.2 Recognition Loss

中文说明：
真实数据微调时，识别主损失是 `loss_CTC`。

For line-level finetuning, the original recognition-specific loss is:

- `loss_CTC`

Original CTC sequence construction:

- take `pred_logits`
- sort by `pred_boxes[..., 0]` (horizontal x-axis order)
- normalize to add blank probability
- interleave blank tokens
- compute `nn.CTCLoss`


## 4. Original Recognition Assumptions

中文说明：
原项目默认更偏横排文本，至少在 query 排序逻辑上如此；没有显式方向分类头。

Before the new changes, the code implicitly assumed:

- reading order is horizontal
- query sorting is based on x-coordinate
- no explicit orientation prediction head exists
- no orientation loss exists
- no distinction between oracle direction and predicted direction during evaluation


## 5. New Changes Added

中文说明：
这一节开始记录我们这次新增的内容，也就是“横竖统一入口 + 方向感知分流”的最轻量版本。

The current modifications introduce a reusable bidirectional recognition layer on top of the original DTLR line-recognition flow.

### 5.1 New Config Options

中文说明：
这些配置项是为了把方向相关能力做成开关，而不是把逻辑写死。

Added to CTC-related configs:

- `use_direction_head`
- `direction_loss_coef`
- `decode_by_pred_direction`
- `direction_source`

Files updated:

- [config/HWDB_full.py](/home/ubuntu/DTLR/config/HWDB_full.py)
- [config/Chinese.py](/home/ubuntu/DTLR/config/Chinese.py)
- [config/Chinese_w_masking.py](/home/ubuntu/DTLR/config/Chinese_w_masking.py)
- [config/Latin_CTC.py](/home/ubuntu/DTLR/config/Latin_CTC.py)

These options are also defaulted in [finetuning.py](/home/ubuntu/DTLR/finetuning.py).

中文说明：
这样即使旧命令不显式传参，代码也不会直接报错，默认行为会尽量兼容旧逻辑。


## 6. New Modules / Behaviors

中文说明：
这里记录新增的模块和新增的运行行为。

### 6.0 Vertical-First Training Controls (new)

中文说明：
为了先把竖排能力跑稳，数据集入口新增了“强制方向”和“按方向筛样本”两个开关。
这两个开关都做成可配置项，不会破坏原来的横排/混合训练流程。

Files:

- [datasets/MTH1000.py](/home/ubuntu/DTLR/datasets/MTH1000.py)
- [config/HWDB_full.py](/home/ubuntu/DTLR/config/HWDB_full.py)

Added options:

- `forced_direction`: `auto|vertical|horizontal`
  - `auto` 使用样本标签或回退规则
  - `vertical/horizontal` 直接强制整批样本按指定方向训练/解码
- `mth1000_filter_direction`: `all|vertical|horizontal`
  - 可在 dataset 初始化时按方向过滤样本
  - 适合“先只训竖排”的阶段

Also added:

- [config/MTH1000_vertical.py](/home/ubuntu/DTLR/config/MTH1000_vertical.py)
  - 竖排优先实验专用配置
  - 固定 `forced_direction="vertical"`
  - 关闭方向头和方向损失，先把竖排识别主任务收敛

### 6.1 Dataset-Level Direction Field

中文说明：
方向首先被提升为数据层字段，而不是只在模型里临时猜。

File:

- [datasets/MTH1000.py](/home/ubuntu/DTLR/datasets/MTH1000.py)

Added:

- explicit `direction` field in each sample
- `_normalize_direction()` helper
- fallback behavior when direction label is missing

Current behavior:

- prefer explicit sample-level direction if present
- support string / int / bool direction values
- fall back to geometry heuristic if needed

This change makes direction a first-class part of the sample format.

中文说明：
也就是说，`direction` 现在和 `labels`、`boxes` 一样，是正式输入的一部分。

### 6.2 Direction Head

中文说明：
这是这次新增的最核心模块之一。它负责预测整张 line image 的方向，而不是预测每个字符的方向。

File:

- [models/dino/dino.py](/home/ubuntu/DTLR/models/dino/dino.py)

Added to `DINO`:

- `use_direction_head`
- `direction_embed = nn.Linear(hidden_dim, 2)`
- `pred_direction` in model outputs

Current implementation:

- direction is predicted from the mean pooled last decoder state: `hs[-1].mean(dim=1)`
- output shape is batch-level binary orientation logits

This is a lightweight orientation classifier, not a second recognition branch.

中文说明：
当前实现还是轻量版，不是双识别头，也不是双 backbone。

### 6.3 Direction Loss

中文说明：
方向头新增以后，需要一个监督信号，所以增加了 `loss_direction`。

File:

- [models/dino/dino.py](/home/ubuntu/DTLR/models/dino/dino.py)

Added to `SetCriterion`:

- `_extract_direction_target()`
- `loss_direction()`

New loss:

- `loss_direction`

New metric:

- `direction_acc`

Current implementation:

- supervised binary cross-entropy via `F.cross_entropy`
- computed only when `pred_direction` exists and targets include `direction`

### 6.4 Bidirectional Query Sorting

中文说明：
这是“分流识别”真正落地的地方。原本只按 x 排，现在根据方向决定按 x 还是按 y 排。

Files:

- [models/dino/dino.py](/home/ubuntu/DTLR/models/dino/dino.py)
- [engine.py](/home/ubuntu/DTLR/engine.py)
- [evaluation.py](/home/ubuntu/DTLR/evaluation.py)

Original sorting:

- always sort by x-axis

Current sorting:

- horizontal: sort by `pred_boxes[..., 0]`
- vertical: sort by `pred_boxes[..., 1]`

This change has been made in:

- CTC loss path
- training metric path
- evaluation metric path
- standalone evaluation script


## 7. New Reusable Helpers

中文说明：
为了让方向逻辑可复用，没有把判断横竖的代码散落在每个函数里，而是抽成了 helper。

### 7.1 Engine Helpers

中文说明：
这些 helper 主要服务训练和验证循环。

File:

- [engine.py](/home/ubuntu/DTLR/engine.py)

Added helpers:

- `_direction_to_label()`
- `_get_target_direction()`
- `_get_decode_directions()`
- `_sort_pred_logits_by_direction()`
- `_compute_direction_accuracy()`

Purpose:

- centralize orientation decoding logic
- avoid scattering horizontal/vertical logic across multiple loops
- make training/eval behavior easier to reuse

### 7.2 Evaluation Helpers

中文说明：
这些 helper 主要服务独立评测脚本 `evaluation.py`。

File:

- [evaluation.py](/home/ubuntu/DTLR/evaluation.py)

Added helpers:

- `_get_text_direction()`
- `_sort_boxes_by_direction()`
- `_labels_to_text()`

Purpose:

- support orientation-aware standalone evaluation
- make integer / unicode charset conversion safer
- support charsets without explicit space token


## 8. New Evaluation Outputs

中文说明：
这次最重要的评测增量之一，就是把“理想方向条件下的性能”和“真实预测方向条件下的性能”分开报告。

The updated line-recognition evaluation now supports two decoding modes:

- `oracle_direction`
  - use target direction for sorting
  - estimates recognition upper bound

- `pred_direction`
  - use model-predicted direction for sorting
  - estimates real end-to-end usability

New tracked metrics:

- `wer_oracle_direction`
- `cer_oracle_direction`
- `wer_pred_direction`
- `cer_pred_direction`
- `direction_acc`


## 9. New Loss / Module Summary

中文说明：
这一节给出最简洁的总表，方便快速查对。

### Original Losses

- `loss_ce`
- `loss_bbox`
- `loss_giou`
- `cardinality_error`
- optional `loss_mask`
- optional `loss_dice`
- optional DN / aux / interm variants
- `loss_CTC`

### Newly Added Losses

- `loss_direction`

### Original Modules

- backbone
- deformable transformer
- class heads
- bbox heads
- postprocessor
- CTC conversion inside criterion

### Newly Added Modules

- batch-level direction head
- direction target extraction
- bidirectional sorting helpers
- oracle/predicted direction evaluation path


## 10. Important Implementation Notes

中文说明：
这里记录几个关键实现边界，避免后面继续改的时候把逻辑混掉。

### 10.1 What Did Not Change

中文说明：
这部分很重要，用来明确当前版本还没有做成什么程度。

The current design deliberately does not add:

- a second recognition head
- a second backbone branch
- a separate vertical decoder
- a page-level order head

So this is still a lightweight modification of the original DTLR line-recognition pipeline.

### 10.2 Weight Dict Fix

中文说明：
这里记录了一个真实修过的 bug：`loss_CTC` 不能混进 DETR 中间层权重构造。

`loss_CTC` and `loss_direction` are now appended after DETR aux / interm weight construction in [models/dino/dino.py](/home/ubuntu/DTLR/models/dino/dino.py).

Reason:

- these losses are recognition-specific
- they must not be mixed into the intermediate detection-only loss expansion

### 10.3 Checkpoint Compatibility

中文说明：
这是为了兼容旧 checkpoint 和新模块结构，避免一改头部就完全加载失败。

[finetuning.py](/home/ubuntu/DTLR/finetuning.py) now contains `_load_compatible_state()`.

Purpose:

- skip incompatible parameters safely
- allow loading pretrained / finetuned checkpoints even when classification head size changes
- reduce failure risk when adding the new direction head


## 11. Current Design Interpretation

中文说明：
当前版本最准确的说法是“方向感知的 line-level DTLR 扩展”，不是完全双分支架构。

The codebase is now best described as:

- shared DTLR detector / recognizer backbone
- shared character recognition head
- lightweight orientation classifier
- direction-aware sequence ordering
- evaluation under both oracle and predicted direction

This means the current implementation is a clean, reusable "orientation-aware line recognition" extension of DTLR, not yet a fully separated dual-branch architecture.


## 12. Recommended Next Step

中文说明：
下一步还是应该先在 `mth1000_dtlr` 上跑通 line-level 微调，再决定要不要继续加更重的模块。

Before adding more modules, the next step should be:

- run line-level finetuning on `data/mth1000_dtlr`
- verify `loss_CTC`, `loss_direction`, `direction_acc`
- compare `oracle_direction` vs `pred_direction`

Only after that should the code be extended toward:

- dual recognition heads
- page-level detection + reading order
- larger paper-specific architectural changes
