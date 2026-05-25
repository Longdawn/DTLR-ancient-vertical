from __future__ import annotations

from typing import Iterable

import torch


def collapse_ctc(tokens: Iterable[int], blank: int = 0) -> list[int]:
    collapsed: list[int] = []
    prev_token = None
    for token in tokens:
        token = int(token)
        if token != prev_token and token != blank:
            collapsed.append(token)
        prev_token = token
    return collapsed


def decode_greedy(pred_probs: torch.Tensor, charset_size: int, blank: int = 0) -> list[int]:
    if pred_probs.ndim == 3:
        if pred_probs.shape[0] != 1:
            raise ValueError(
                "decode_greedy is a single sample helper; expected CTC batch size 1, "
                f"got batch size {pred_probs.shape[0]}"
            )
        token_ids = pred_probs.argmax(-1)[0].tolist()
    elif pred_probs.ndim == 2:
        token_ids = pred_probs.argmax(-1).tolist()
    else:
        raise ValueError(f"expected 2D or 3D CTC tensor, got shape {tuple(pred_probs.shape)}")

    collapsed = collapse_ctc(token_ids, blank=blank)
    return [token - 1 for token in collapsed if 1 <= token <= int(charset_size)]


def ratio_from_target(target: dict, default: float = 1.0) -> float:
    orig_size = target.get("orig_size") if isinstance(target, dict) else None
    if orig_size is None:
        return float(default)
    if torch.is_tensor(orig_size):
        values = orig_size.detach().cpu().reshape(-1).tolist()
    else:
        values = list(orig_size)
    if len(values) < 2:
        return float(default)
    height, width = float(values[0]), float(values[1])
    return height / max(width, 1.0)


def apply_ctc_calibration(
    pred_probs: torch.Tensor,
    *,
    target: dict | None = None,
    blank_bias: float = 0.0,
    nonblank_bias: float = 0.0,
    ratio_nonblank_bias: float = 0.0,
    ratio_min: float = 1.5,
    ratio_max: float = 2.0,
    margin_gate_min: float | None = None,
    margin_gate_max: float | None = None,
) -> torch.Tensor:
    if blank_bias == 0.0 and nonblank_bias == 0.0 and ratio_nonblank_bias == 0.0:
        return pred_probs

    scores = torch.log(pred_probs.clamp(min=1e-12))
    use_margin_gate = margin_gate_min is not None or margin_gate_max is not None
    if use_margin_gate:
        if margin_gate_min is None or margin_gate_max is None:
            raise ValueError("margin gate requires both margin_gate_min and margin_gate_max")
        if float(margin_gate_min) > float(margin_gate_max):
            raise ValueError("margin_gate_min must be <= margin_gate_max")

        if blank_bias != 0.0 or nonblank_bias != 0.0:
            blank_probs = pred_probs[..., 0]
            best_nonblank_probs = pred_probs[..., 1:].amax(dim=-1)
            margins = blank_probs - best_nonblank_probs
            gate_mask = (margins >= float(margin_gate_min)) & (margins <= float(margin_gate_max))
            gate_bias = gate_mask.to(scores.dtype)
            scores[..., 0] += float(blank_bias) * gate_bias
            scores[..., 1:] += float(nonblank_bias) * gate_bias.unsqueeze(-1)
    else:
        scores[..., 0] += float(blank_bias)
        scores[..., 1:] += float(nonblank_bias)

    if ratio_nonblank_bias != 0.0 and target is not None:
        ratio = ratio_from_target(target)
        if float(ratio_min) < ratio <= float(ratio_max):
            scores[..., 1:] += float(ratio_nonblank_bias)

    return scores
