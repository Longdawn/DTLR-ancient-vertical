# Recent Method Scan and Experiment Queue

Date: 2026-06-08

This note translates recent OCR/STR/HTR method trends into concrete actions for
the current DTLR ancient vertical text repository. It is intentionally
experiment-facing: a module is useful only if it can be isolated, tested against
existing baselines, and explained as part of SAQT rather than as a generic
backbone swap.

## Source Signals

| Source | Relevant idea | Fit to SAQT |
| --- | --- | --- |
| General Detection-based Text Line Recognition, NeurIPS 2024 (`https://proceedings.neurips.cc/paper_files/paper/2024/file/4acb23d5d9b4bea566799afac0ee3125-Paper-Conference.pdf`) | Detection-style character queries can be trained with localization supervision and then adapted to line-level recognition. | Directly supports the SAQT framing, but the paper must distinguish our vertical ancient-text setting, charset adaptation, and query-to-CTC protocol. |
| SVTRv2, ICCV 2025 / arXiv 2024 (`https://arxiv.org/abs/2411.15858`) | Strong CTC recognizers can compete with encoder-decoder models when CTC alignment and visual context are handled well. | Supports keeping CTC rather than replacing the recognizer with an attention decoder. It does not justify a generic SVTR backbone swap inside DTLR. |
| DCTC, AAAI 2024 (`https://ojs.aaai.org/index.php/AAAI/article/view/28575`) | CTC self-distillation / CTC-path regularization can improve STR without changing inference. | We already tested DCTC-lite/Viterbi-style alignment and it was negative; do not continue this branch without a much clearer formulation. |
| Discriminative Character Modeling, IJCAI 2024 (`https://www.ijcai.org/proceedings/2024/195`) | Improve recognition by making character-level visual features more discriminative. | Related to our glyph-prototype auxiliary branch. Current evidence is weak/unstable, so it should remain internal unless a stability run improves. |
| Accurate STR with Efficient Model Scaling and Cloze Self-Distillation, CVPR 2025 (`https://openaccess.thecvf.com/content/CVPR2025/papers/Maracani_Accurate_Scene_Text_Recognition_with_Efficient_Model_Scaling_and_Cloze_CVPR_2025_paper.pdf`) | Uses efficient scaling and cloze-style self-distillation in an encoder-decoder STR setting. | Interesting as a training regularization direction, but it depends on a decoder/language-modeling formulation that does not match SAQT's sorted-query CTC path. Do not port directly. |
| Instruction-Guided STR, TPAMI 2025 (`https://pubmed.ncbi.nlm.nih.gov/40030880/`) | Predicts auxiliary character attributes such as frequency and position. | Conceptually supports our count/position-aware training direction, but the instruction-learning architecture is a poor fit for the current DTLR code path. |

## What We Should Not Do

| Tempting module | Reason to avoid |
| --- | --- |
| Replace ResNet with a newer backbone | Too generic; expensive; weakly tied to the SAQT contribution. Reviewers can dismiss it as engineering. |
| Add a sequence refiner after sorted queries | Already tested SQR and sorted CTC refiner; both were clearly worse than the matched 1000-step base. |
| Keep tuning blank caps | Blank-cap probe worsened CER and did not change blank/nonblank behavior enough. |
| Present expected-count as universal | MTHv2 improves modestly, but HDRC count001 regressed badly. |
| Present decode calibration as a model module | It is useful, but it is validation-selected post-processing. Keep it in protocol, not as the main novelty. |
| Add CHDAC as a main dataset now | Current CHDAC remains too weak; it dilutes the MTHv2/HDRC story unless substantially improved. |

## Current Paper-Ready Model Story

The paper can credibly describe SAQT as a structured query transfer framework:

1. Character-localization learning teaches queries to bind visual character
   evidence and vertical position.
2. Query sorting converts detection-style outputs into a CTC sequence for
   single-column recognition.
3. Charset-aware classifier adaptation transfers shared character parameters
   and initializes new target characters.
