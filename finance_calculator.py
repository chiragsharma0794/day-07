from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

# -*- coding: utf-8 -*-
"""
Day 7 PM Take Home Assignment
Personal Finance Calculator

Run:
python finance_calculator.py
"""


TOP_LINE = "════════════════════════════════════════════"
MID_LINE = "────────────────────────────────────────────"


@dataclass(frozen=True)
class EmployeeInputs:
    """Container for raw employee inputs."""

    name: str
    annual_salary: float
    tax_percent: float
    monthly_rent: float
    savings_percent: float


def parse_float(raw: str) -> float:
    """Parse a float from user input, accepting commas, ₹, and %."""
    cleaned = raw.strip().replace(",", "").replace("₹", "").replace("%", "")
    return float(cleaned)


def format_inr_number(amount: float, decimals: int = 2) -> str:
    """Format a number using Indian digit grouping with fixed decimals."""
    sign = "-" if amount < 0 else ""
    amount_abs = abs(amount)
    formatted = f"{amount_abs:.{decimals}f}"
    whole, frac = formatted.split(".")
    if len(whole) <= 3:
        grouped = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        parts: list[str] = []
        while rest:
            parts.append(rest[-2:])
            rest = rest[:-2]
        grouped = ",".join(reversed(parts)) + "," + last3
    return f"{sign}{grouped}.{frac}"


def money_inr(amount: float, space_after_symbol: bool = True) -> str:
    """Format a money value with ₹ and Indian grouping."""
    space = " " if space_after_symbol else ""
    return f"₹{space}{format_inr_number(amount)}"


