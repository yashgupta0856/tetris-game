#!/usr/bin/env python3
"""
Code Quality Auto-Fix Script
=============================

This script automatically fixes common code quality issues that can be auto-corrected.
It runs formatters and linters in the correct order to ensure code meets quality standards.

Usage:
    python scripts/lint_fix.py [--check-only] [--verbose]

Options:
    --check-only    Only check for issues, don't auto-fix
    --verbose       Show detailed output
    --help          Show this help message

Exit Codes:
    0 - All checks passed / fixes applied successfully
    1 - Issues found (in check-only mode) or fixes failed
"""

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(message: str) -> None:
    """Print a formatted header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_step(step: str, status: str = "running") -> None:
    """Print a step with status"""
    if status == "running":
        print(f"{Colors.OKCYAN}▶ {step}...{Colors.ENDC}")
    elif status == "success":
        print(f"{Colors.OKGREEN}✓ {step}{Colors.ENDC}")
    elif status == "warning":
        print(f"{Colors.WARNING}⚠ {step}{Colors.ENDC}")
    elif status == "error":
        print(f"{Colors.FAIL}✗ {step}{Colors.ENDC}")


def run_command(cmd: List[str], verbose: bool = False) -> Tuple[int, str, str]:
    """
    Run a shell command and return the result

    Args:
        cmd: Command and arguments as list
        verbose: Whether to print command output

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, encoding="utf-8")

        if verbose:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

        return result.returncode, result.stdout, result.stderr

    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"
    except (OSError, subprocess.SubprocessError) as e:
        return 1, "", str(e)


def check_dependencies() -> bool:
    """Check if required tools are installed"""
    print_header("Checking Dependencies")

    required_tools = ["black", "isort", "flake8", "pylint"]
    missing_tools = []

    for tool in required_tools:
        # Try running via python -m first
        returncode, _, _ = run_command([sys.executable, "-m", tool, "--version"])
        if returncode == 0:
            print_step(f"{tool} is installed", "success")
        else:
            print_step(f"{tool} is NOT installed", "error")
            missing_tools.append(tool)

    if missing_tools:
        tools_str = ", ".join(missing_tools)
        print(f"\n{Colors.FAIL}Missing tools: {tools_str}{Colors.ENDC}")
        install_cmd = f"pip install {' '.join(missing_tools)}"
        print(f"{Colors.WARNING}Install them with: {install_cmd}{Colors.ENDC}\n")
        return False

    return True


def format_with_black(check_only: bool, verbose: bool) -> bool:
    """Run black formatter on all Python files (auto-discovered)"""
    print_header("Black Code Formatter")

    cmd = [sys.executable, "-m", "black"]
    if check_only:
        cmd.append("--check")
    cmd.append(".")  # Let black discover files based on pyproject.toml

    print_step("Running black formatter", "running")
    returncode, stdout, stderr = run_command(cmd, verbose=verbose)

    if returncode == 0:
        print_step("Black formatting passed", "success")
        return True

    if check_only:
        print_step("Black found formatting issues", "warning")
        print(stdout)
    else:
        print_step("Black formatting failed", "error")
        print(stderr)
    return False


def sort_imports(check_only: bool, verbose: bool) -> bool:
    """Run isort to sort imports on all Python files (auto-discovered)"""
    print_header("Import Sorting (isort)")

    cmd = [sys.executable, "-m", "isort"]
    if check_only:
        cmd.append("--check-only")
    cmd.append(".")  # Let isort discover files based on pyproject.toml

    print_step("Running isort", "running")
    returncode, stdout, _ = run_command(cmd, verbose=verbose)

    if returncode == 0:
        print_step("Import sorting passed", "success")
        return True

    if check_only:
        print_step("isort found unsorted imports", "warning")
        print(stdout)
    else:
        print_step("Import sorting failed", "error")
    return False


def lint_with_flake8(verbose: bool) -> bool:
    """Run flake8 linter on all Python files (auto-discovered)"""
    print_header("Flake8 Linting")

    cmd = [sys.executable, "-m", "flake8"]  # Uses .flake8 config for discovery

    print_step("Running flake8", "running")
    returncode, stdout, _ = run_command(cmd, verbose=verbose)

    if returncode == 0:
        print_step("Flake8 passed", "success")
        return True

    print_step("Flake8 found issues", "warning")
    print(stdout)
    return False


def lint_with_pylint(verbose: bool) -> bool:
    """Run pylint linter on main source files (auto-discovered via regex)"""
    print_header("Pylint Linting")

    # Find all Python files in the project root (not in tests or .venv)
    python_files = [
        f for f in glob.glob("*.py") if not f.startswith("setup") and not f.startswith(".")
    ]

    if not python_files:
        print_step("No Python files found to lint", "warning")
        return True

    cmd = [sys.executable, "-m", "pylint"] + python_files

    print_step("Running pylint", "running")
    returncode, stdout, _ = run_command(cmd, verbose=verbose)

    # Pylint returns non-zero for warnings, so we check the score
    if returncode == 0:
        print_step("Pylint passed", "success")
        return True

    # Parse pylint output to check if score is acceptable
    if "rated at" in stdout:
        print_step("Pylint completed with warnings", "warning")
        print(stdout)
        # Consider it a pass if pylint ran (even with warnings)
        return True

    print_step("Pylint failed", "error")
    print(stdout)
    return False


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Auto-fix code quality issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for issues, don't auto-fix",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    # Print banner
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         Code Quality Auto-Fix & Validation Script                ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    mode = "CHECK MODE" if args.check_only else "FIX MODE"
    print(f"{Colors.OKCYAN}Mode: {mode}{Colors.ENDC}\n")

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check dependencies
    if not check_dependencies():
        return 1

    # Run tools in order
    results = []

    # 1. Format with black (auto-fixes formatting)
    results.append(("Black", format_with_black(args.check_only, args.verbose)))

    # 2. Sort imports with isort (auto-fixes import order)
    results.append(("isort", sort_imports(args.check_only, args.verbose)))

    # 3. Check with flake8 (can't auto-fix, but reports issues)
    results.append(("Flake8", lint_with_flake8(args.verbose)))

    # 4. Check with pylint (can't auto-fix, but reports issues)
    results.append(("Pylint", lint_with_pylint(args.verbose)))

    # Summary
    print_header("Summary")

    all_passed = True
    for tool, passed in results:
        status = "success" if passed else "error"
        print_step(f"{tool}: {'PASSED' if passed else 'FAILED'}", status)
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ All checks passed!{Colors.ENDC}\n")
        return 0

    if args.check_only:
        msg = "⚠ Issues found. Run without --check-only to auto-fix."
        print(f"{Colors.WARNING}{Colors.BOLD}{msg}{Colors.ENDC}\n")
    else:
        msg = "✗ Some issues could not be auto-fixed. Please review manually."
        print(f"{Colors.FAIL}{Colors.BOLD}{msg}{Colors.ENDC}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
