"""Validation report formatting."""

from __future__ import annotations


def print_report(errors: list[str], warnings: list[str]) -> None:
    if errors:
        validation_status = "fail"
        display_status = "FAIL"
    elif warnings:
        validation_status = "pass-with-warnings"
        display_status = "PASS WITH WARNINGS"
    else:
        validation_status = "pass"
        display_status = "PASS"

    print(f"validation_status={validation_status}")
    print(f"Validation: {display_status}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
