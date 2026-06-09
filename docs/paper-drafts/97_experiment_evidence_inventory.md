# Experiment Evidence Inventory

本文档用于记录当前论文草稿中可进入正文的实验证据、证据来源和仍缺失的消融。除非另有说明，正文主表只采用 AR/CR，不使用 CER、空预测率、长度分桶等诊断指标。

## Evidence Policy

- `preexisting_artifact`: 仓库中已有日志、checkpoint 或结果文件，可作为当前草稿的结果来源，但投稿前最好用最终评估脚本复核一次。
- `newly_run`: 当前会话重新运行并产生的结果。
- `user_claim`: 用户口头说明或未落盘信息，不能直接写入论文正文。

## Main Results

| Claim | Evidence type | Source artifact | Draft location | Status |
| --- | --- | --- | --- | --- |
| SAQT 在 MTHv2 test 上取得 clean AR/CR 96.33/96.50，开发集固定校准 AR/CR 96.75/97.00 | newly_run + preexisting_artifact | `logs/paper_results_summary.md`; `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_clean_0608.json`; `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/decode_bias_sweep_valid_0608.json`; `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/micro_test_bias_b-20_nb08_0608.json` | `05_results_analysis.md` Table 1 | usable as current MTHv2 main result |
| SAQT 在 HDRC test 上取得 clean AR/CR 91.50/91.64，开发集固定校准 AR/CR 93.44/94.36 | newly_run | `logs/paper_results_summary.md`; `logs/hdrc_qbudget_full_0607/micro_valid_clean_0607.json`; `logs/hdrc_qbudget_full_0607/micro_test_clean_0607.json`; `logs/hdrc_qbudget_full_0607/decode_bias_sweep_valid_0607.json`; `logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json` | `05_results_analysis.md` Table 1 and qbudget-localization-query variant table | usable as current HDRC main result; must be described as qbudget-localization-query variant evidence |
| HDRC 字符表适配消融：随机目标分类头 test clean AR/CR 81.01/81.41，bias AR/CR 82.72/83.97；字符表感知初始化对应 89.99/90.33 和 90.70/91.80 | newly_run + preexisting_artifact | `logs/hdrc_charset_random_full_visible1_0605/micro_test_clean_0605.json`; `logs/hdrc_charset_random_full_visible1_0605/decode_bias_sweep_valid_0605.json`; `logs/hdrc_charset_random_full_visible1_0605/micro_test_bias_b-12_nb10_0605.json`; smart reference in `logs/mth1000mth1200pre_hdrcft_full_0527-1732/*` | `05_results_analysis.md` charset-adaptation table | usable as HDRC-only ablation |
| MTHv2 上 query activation budget 优于不使用该约束 | preexisting_artifact | `logs/paper_results_summary.md`; `logs/mthv2_mth1000mth1200tkh_full_0528-0957/*`; `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/*` | `05_results_analysis.md` Table 3 | usable as MTHv2-only ablation |
| MTHv2 expected-count 辅助项带来小幅收益：clean AR/CR 96.17/96.29 -> 96.33/96.50，校准 AR/CR 96.69/96.90 -> 96.75/97.00 | newly_run + preexisting_artifact | `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/*`; `logs/mthv2_qbudgetstage1pre_mthv2_full_ctc_count001_0608/*`; `logs/paper_results_summary.md` | `05_results_analysis.md` expected-count table | usable as MTHv2-positive optional auxiliary ablation; not cross-dataset core evidence |
| MTHv2 无字符定位学习 CTC 对照发生 blank-collapse：test clean AR/CR 0.00/0.00，开发集校准 AR/CR 0.11/0.16 | newly_run | `logs/mthv2_no_structure_ctc_full_0605/micro_test_clean_0606.json`; `logs/mthv2_no_structure_ctc_full_0605/decode_bias_sweep_valid_0606.json`; `logs/mthv2_no_structure_ctc_full_0605/micro_test_bias_b-20_nb04_0606.json` | `05_results_analysis.md` character-localization-learning table | usable as conservative MTHv2 lower-bound control |
| HDRC classification-head reconstruction vs full-model recognition training：head-reconstruction test bias AR/CR 85.97/89.72，full-recognition test bias AR/CR 90.70/91.80 | newly_run + preexisting_artifact | `logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_clean_0607.json`; `logs/mth1000mth1200pre_hdrcft_head_0527-1530/decode_bias_sweep_valid_0607.json`; `logs/mth1000mth1200pre_hdrcft_head_0527-1530/micro_test_bias_b-20_nb04_0607.json`; full reference in `logs/mth1000mth1200pre_hdrcft_full_0527-1732/*` | `05_results_analysis.md` head/full table | usable as HDRC-only recognition-stage ablation |
| MTHv2 classification-head reconstruction vs full-model recognition training：head-reconstruction test clean AR/CR 93.00/93.42，bias AR/CR 93.83/95.03；full-recognition test bias AR/CR 96.69/96.90 | newly_run + preexisting_artifact | `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_valid_clean_0607.json`; `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/decode_bias_sweep_valid_0607.json`; `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_clean_0607.json`; `logs/mthv2_qbudgetstage1pre_mthv2_head_0603/micro_test_bias_bm08_nb10_0607.json`; full reference in `logs/mthv2_qbudgetstage1pre_mthv2_full_0603/*` | `05_results_analysis.md` head/full table | usable as MTHv2 recognition-stage ablation |
| HDRC qbudget-localization-query 变体：test clean AR/CR 91.50/91.64，开发集校准 bias AR/CR 93.44/94.36 | newly_run | `logs/hdrc_qbudget_full_0607/micro_valid_clean_0607.json`; `logs/hdrc_qbudget_full_0607/micro_test_clean_0607.json`; `logs/hdrc_qbudget_full_0607/decode_bias_sweep_valid_0607.json`; `logs/hdrc_qbudget_full_0607/micro_test_bias_bm20_nb10_0607.json` | `05_results_analysis.md` HDRC qbudget-localization-query variant table | usable as variant-level HDRC evidence; not a pure query-budget ablation |
| 与 CRNN、SVTR、ABINet、SAR 等竖排适配场景文本识别基线比较 | preexisting_artifact | `logs/paper_results_summary.md` | `05_results_analysis.md` Table 2 | usable, but baseline protocol should remain explicit |

