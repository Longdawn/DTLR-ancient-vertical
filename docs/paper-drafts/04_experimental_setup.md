# 4. 实验设置

## 4.1 数据集

本文在 MTHv2 和 HDRC 两个古籍竖排单列识别数据集上评估 SAQT。所有实验均以裁剪后的行级或单列图像为输入，目标是直接预测对应字符序列。

MTHv2 由三个子集组成，合计提供 105,579 张古籍竖排单列图像 [Tang et al., 2020]。本文将三个子集统一为同一识别任务进行训练和评估；在字符定位信息学习阶段，额外利用可用的字符级位置标注，并将字符框按竖直方向排序后作为定位监督。

HDRC 来自 ICDAR 2019 Historical Document Reading Challenge on Large Structured Chinese Family Records [Saini et al., 2019]。该数据集提供 PAGE-XML 标注，本文依据其中的文本行区域和 Unicode 转录构建行级竖排识别样本。为减少同页样本同时出现在训练和测试中的风险，HDRC 按页面组划分；其页面数为 936/113/123，行样本数为 24,285/2,854/3,381。MTHv2 和 HDRC 的字符表大小分别为 6,727 和 4,017。

## 4.2 基线方法

本文比较 SAQT 与多种经竖排输入适配的场景文本识别方法，包括 MMOCR 中的 CRNN、SVTR、ABINet 和 SAR。对于默认处理横排文本的识别器，本文在输入端旋转竖排单列图像，使其文本方向与模型预期的读取方向一致。MTHv2 上的基线方法包括 CRNN、SVTR-tiny、SVTR-small、SVTR-L、ABINet 和 SAR；HDRC 上包括 CRNN、SVTR-tiny、SVTR-L、ABINet 和 SAR。所有 MMOCR 输出均转换到本文统一的 micro AR/CR 评估协议。

所有基线方法均使用各数据集导出的 MMOCR 字符表和训练、验证、测试标注，不使用额外语料。竖排图像统一采用 `Rot90(k=3)` 旋转。CRNN 使用高度 32、最大宽度 2048 的变宽输入；SVTR-tiny、SVTR-small 和 SVTR-L 使用对应 MMOCR 配置，其中 SVTR-L 采用官方 48x160 几何设置；ABINet 使用 32x128 输入；SAR 使用高度 48、宽度 768 的 padded 输入。训练轮数遵循各模型配置：CRNN 和 SVTR 系列训练 30 个 epoch，ABINet 和 SAR 训练 20 个 epoch，并根据验证集 `1-N.E.D` 保存模型权重。测试阶段仅将预测字符串转换到本文统一的 AR/CR 评估协议。

## 4.3 评价指标

本文报告 accuracy rate (AR) 和 correct rate (CR)。设 \(S\)、\(D\)、\(I\) 分别表示替换、删除和插入错误，\(N\) 表示真实字符数：

$$
AR=1-\frac{S+D+I}{N},\qquad
CR=1-\frac{S+D}{N}.
$$

## 4.4 实现细节

SAQT 采用 DINO-style detection transformer 作为结构查询骨架，ResNet-50 为视觉主干，Transformer encoder/decoder 均为 6 层，隐藏维度为 256，注意力头数为 8，查询数为 900。字符定位信息学习使用字符框监督和 DETR-style matching loss。MTHv2 的 query-budget 设置训练 6 个 epoch，学习率为 \(1\times10^{-4}\)，backbone 学习率为 \(1\times10^{-5}\)，batch size 为 2，weight decay 为 \(1\times10^{-4}\)。该训练使用竖排筛选和固定长边 resize 设置，并加入 query-budget 正则项，系数为 0.01。

下游识别阶段将查询输出按竖直位置组织为 CTC 序列。若目标数据集字符表与定位信息查询表示对应的参考字符表不同，分类器适配模块先重建分类头：共享字符继承对应分类权重，新增字符用未占用的分类行初始化。分类头重建阶段训练 3 个 epoch，学习率为 \(1\times10^{-4}\)；全模型识别训练阶段从分类头重建后的模型权重继续训练 12 个 epoch，学习率为 \(1\times10^{-5}\)。两个阶段均使用 AdamW，batch size 为 2，weight decay 为 \(1\times10^{-4}\)，随机种子为 42。模型权重依据开发集识别结果确定；blank/nonblank 偏置由开发集校准协议确定，并在测试阶段固定。测试集仅用于最终报告 AR/CR。该校准不引入语言模型或外部文本数据。实验在 NVIDIA RTX 3090 GPU 上完成。
