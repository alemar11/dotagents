"""Validation report formatting."""

from __future__ import annotations


def print_report(errors: list[str], warnings: list[str]) -> None:
    if errors:
        print("FAIL")
        for error in errors:
            print(f"ERROR: {error}")
    elif warnings:
        print("PASS_WITH_WARNINGS")
    else:
        print("PASS")
    for warning in warnings:
        print(f"WARN: {warning}")