def prompt_non_empty(prompt: str) -> str:
    """Prompt until a non empty string is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Invalid input. Please enter a non empty value.")


def prompt_valid_float(
    prompt: str,
    validate_fn: Callable[[float], bool],
    error_msg: str,
) -> float:
    """Prompt until a valid float satisfying validate_fn is entered."""
    while True:
        raw = input(prompt)
        try:
            value = parse_float(raw)
        except ValueError:
            print("Invalid number. Please try again.")
            continue

        if validate_fn(value):
            return value

        print(error_msg)


def collect_employee_inputs(label: str) -> EmployeeInputs:
    """Collect validated inputs for one employee."""
    print()
    print(f"Enter details for {label}")

    name = prompt_non_empty("Employee name: ")
    annual_salary = prompt_valid_float(
        "Annual salary (₹): ",
        lambda x: x > 0,
        "Salary must be greater than 0.",
    )
    tax_percent = prompt_valid_float(
        "Tax bracket percentage (0 to 50): ",
        lambda x: 0 <= x <= 50,
        "Tax must be between 0 and 50.",
    )
    monthly_rent = prompt_valid_float(
        "Monthly rent (₹): ",
        lambda x: x > 0,
        "Rent must be greater than 0.",
    )
    savings_percent = prompt_valid_float(
        "Savings goal percentage (0 to 100): ",
        lambda x: 0 <= x <= 100,
        "Savings goal must be between 0 and 100.",
    )

    return EmployeeInputs(
        name=name,
        annual_salary=annual_salary,
        tax_percent=tax_percent,
        monthly_rent=monthly_rent,
        savings_percent=savings_percent,
    )


def compute_breakdown(employee: EmployeeInputs) -> dict[str, float]:
    """Compute the monthly breakdown and annual projection."""
    monthly_salary = employee.annual_salary / 12.0
    tax_deduction = monthly_salary * (employee.tax_percent / 100.0)
    net_salary = monthly_salary - tax_deduction

    rent_ratio = (employee.monthly_rent / net_salary) * 100.0 if net_salary else 0.0
    savings_amount = net_salary * (employee.savings_percent / 100.0)
    disposable_income = net_salary - employee.monthly_rent - savings_amount

    return {
        "monthly_salary": monthly_salary,
        "tax_deduction": tax_deduction,
        "net_salary": net_salary,
        "rent_ratio": rent_ratio,
        "savings_amount": savings_amount,
        "disposable_income": disposable_income,
        "annual_tax": tax_deduction * 12.0,
        "annual_savings": savings_amount * 12.0,
        "annual_rent": employee.monthly_rent * 12.0,
        "disposable_percent": (
            (disposable_income / net_salary) * 100.0 if net_salary else 0.0
        ),
    }


def rent_score(rent_ratio: float) -> float:
    """Score rent ratio, where <= 30 is best and >= 60 is worst."""
    if rent_ratio <= 30:
        return 100.0
    if rent_ratio >= 60:
        return 0.0
    return 100.0 - ((rent_ratio - 30.0) * (100.0 / 30.0))


def savings_score(savings_percent: float) -> float:
    """Score savings rate, where >= 30 is best."""
    if savings_percent <= 0:
        return 0.0
    if savings_percent >= 30:
        return 100.0
    return (savings_percent / 30.0) * 100.0


def disposable_score(disposable_percent: float) -> float:
    """Score disposable percent, where >= 40 is best."""
    if disposable_percent <= 0:
        return 0.0
    if disposable_percent >= 40:
        return 100.0
    return (disposable_percent / 40.0) * 100.0


def compute_health_score(employee: EmployeeInputs, breakdown: dict[str, float]) -> int:
    """Compute a financial health score from 0 to 100."""
    rent_subscore = rent_score(breakdown["rent_ratio"])
    savings_subscore = savings_score(employee.savings_percent)
    disposable_subscore = disposable_score(breakdown["disposable_percent"])

    weighted = (
        (0.40 * rent_subscore)
        + (0.30 * savings_subscore)
        + (0.30 * disposable_subscore)
    )
    bounded = max(0.0, min(100.0, weighted))
    return int(round(bounded))


def render_report(employee: EmployeeInputs, breakdown: dict[str, float]) -> str:
    """Render the formatted report matching the sample layout."""
    lines = [
        TOP_LINE,
        "EMPLOYEE FINANCIAL SUMMARY",
        TOP_LINE,
        f"Employee : {employee.name}",
        f"Annual Salary : {money_inr(employee.annual_salary, False)}",
        MID_LINE,
        "Monthly Breakdown:",
        f"Gross Salary : {money_inr(breakdown['monthly_salary'], True)}",
        (
            f"Tax ({employee.tax_percent:.1f}%) : "
            f"{money_inr(breakdown['tax_deduction'], True)}"
        ),
        f"Net Salary : {money_inr(breakdown['net_salary'], True)}",
        (
            f"Rent : {money_inr(employee.monthly_rent, True)} "
            f"({breakdown['rent_ratio']:.1f}% of net)"
        ),
        (
            f"Savings ({employee.savings_percent:.1f}%) : "
            f"{money_inr(breakdown['savings_amount'], True)}"
        ),
        f"Disposable : {money_inr(breakdown['disposable_income'], True)}",
        MID_LINE,
        "Annual Projection:",
        f"Total Tax : {money_inr(breakdown['annual_tax'], True)}",
        f"Total Savings : {money_inr(breakdown['annual_savings'], True)}",
        f"Total Rent : {money_inr(breakdown['annual_rent'], True)}",
        TOP_LINE,
    ]
    return "\n".join(lines)


def render_comparison(
    employee_1: EmployeeInputs,
    breakdown_1: dict[str, float],
    employee_2: EmployeeInputs,
    breakdown_2: dict[str, float],
) -> str:
    """Render a side by side comparison table for two employees."""
    health_1 = compute_health_score(employee_1, breakdown_1)
    health_2 = compute_health_score(employee_2, breakdown_2)

    header = (
        f"{'Metric':<22} {employee_1.name[:14]:>14}  {employee_2.name[:14]:>14}\n"
        f"{'-' * 54}"
    )

    rows = [
        (
            "Annual Salary",
            money_inr(employee_1.annual_salary, False),
            money_inr(employee_2.annual_salary, False),
        ),
        (
            "Monthly Net",
            money_inr(breakdown_1["net_salary"], True),
            money_inr(breakdown_2["net_salary"], True),
        ),
        (
            "Rent Ratio",
            f"{breakdown_1['rent_ratio']:.1f}%",
            f"{breakdown_2['rent_ratio']:.1f}%",
        ),
        (
            "Savings Rate",
            f"{employee_1.savings_percent:.1f}%",
            f"{employee_2.savings_percent:.1f}%",
        ),
        (
            "Monthly Disposable",
            money_inr(breakdown_1["disposable_income"], True),
            money_inr(breakdown_2["disposable_income"], True),
        ),
        ("Health Score", f"{health_1}/100", f"{health_2}/100"),
    ]

    lines = [header]
    for metric, left, right in rows:
        lines.append(f"{metric:<22} {left:>14}  {right:>14}")
    return "\n".join(lines)


def main() -> None:
    """Program entry point."""
    print("Personal Finance Calculator")
    compare_two = input("Compare two employees (y or n): ").strip().lower() == "y"

    employee_1 = collect_employee_inputs("Employee 1")
    breakdown_1 = compute_breakdown(employee_1)
    print()
    print(render_report(employee_1, breakdown_1))

    if not compare_two:
        return

    employee_2 = collect_employee_inputs("Employee 2")
    breakdown_2 = compute_breakdown(employee_2)
    print()
    print(render_report(employee_2, breakdown_2))
    print()
    print("COMPARISON")
    print(render_comparison(employee_1, breakdown_1, employee_2, breakdown_2))


if __name__ == "__main__":
    main()