## Dataset Evidence

| Dataset | Evidence type | Source artifact | Paper-facing facts |
| --- | --- | --- | --- |
| MTHv2 | preexisting_artifact | `logs/paper_results_summary.md` | 由三个子集组成，合计 105,579 张古籍竖排单列图像；字符表大小 6,727 |
| HDRC | preexisting_artifact | `logs/paper_results_summary.md`; `data/hdrc_dtlr` conversion artifacts if needed | train/valid/test 为 24,285/2,854/3,381；字符表大小 4,017；按页面组划分 |

## Evidence Not Yet Paper-Ready

| Candidate evidence | Available artifact | Reason not paper-ready |
| --- | --- | --- |
| HDRC qbudget-localization-query full 结果 | completed postprocess | Moved to usable evidence above. The full run was early-stopped after epoch 2/3 validation regression; the epoch-1 best checkpoint was evaluated with clean valid/test, development-set bias sweep, and fixed-bias test. |
| LGQ query-to-CTC adapter smoke | `logs/mthv2_lgq_adapter_smoke_0607/log.txt`; `logs/mthv2_lgq_adapter_smoke_0607/checkpoint_best_regular.pth` | Internal negative result. The smoke run completes without fatal errors, but validation CER is `14.8588%` with blank ratio `0.989749`, worse than the MTHv2 qbudget head-only starting point at about `8.56%` validation CER. Do not use in paper body. |

## Protocol Risks

1. 当前主结果主要来自已有日志文件，投稿前应固定最终评估脚本并重跑一次测试集评估，确保表格数字可从命令直接复现。
2. blank/nonblank bias 由开发集校准协议确定后固定用于测试，这是合理的校准协议，但正文必须明确它不使用测试集、不引入语言模型或外部语料。
3. 字符定位学习、字符表适配、分类头重建/全模型识别训练和 query budget 是方法贡献的一部分，其中字符表适配和识别训练阶段消融已在 HDRC 上闭合，query budget 已有 MTHv2 单因素消融；HDRC qbudget-localization-query 变体已完成最终 AR/CR 后处理，可作为变体级目标域证据，但不能写成 query budget 的纯因果消融。字符定位学习核心消融已在 MTHv2 上完成 clean 和开发集校准测试；字符定位学习结果应按 lower-bound control 保守解释。
4. 当前所有结果为单次运行，无随机种子方差；因此正文不应使用“稳定”“显著”“泛化性强”等需要多次运行或统计检验支撑的表述。

## Minimum Additional Experiments for ICDAR/CCF-B

1. 最优先的可选实验是 MTHv2 length-balanced sampling probe。它已完成 smoke 验证，但真实 tmux 训练启动被执行环境阻止；未产生 validation CER 前不得写入论文结果。
2. 若需要进一步加强字符定位学习证据，可在 HDRC 上重复 no-localization control，但这不是当前最小投稿门槛。
3. 若需要让 expected-count 更安全，可只测试一个更弱系数（例如 `0.003`）而不是展开大规模 sweep；保留条件是 MTHv2 不失去收益且 HDRC 不再出现 count collapse。
