from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

"""
Part D helper script.

This script tests common type conversions and writes results to a text file.
Add or modify VALUES to match the conversions your AI suggested.

Run:
python type_conversion_test.py
"""


@dataclass(frozen=True)
class ConversionResult:
    """Result of a single conversion attempt."""

    expression: str
    ok: bool
    result: str


def try_convert(expression: str, fn: Callable[[], Any]) -> ConversionResult:
    """Run a conversion, capturing exceptions as text."""
    try:
        value = fn()
        return ConversionResult(expression=expression, ok=True, result=repr(value))
    except Exception as exc:  # noqa: BLE001
        return ConversionResult(
            expression=expression,
            ok=False,
            result=f"{type(exc).__name__}: {exc}",
        )


def build_default_tests() -> list[ConversionResult]:
    """Build a baseline conversion set you can extend."""
    values = {
        "0": 0,
        "1": 1,
        "-1": -1,
        "3.14": 3.14,
        "True": True,
        "False": False,
        "''": "",
        "'False'": "False",
        "'123'": "123",
        "'3.14'": "3.14",
        "'  7  '": "  7  ",
        "[]": [],
        "[1, 2, 3]": [1, 2, 3],
        "()": (),
        "(1, 2)": (1, 2),
        "{'a': 1}": {"a": 1},
    }

    constructors: list[tuple[str, Callable[[Any], Any]]] = [
        ("int", int),
        ("float", float),
        ("str", str),
        ("bool", bool),
        ("list", list),
        ("tuple", tuple),
    ]

    results: list[ConversionResult] = []
    for label, value in values.items():
        for target_name, ctor in constructors:
            expr = f"{target_name}({label})"
            results.append(try_convert(expr, lambda v=value, c=ctor: c(v)))
    return results


def format_report(results: list[ConversionResult]) -> str:
    """Create a readable report."""
    lines = []
    lines.append("TYPE CONVERSION TEST RESULTS")
    lines.append("=" * 60)
    for item in results:
        status = "OK" if item.ok else "ERROR"
        lines.append(f"{status:<5} {item.expression:<20} -> {item.result}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main() -> None:
    """Entry point."""
    results = build_default_tests()
    report = format_report(results)

    print(report)
    with open("type_conversion_results.txt", "w", encoding="utf-8") as file:
        file.write(report)
    print()
    print("Saved: type_conversion_results.txt")


if __name__ == "__main__":
    main()
