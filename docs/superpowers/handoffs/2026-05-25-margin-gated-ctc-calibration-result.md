# Margin-Gated CTC Calibration Result

Date: 2026-05-25

## 1. Experiment Purpose

This note freezes the result of a narrow decode-side experiment on the trusted MTH1000 full-finetuning baseline:

- checkpoint: `logs/mth1000mth1200pre_mth1000ft_full_0513-2257/checkpoint_best_regular.pth`
- task: add `margin-gated blank suppression` on top of the existing CTC decode-time calibration path

The goal was limited to one question:

- can margin-gating improve on the already-strong fixed decode bias baseline?

Out of scope for this experiment:

- model changes
- training changes
- config changes
- dataset changes
- reranking
- new checkpoints

## 2. Modified Files And Implementation Logic

### Files touched by the implementation

- `util/ctc_decoding.py`
- `tools/sweep_ctc_decode_bias.py`
- `tests/test_ctc_eval_utils.py`
- `tests/test_paper_workflow_tools.py`

### Implementation summary

The existing decode-time calibration path already supports fixed:

- `blank_bias`
- `nonblank_bias`

This experiment added optional gate parameters:

- `margin_gate_min`
- `margin_gate_max`

The gate is defined on each query using:

- `blank_prob - top_nonblank_prob`

Behavior:

- if gate parameters are not provided, behavior remains identical to the original fixed-bias implementation
- if gate parameters are provided, the calibration is applied only to queries whose margin falls inside `[margin_gate_min, margin_gate_max]`

The sweep tool was extended to evaluate gated settings while preserving the same output schema and metric definitions used by the existing fixed-bias sweep.

## 3. CPU Tests And GPU Smoke

### CPU tests

Commands run:

```bash
python -m unittest tests.test_ctc_eval_utils -v
python -m unittest tests.test_paper_workflow_tools -v
```

Recorded results:

- `tests.test_ctc_eval_utils`: `Ran 11 tests ... OK`
- `tests.test_paper_workflow_tools`: `Ran 7 tests ... OK`

Coverage added by these tests:

- no-gate path keeps original behavior
- bias is applied only when margin is inside the gate
- bias is not applied when margin is outside the gate
- batch / shape / blank-index logic stays correct
- sweep setting construction supports `margin_gate_min/max`

### GPU smoke

Smoke outputs:

- `logs/ctc_margin_gate_smoke_0525.json`
- `logs/ctc_fixed_bias_baseline_smoke_0525.json`

On the 100-sample valid smoke:

- baseline greedy: `CER = 0.05741`
- fixed bias (`blank=-0.3, nonblank=+0.3`): `CER = 0.05474`
- best margin-gated setting (`margin_gate_min=0.0, margin_gate_max=0.4`): `CER = 0.05474`

Smoke conclusion:

- gated improved over greedy
- gated did not exceed fixed bias

## 4. Full Valid Comparison

### Compared runs

- baseline greedy
- fixed bias
- margin-gated
- shortboost presence training run

### Key metrics

| Run | CER | Empty rate | pred/gt len ratio | del rate | sub rate | ins rate | len=1 CER | len=2 CER | len>=11 CER |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline greedy | `0.07841477863481394` | `0.0485631543773669` | `0.9636337258505211` | `0.0387358850980487` | `0.03730928258819547` | `0.0023696109485697703` | `0.29020556227327693` | `0.28264331210191085` | `0.058329776639635796` |
| fixed bias `blank=-0.3, nonblank=+0.3` | `0.07486036221195928` | `0.04321675206059256` | `0.9708150978069009` | `0.0319897478056919` | `0.04006576879367459` | `0.0028048456125927897` | `0.2756952841596131` | `0.27070063694267515` | `0.05556978233034571` |
| margin-gated `blank=-0.3, nonblank=+0.3, gate=[0.0, 0.4]` | `0.07486036221195928` | `0.04321675206059256` | `0.9708150978069009` | `0.0319897478056919` | `0.04006576879367459` | `0.0028048456125927897` | `0.2756952841596131` | `0.27070063694267515` | `0.05556978233034571` |
| shortboost presence `mth1000_realmain_shortboost_presence_0524-2307` | `0.07955122470198515` | `0.04165738471820005` | `0.962618178301134` | `0.0395096356118674` | `0.037913775177116325` | `0.0021278139130014267` | `0.27690447400241835` | `0.27945859872611467` | `0.05941101152368758` |

### Direct comparison

- baseline greedy -> fixed bias:
  - clear overall improvement
  - clear `len=1` and `len=2` improvement
  - better long-text bucket
- fixed bias -> margin-gated:
  - no metric change
  - no additional gain on full valid
- shortboost vs fixed bias / margin-gated:
  - shortboost helps some empty-rate behavior
  - but it is worse on overall CER
  - and worse on the long-text bucket

## 5. Core Conclusion

The result is straightforward:

1. margin-gated calibration is clearly better than baseline greedy
2. margin-gated calibration is exactly identical to the existing fixed-bias decode baseline on full valid
3. therefore margin-gated calibration adds no demonstrated benefit beyond fixed bias in this experiment

This means the experiment is still useful, but as a bounded negative result:

- the implementation works
- the evaluation path is valid
- the selected gate does not improve on the simpler baseline

## 6. Follow-Up Recommendation

Recommended interpretation going forward:

- keep fixed bias as the simpler decode baseline
- record margin-gated calibration as a negative result
- move the next decode-side iteration to `conditional short rescue`

Why this is the right next step:

- fixed bias already captures the main blank-vs-nonblank calibration gain
- margin-gating did not separate a better subset of queries on this checkpoint
- the next plausible gain source is a more targeted short-output intervention rather than another small variant of the same global calibration rule

## 7. What Is Safe To Reuse In Paper Writing

These claims are supported by this experiment and are safe to reuse in paper motivation or experimental discussion:

- short-text failures are strongly affected by CTC blank-vs-nonblank calibration
- simple decode-time blank suppression produces a meaningful gain over naive greedy decode
- not every more selective calibration variant yields additional benefit
- a negative result here supports using the simpler fixed decode bias as the main baseline

What this experiment does **not** support:

- claiming margin-gated calibration is better than fixed bias
- claiming gating should be part of the main method

