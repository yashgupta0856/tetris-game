#!/usr/bin/env bash
# Quick lint fix wrapper script for Unix-like systems

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Run the Python lint fix script
python scripts/lint_fix.py "$@"
