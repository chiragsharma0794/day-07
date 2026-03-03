"""
Day 7 PM Take Home Assignment
Interview Ready tasks for Part C.

Run:
python interview_ready.py
"""

from __future__ import annotations


def analyze_value(value) -> str:
    """Return a formatted analysis string for any Python value."""
    value_str = f"{value}"
    type_name = type(value).__name__
    truthy = bool(value)

    try:
        length = len(value)
        length_str = str(length)
    except TypeError:
        length_str = "N/A"

    return (
        f"Value: {value_str} | Type: {type_name} | "
        f"Truthy: {truthy} | Length: {length_str}"
    )


def run_q1_verification() -> None:
    """Verify the Part C Q1 prints by running them."""
    print("Q1 verification outputs")
    print(type(True))
    print(isinstance(True, int))
    print(True + True + False)
    print(int(3.99))
    print(bool("False"))
    print(bool(""))
    print(0.1 + 0.2 == 0.3)
    print("5" + "3")
    print(5 + 3)


def run_q2_examples() -> None:
    """Show example outputs for analyze_value."""
    print("Q2 examples")
    print(analyze_value(42))
    print(analyze_value(""))
    print(analyze_value([1, 2, 3]))
    print(analyze_value((1, 2)))
    print(analyze_value({"a": 1}))


def run_q3_fixed_bug_demo() -> None:
    """Fixed version of the buggy snippet from Part C Q3."""
    name = input("Name: ")
    age = int(input("Age: "))

    if age >= 18:
        status = "Adult"
    else:
        status = "Minor"

    print(f"{name} is {age} years old and is a {status}")
    print(f"In 5 years: {age + 5}")

    score = 85.5
    print(f"Score: {score:.0f}")


def main() -> None:
    """Menu runner."""
    print("Choose an option")
    print("1. Run Q1 verification prints")
    print("2. Run Q2 analyze_value examples")
    print("3. Run Q3 fixed bug demo")

    choice = input("Enter 1, 2, or 3: ").strip()
    if choice == "1":
        run_q1_verification()
    elif choice == "2":
        run_q2_examples()
    elif choice == "3":
        run_q3_fixed_bug_demo()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
