# Module 2 Short-Bucket Decode Calibration Summary

Date: 2026-05-29

## Module

Module 2: Decode-time CTC blank/nonblank calibration.

Existing switchable implementation:

- `util/ctc_decoding.py`
- `tools/analyze_ctc_errors.py`
- `tools/sweep_ctc_decode_bias.py`

Switches:

- `blank_bias`
- `nonblank_bias`
- `ratio_nonblank_bias`
- optional margin gates in `tools/sweep_ctc_decode_bias.py`

Default behavior remains unchanged:

- `blank_bias=0.0`
- `nonblank_bias=0.0`
- `ratio_nonblank_bias=0.0`
- with all defaults, `apply_ctc_calibration` returns the original probabilities.

## Verification

Unit test:

```bash
/home/ubuntu/miniconda3/envs/DTLR/bin/python -m unittest tests/test_ctc_eval_utils.py
```

Result:

- `Ran 11 tests in 0.019s`
- `OK`

Smoke test:

```bash
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=/home/ubuntu/DTLR /home/ubuntu/miniconda3/envs/DTLR/bin/python tools/sweep_ctc_decode_bias.py -c config/MTHV2_dtlr.py --dataset_file mth_combo --checkpoint logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth --split val --device cuda:0 --num_workers 0 --max_samples 10 --new_class_embedding --blank_biases 0.0 -1.0 --nonblank_biases 0.0 1.0 --ratio_nonblank_biases 0.0 --output_json logs/mthv2_module2_decode_calibration_smoke_0529.json
```

Result:

- exited `0`
- wrote `logs/mthv2_module2_decode_calibration_smoke_0529.json`
- produced 4 sweep rows on 10 MTHv2 valid samples.

## MTHv2

Baseline checkpoint:

- `logs/mthv2_mth1000mth1200tkh_full_0528-0957/checkpoint_best_regular.pth`

Files:

- clean summary: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/ctc_error_summary_valid_clean_0528.json`
- sweep: `logs/mthv2_mth1000mth1200tkh_full_0528-0957/decode_bias_sweep_valid_0528.json`

Best setting:

- `blank_bias=-2.0`
- `nonblank_bias=1.0`
- `ratio_nonblank_bias=0.0`

Valid comparison:

AR/CR are computed from the same CTC edit-rate summary:

- `AR = 1 - (insertion rate + deletion rate + substitution rate)`
- `CR = 1 - (deletion rate + substitution rate)`

| Metric | Clean | Calibrated |
| --- | ---: | ---: |
| overall AR | `0.9480438539335392` | `0.9543801996279404` |
| overall CR | `0.9502724345354708` | `0.9582141137142696` |
| overall CER | `0.051956146066460804` | `0.04561980037205964` |
| empty rate | `0.03379612714651078` | `0.007124588966021191` |
| deletion rate | `0.0272434535444819` | `0.007677271310802006` |
| insertion rate | `0.002228580601905625` | `0.003833914086329169` |
| substitution rate | `0.02248411192007328` | `0.03410861497492847` |
| len=1 CER | `0.26737967914438504` | `0.22281639928698752` |
| len=1 empty | `0.1948900772430184` | `0.0451574569221628` |
| len=2 CER | `0.22151898734177214` | `0.19026898734177214` |
| len=2 empty | `0.030854430379746837` | `0.0015822784810126582` |
| 3-5 CER | `0.18427569129178703` | `0.15889393314073463` |
| 6-10 CER | `0.1214020427112349` | `0.10584958217270195` |
| 11+ CER | `0.03324255392729002` | `0.02970864133488955` |

Interpretation:

- MTHv2 satisfies the module goal.
- Short empty/deletion improves strongly.
- Overall CER improves.
- Tradeoff: substitutions and a few over-activation insertion cases increase, but the net CER is better.

Representative calibrated errors:

| idx | gt_len | pred_len | CER | gt | pred | error |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| `3302` | 7 | 37 | `5.285714285714286` | `譯丈推誠德安仁` | `###大####習金####行#眞#######論##處#三主王#####` | severe over-activation |
| `2654` | 2 | 3 | `1.5` | `##` | `二十四` | substitutions + insertion |
| `2958` | 2 | 3 | `1.5` | `弟#` | `第子張` | substitutions + insertion |
| `3876` | 2 | 3 | `1.5` | `呻吟` | `由呵呤` | substitutions + insertion |
| `6648` | 2 | 4 | `1.5` | `於冀` | `於苦莖六` | insertion + substitution |

