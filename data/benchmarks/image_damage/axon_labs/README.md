# Axon Labs - Cracked vs. Intact Smartphone Images Benchmark

## Overview
Axon Labs dataset for binary visual damage classification of smartphone displays and front covers.

## Format & Labels
* **Format:** High-resolution JPG images.
* **Classes:**
  * `whole`: Screen intact with no cracks (normal wear/micro-scratches permitted).
  * `broken`: Visible glass fractures, hairline cracks, or shatter patterns.
* **Lighting & Angles:** Varied indoor/outdoor ambient lighting, angled perspectives, and reflections.

## Usage in REVIVAI
Evaluates REVIVAI's Step 1 image triage capability:
* Serves as binary screening to confirm user-reported screen damage.
* Tests false-positive rate on screen protectors vs. true panel glass fractures.

## Limitations
* Binary classification only; does not provide pixel-level polygon segmentation or damage depth.
* Exterior photo cannot diagnose underlying internal board or display connector faults.
