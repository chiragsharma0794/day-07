"""
Developer Onboarding Kit
Runs environment checks and writes setup_report.txt.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from importlib import import_module, metadata
from pathlib import Path

MIN_PY_MAJOR = 3
MIN_PY_MINOR = 10
DISK_WARN_BYTES = 1_000_000_000  # 1 GB


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    message: str
    seconds: float


def status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def fmt_seconds(seconds: float) -> str:
    return f"{seconds:.4f}s"


def gb(byte_count: int) -> str:
    return f"{byte_count / 1_000_000_000:.2f} GB"


def check_python_version() -> CheckResult:
    start = time.perf_counter()
    v = sys.version_info
    ok = (v.major, v.minor) >= (MIN_PY_MAJOR, MIN_PY_MINOR)
    current = f"{v.major}.{v.minor}.{v.micro}"
    msg = f"Python version: {current} (>= {MIN_PY_MAJOR}.{MIN_PY_MINOR} required)"
    return CheckResult("Python version", ok, msg, time.perf_counter() - start)


def check_virtual_environment() -> CheckResult:
    start = time.perf_counter()
    in_venv = sys.prefix != sys.base_prefix
    venv_name = Path(sys.prefix).name
    msg = (
        f"Virtual environment: Active ({venv_name})"
        if in_venv
        else "Virtual environment: NOT active"
    )
    return CheckResult("Virtual environment", in_venv, msg, time.perf_counter() - start)


def check_disk_space() -> CheckResult:
    start = time.perf_counter()
    usage = shutil.disk_usage(Path.cwd())
    free = usage.free
    ok = free >= DISK_WARN_BYTES
    msg = f"Disk space free: {gb(free)} (>= {gb(DISK_WARN_BYTES)} recommended)"
    if not ok:
        msg = f"Disk space low: {gb(free)} (< {gb(DISK_WARN_BYTES)}). Consider freeing space."
    return CheckResult("Disk space", ok, msg, time.perf_counter() - start)


def check_import(dist_name: str, module_name: str | None = None) -> CheckResult:
    start = time.perf_counter()
    mod = module_name or dist_name
    try:
        import_module(mod)
        ver = metadata.version(dist_name)
        msg = f"{dist_name} installed: version {ver}"
        return CheckResult(dist_name, True, msg, time.perf_counter() - start)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        msg = f"{dist_name} not available ({exc.__class__.__name__})"
        return CheckResult(dist_name, False, msg, time.perf_counter() - start)


def try_fix_missing(missing: list[str], verbose: bool) -> CheckResult:
    start = time.perf_counter()
    if not missing:
        return CheckResult(
            "Auto fix",
            True,
            "Auto fix: nothing to install",
            time.perf_counter() - start,
        )

    cmd = [sys.executable, "-m", "pip", "install", *missing]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if verbose:
        print("Fix command:", " ".join(cmd))
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print(proc.stderr.strip())

    ok = proc.returncode == 0
    msg = (
        "Auto fix: installed missing packages"
        if ok
        else "Auto fix failed for some packages"
    )
    return CheckResult("Auto fix", ok, msg, time.perf_counter() - start)


def check_internet() -> CheckResult:
    start = time.perf_counter()
    try:
        import requests  # type: ignore

        urls = [
            "https://pypi.org/simple/pip/",
            "https://www.python.org/",
            "https://www.example.com",
        ]
        last_error = ""
        for url in urls:
            try:
                resp = requests.get(url, timeout=5)
                ok = resp.status_code < 400
                msg = f"Internet connectivity: OK via {url} (HTTP {resp.status_code})"
                return CheckResult("Internet", ok, msg, time.perf_counter() - start)
            except requests.exceptions.SSLError as exc:
                last_error = f"SSLError on {url}: {exc.__class__.__name__}"
            except requests.exceptions.RequestException as exc:
                last_error = f"Request error on {url}: {exc.__class__.__name__}"

        return CheckResult(
            "Internet",
            False,
            f"Internet error ({last_error})",
            time.perf_counter() - start,
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return CheckResult(
            "Internet",
            False,
            f"Internet error ({exc.__class__.__name__})",
            time.perf_counter() - start,
        )


def list_packages() -> list[tuple[str, str]]:
    pkgs: list[tuple[str, str]] = []
    for dist in metadata.distributions():
        name = dist.metadata.get("Name", "unknown")
        ver = dist.version or "unknown"
        pkgs.append((name, ver))
    pkgs.sort(key=lambda x: x[0].lower())
    return pkgs


def write_report(path: Path, results: list[CheckResult], total_seconds: float) -> None:
    passed = sum(1 for r in results if r.ok)
    total = len(results)

    lines: list[str] = []
    lines.append("=== Developer Onboarding Check ===")
    for r in results:
        lines.append(f"[{status(r.ok)}] {r.message} | time={fmt_seconds(r.seconds)}")
    lines.append("---")
    lines.append(f"Result: {passed}/{total} checks passed")
    lines.append(f"Total execution time: {fmt_seconds(total_seconds)}")
    lines.append("")
    lines.append("Installed packages (name==version):")
    for name, ver in list_packages():
        lines.append(f"{name}=={ver}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify Python developer setup for onboarding."
    )
    parser.add_argument("--verbose", action="store_true", help="Show extra details.")
    parser.add_argument(
        "--fix", action="store_true", help="Attempt to auto-install missing packages."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start_total = time.perf_counter()

    results: list[CheckResult] = []
    results.append(check_python_version())
    results.append(check_virtual_environment())
    results.append(check_disk_space())

    required = [
        ("pylint", "pylint"),
        ("black", "black"),
        ("numpy", "numpy"),
        ("requests", "requests"),
    ]
    pkg_results: list[CheckResult] = []
    missing: list[str] = []

    for dist_name, module_name in required:
        r = check_import(dist_name, module_name)
        pkg_results.append(r)
        if not r.ok:
            missing.append(dist_name)

    results.extend(pkg_results)

    if args.fix:
        results.append(try_fix_missing(missing, args.verbose))
        for dist_name, module_name in required:
            results.append(check_import(dist_name, module_name))

    results.append(check_internet())

    total_seconds = time.perf_counter() - start_total
    report_path = Path("setup_report.txt")
    write_report(report_path, results, total_seconds)

    print("=== Developer Onboarding Check ===")
    for r in results:
        print(f"[{status(r.ok)}] {r.message} | time={fmt_seconds(r.seconds)}")
    print(f"Report saved to: {report_path}")

    return 0 if all(r.ok for r in results if r.name != "Disk space") else 1


if __name__ == "__main__":
    raise SystemExit(main())