4. Full recognition finetuning updates the visual/query stack after head
   reconstruction.
5. A lightweight expected-count auxiliary can be reported as an MTHv2-positive
   optional regularizer, with explicit limitation on HDRC.

This is enough for a conservative CCF-B candidate, provided the claims avoid
"SOTA", "robust", "stable", and "universal".

## Next Experiment Queue

### 1. MTHv2 Length-Balanced Sampling Probe

Status: technically ready, not yet run as a real experiment. A tmux launch was
attempted again on 2026-06-08 after confirming GPU0 was idle, but the sandbox
could not connect to the tmux socket and the escalated retry was rejected by the
execution environment.
The latest operational state and exact launch command are recorded in
`docs/paper-drafts/105_current_decision_and_launch_state.md`.

- Code: `datasets/MTHCombo.py`
- Config: `config/MTHV2_dtlr_length_balance_probe.py`
- Script: `logs/mthv2_length_balance_v2_resume_1000_0608/run_length_balance_probe_0608.sh`
- Smoke: `logs/mthv2_length_balance_smoke_0608`
- Comparison target: `logs/mthv2_base_resume_1000_0607`, valid CER `0.11879202286282202`
- Keep if: valid CER improves and blank ratio does not rise materially.
- Stop if: overall CER worsens, or short buckets improve only by hurting long columns.

Rationale:

- This tests whether the main remaining MTHv2 weakness, short-column behavior,
  is partly caused by training distribution imbalance.
- It is not an architecture contribution, but a positive result could support a
  small "short-column-aware training" ablation.

### 2. Expected-Count Coefficient Sanity Check

Status: optional; lower priority than length-balance.

- Current positive setting: `ctc_count_loss_coef=0.01`,
  `ctc_count_loss_short_weight=3.0`.
- Do not retune broadly. If one more check is needed, test only a weaker
  coefficient such as `0.003` on MTHv2 and HDRC validation.
- Keep only if it preserves MTHv2 gain and no longer collapses HDRC.

Rationale:

- Current MTHv2 result is paper-facing, but HDRC failure blocks a universal
  claim. A weaker coefficient may turn it into a safer optional module.

### 3. Glyph Prototype Auxiliary Stability Check

Status: weak internal branch.

- 1000-step was positive, 2000-step regressed, and count+proto was negative.
- Only continue if there is a precise reason to change the objective, such as
  applying it only to rare characters or only after a warmup.
- Do not add to the paper without a full clean/bias postprocess.

Rationale:

- It is the closest branch to IJCAI-style discriminative character modeling,
  but current evidence is not stable enough.

## If We Need One More "Own Model" Module

The safest conceptual direction is not a bigger network. It is a query-specific
training objective tied to SAQT:

- query activation/count consistency;
- length-aware sampling;
- charset-aware classifier reconstruction;
- localization-to-CTC sequence conversion.

Among these, only charset-aware adaptation and query-localization learning are
already strong enough for the main method. Expected-count is useful but limited.
Length-balanced sampling is the next cheapest evidence check.

## Current Decision

Do not start new architecture branches until the length-balanced probe either
passes or fails. The repository already contains enough negative evidence
against generic refiner/alignment/gating ideas. The strongest paper path is to
consolidate SAQT's current evidence and use any further modules only as small,
carefully bounded ablations.

## 2026-06-08 Web Recheck

Recent STR papers still point to three broad directions: stronger CTC
alignment/context modeling, language or cloze-style distillation, and
character-discriminative feature modeling. For this repository, the first
direction is already represented by SAQT's query-to-CTC conversion, query
activation budget, and expected-count auxiliary term. The second direction
would require adding a decoder or teacher-student training loop and is too
large for the current evidence gap. The third direction overlaps with the
glyph-prototype branch, whose current evidence is unstable. Therefore the
next experiment remains length-balanced sampling; if tmux execution becomes
available, it is still the cheapest way to test the short-column failure mode
without opening a new architecture branch.
