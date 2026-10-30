"""Command-line demo of the multi-agent pipeline (no UI needed).

Run with:  python run_demo.py
Useful for testing agents quickly and for terminal-based demos.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph import run_pipeline


def main():
    old_device = {
        "brand": "Samsung", "model": "Galaxy A51", "year": 2021,
        "original_price_lkr": 75000, "condition": "fair",
        "fault": "screen cracked",
    }
    needs = "good camera and battery, occasional gaming"
    budget = 100000.0

    print("=" * 70)
    print("MULTI-AGENT PHONE REPLACEMENT PIPELINE — demo run")
    print("=" * 70)
    state = run_pipeline(old_device, needs, budget)

    print("\nFINAL EXPLANATION:\n")
    print(state["explanation"])

    print("\nAGENT TRACE (collaboration order):")
    for i, step in enumerate(state["trace"], 1):
        details = json.dumps(step["details"], default=str)[:160]
        print(f"  {i}. {step['agent']:<28} {step['action']}")
        print(f"     -> {details}")


if __name__ == "__main__":
    main()
