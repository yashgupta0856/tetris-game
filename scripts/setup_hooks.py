#!/usr/bin/env python3
"""
Git pre-commit hook installer and manager

This script helps set up git hooks to run code quality checks before commits.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check, encoding="utf-8")
        return result.returncode == 0, result.stdout, result.stderr
    except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
        return False, "", str(e)


def install_pre_commit():
    """Install pre-commit package if not already installed"""
    print("Checking for pre-commit...")

    success, _, _ = run_command(["pre-commit", "--version"], check=False)

    if not success:
        print("Installing pre-commit...")
        success, _, stderr = run_command(
            [sys.executable, "-m", "pip", "install", "pre-commit"], check=False
        )
        if success:
            print("✓ pre-commit installed successfully")
        else:
            print(f"✗ Failed to install pre-commit: {stderr}")
            return False
    else:
        print("✓ pre-commit is already installed")

    return True


def setup_hooks():
    """Set up pre-commit hooks"""
    print("\nSetting up pre-commit hooks...")

    # Install the git hook scripts
    success, stdout, stderr = run_command(["pre-commit", "install", "--install-hooks"], check=False)

    if success:
        print("✓ Pre-commit hooks installed successfully")
        print(stdout)
    else:
        print(f"✗ Failed to install hooks: {stderr}")
        return False

    # Also install pre-push hooks
    success, stdout, stderr = run_command(
        ["pre-commit", "install", "--hook-type", "pre-push"], check=False
    )

    if success:
        print("✓ Pre-push hooks installed successfully")
    else:
        print(f"⚠ Warning: Failed to install pre-push hooks: {stderr}")

    return True


def main():
    """Main entry point"""
    print("=" * 70)
    print("Pre-commit Hook Installer")
    print("=" * 70)

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check if .git directory exists
    if not (project_root / ".git").exists():
        print("✗ Not a git repository. Please initialize git first.")
        return 1

    # Install pre-commit
    if not install_pre_commit():
        return 1

    # Setup hooks
    if not setup_hooks():
        return 1

    print("\n" + "=" * 70)
    print("✓ Setup complete!")
    print("=" * 70)
    print("\nPre-commit hooks are now active. They will run automatically on:")
    print("  • git commit (formatting and linting)")
    print("  • git push (full validation)")
    print("\nTo run checks manually: pre-commit run --all-files")
    print("To skip hooks temporarily: git commit --no-verify")

    return 0


if __name__ == "__main__":
    sys.exit(main())