## HDRC

Baseline checkpoint:

- `logs/mth1000mth1200pre_hdrcft_full_0527-1732/checkpoint_best_regular.pth`

Files:

- clean summary: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_clean_0527.json`
- sweep: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/decode_bias_sweep_valid_0527.json`
- calibrated summary: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_summary_valid_bias_b-20_nb04_0529.json`
- calibrated cases: `logs/mth1000mth1200pre_hdrcft_full_0527-1732/ctc_error_cases_valid_bias_b-20_nb04_0529.jsonl`

Best setting:

- `blank_bias=-2.0`
- `nonblank_bias=0.4`
- `ratio_nonblank_bias=0.0`

Valid comparison:

AR/CR are computed from the same CTC edit-rate summary:

- `AR = 1 - (insertion rate + deletion rate + substitution rate)`
- `CR = 1 - (deletion rate + substitution rate)`

| Metric | Clean | Calibrated |
| --- | ---: | ---: |
| overall AR | `0.8656216063081354` | `0.8768119363520468` |
| overall CR | `0.8694461494877001` | `0.8871051513291468` |
| overall CER | `0.13437839369186458` | `0.12318806364795316` |
| empty rate | `0.017869656622284513` | `0.008409250175192713` |
| deletion rate | `0.0863119127437556` | `0.04934132867463053` |
| insertion rate | `0.003824543179564663` | `0.010293214977099957` |
| substitution rate | `0.044241937768544314` | `0.06355351999622268` |
| len=1 CER | `0.1392156862745098` | `0.12352941176470589` |
| len=1 empty | `0.09607843137254903` | `0.047058823529411764` |
| len=2 CER | `0.09745762711864407` | `0.08728813559322034` |
| len=2 empty | `0.003389830508474576` | `0.0` |
| 3-5 CER | `0.05652573529411765` | `0.04503676470588235` |
| 6-10 CER | `0.06733393994540492` | `0.05686988171064604` |
| 11+ CER | `0.15805491233873636` | `0.14687396625868343` |

Interpretation:

- HDRC also satisfies the module goal.
- It improves overall CER and every major length bucket.
- It sharply reduces deletion/empty behavior, with expected substitution/insertion increase from stronger nonblank activation.

Representative calibrated errors:

| idx | gt_len | pred_len | CER | gt | pred | error |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| `1461` | 1 | 3 | `2.0` | `子` | `子子一` | insertion over-activation |
| `2227` | 1 | 2 | `2.0` | `出` | `繼繼` | insertion + substitution |
| `33` | 2 | 3 | `1.5` | `尾二` | `二雲百` | deletion + insertion |
| `22` | 4 | 5 | `1.0` | `二十四世` | `十四四四四` | mixed |
| `521` | 1 | 0 | `1.0` | `偲` | empty | remaining deletion |
| `532` | 1 | 0 | `1.0` | `伉` | empty | remaining deletion |

## Decision

Module 2 is useful and satisfies the stated goal on both MTHv2 and HDRC.

- It improves overall AR/CR/CER under the CTC edit-rate metric.
- It improves overall CER.
- It improves len=1/2 empty/deletion behavior.
- It requires no retraining and keeps baseline defaults unchanged.
- It should be treated as the recommended current module.

No additional full training should be launched for SGQ before using this decode calibration as the evaluation default for the current goal. A third module is not needed unless a stricter target is set for remaining substitution/over-activation errors after calibration.
