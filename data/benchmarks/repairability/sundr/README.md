# Sundr Durability Scores Dataset (Curated Subset)

## Overview
A public dataset compiling device durability metrics, iFixit repairability ratings, and Open Repair Alliance community fix rates across consumer electronics, with a focus on smartphones.

## Schema (`durability-scores-v1.csv`)
* `brand` (string): Device manufacturer.
* `model_name` (string): Canonical commercial model name.
* `category` (string): Device category (`Smartphone`).
* `category_slug` (string): Normalized slug (`smartphone`).
* `durability_score` (integer, 1–5): Editorial durability index (5 = highest longevity/resilience).
* `ifixit_repairability_score` (float/int, 1–10): Official iFixit score based on disassembly ease, adhesive use, and modularity.
* `fix_rate` (float, 0.0–100.0%): Historical percentage of successful repairs from community repair records.
* `fix_rate_sample_size` (integer): Number of ORDS records informing the fix rate.
* `common_failure` (string): Most frequent failure mode recorded for this brand/category.
* `why_durable` (string): Editorial notes on design choices (e.g., modular ports, non-proprietary screws).

## Usage in REVIVAI
Used to ground the `RepairDecisionAgent`:
* Helps determine whether a low-cost repair is economically viable or if the model suffers from structural unrepairability (e.g., high failure rates or low modularity).
* Prioritizes the 206-record curated subset for consistent data quality.
