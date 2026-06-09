# Figure 1 Blueprint: SAQT Overview

## Purpose

This figure should make the paper readable at first glance. It should show that SAQT is not a page-layout system and not an inference-time detector. The central message is: character boxes supervise queries during structure learning, while final recognition remains line-level CTC sequence prediction.

## Layout

Use a left-to-right three-stage diagram with a small inference branch underneath.

### Panel (a): Input and Structural Supervision

- Input: cropped vertical single-column ancient text image.
- Optional training signal: character boxes over the column.
- Label: "Line-level transcription" above the text string.
- Label: "Character boxes only for structure learning" near the boxes.

Visual cue: show a tall narrow text crop with several character boxes. Do not draw page layout, column detection, or reading-order arrows beyond the single column.

### Panel (b): Structure-Aware Query Learning

- Backbone: ResNet-50 / visual encoder.
- Transformer encoder-decoder with fixed queries.
- Query outputs: class logits and boxes.
- Losses:
  - DETR-style matching loss.
  - Query activation budget.

Visual cue: show a bank of query tokens attending to vertical character regions. Mark the budget as a small regularizer attached to nonblank activations, not as a separate model branch.

### Panel (c): Charset-Aware Classifier Adaptation and CTC Training

- Show reference charset \(\mathcal{A}_s\) and target charset \(\mathcal{A}_t\).
- Shared characters: arrows copying classifier rows.
- New characters: arrows from unused/random source rows to target rows.
- Sorted query logits become a vertical-order CTC sequence.
- CTC loss uses line-level transcription.

Visual cue: use a compact table-like classifier block. Avoid drawing language model components.

### Inference Branch

- Input image.
- Query outputs.
- Sort by vertical coordinate.
- Greedy CTC decoding.
- Optional blank/nonblank calibration.
- Output text string.

Label clearly: "No character boxes required at inference."

## Caption Draft

Figure 1. Overview of SAQT. During localization-supervised query learning, character boxes supervise detection-style queries to learn character-level visual evidence and vertical spatial organization. For recognition, query outputs are sorted by vertical position and converted into a CTC sequence trained with line-level transcription. When the target charset differs from the reference charset, classifier rows for shared characters are inherited and rows for new characters are initialized from reference classifier parameters. At inference time, SAQT requires only the cropped single-column image and outputs a text string; character boxes are not used.

## QA Checklist

- The figure must not imply page-level layout analysis.
- The inference path must not require character boxes.
- The query activation budget must be shown as a training regularizer.
- Charset adaptation must be shown as parameter initialization, not as an inference module.
- The final output must be a character sequence, not detected boxes.
