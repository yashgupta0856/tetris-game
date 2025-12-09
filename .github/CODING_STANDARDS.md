# Code Quality and Linting Instructions for AI Coding Agents

## CRITICAL: Pre-Commit Code Quality Validation

**MANDATORY REQUIREMENT**: Before completing ANY code change, you MUST run the code quality validation script to ensure all linting and formatting standards are met.

### Required Actions Before Task Completion

1. **Always Run Auto-Fix Script**:
   ```bash
   python scripts/lint_fix.py --verbose
   ```
   This script will automatically fix:
   - Code formatting (Black)
   - Import sorting (isort)
   - And report on issues that need manual fixing (Flake8, Pylint)

2. **Verify No Manual Fixes Needed**:
   - If the script reports issues that cannot be auto-fixed, you MUST fix them manually
   - Common issues requiring manual fixes:
     - Unused variables or imports
     - Complex code that violates style guidelines
     - Missing or incorrect docstrings
     - Code complexity issues

3. **Test Your Changes**:
   ```bash
   pytest tests/ -v
   ```
   Ensure all tests pass after your changes.

### Code Quality Standards

#### Python Code Formatting
- **Line length**: Maximum 100 characters
- **Formatter**: Black (automatically enforced)
- **Import sorting**: isort with Black profile (automatically enforced)

#### Linting Requirements
- **Flake8**: Must pass with project configuration (.flake8)
- **Pylint**: Must pass with project configuration (.pylintrc)
- Configuration files define acceptable warnings and disabled checks

#### File Organization
```
tetris.py           # Main game code
tests/              # Test files
scripts/            # Utility scripts including lint_fix.py
.github/workflows/  # CI/CD automation
```

### Pre-Commit Hooks

This project uses pre-commit hooks that run automatically on `git commit`. These hooks will:
- Format code with Black
- Sort imports with isort
- Check code with Flake8
- Check code with Pylint
- Validate YAML, JSON, TOML files
- Check for trailing whitespace and other common issues

**Note**: If pre-commit hooks fail, the commit will be blocked until issues are fixed.

### GitHub Actions Workflows

Two workflows monitor code quality:

1. **Auto-Fix Workflow** (`.github/workflows/autofix.yml`):
   - Runs on PR creation/update
   - Automatically fixes formatting and import issues
   - Commits fixes back to the PR branch
   - Posts comment when fixes are applied

2. **CI Workflow** (`.github/workflows/ci.yml`):
   - Runs comprehensive checks including:
     - Code formatting validation
     - Linting with multiple tools
     - Test execution with coverage
     - Security scanning
   - Must pass before PR can be merged

### AI Coding Agent Workflow

When making code changes as an AI coding agent (GitHub Copilot Workspace, etc.):

1. **Make your code changes** following project patterns and conventions

2. **Before considering the task complete**, run:
   ```bash
   python scripts/lint_fix.py --verbose
   ```

3. **Review the output**:
   - ✓ Green checks = good
   - ✗ Red errors = must fix manually
   - ⚠ Warnings = review and fix if needed

4. **If manual fixes are needed**:
   - Fix the reported issues
   - Run the script again to verify
   - Repeat until all checks pass

5. **Run tests to ensure nothing broke**:
   ```bash
   pytest tests/ -v
   ```

6. **Only after all checks pass**, mark the task as complete

### Common Issues and Fixes

#### Unused Imports
```python
# Bad - flake8 will report F401
from typing import List
# ... but List is never used

# Good - remove unused import
# (import removed)
```

#### Line Too Long
```python
# Bad - exceeds 100 characters
very_long_function_name(argument1, argument2, argument3, argument4, argument5, argument6)

# Good - use multi-line formatting
very_long_function_name(
    argument1, argument2, argument3,
    argument4, argument5, argument6
)
```

#### Import Sorting
```python
# Bad - imports not sorted
import pygame
from typing import List
import random

# Good - sorted by isort (automatic)
import random
from typing import List

import pygame
```

### Quick Reference Commands

```bash
# Auto-fix all issues (discovers all Python files automatically)
python scripts/lint_fix.py --verbose

# Check only (no fixes)
python scripts/lint_fix.py --check-only

# Manual commands (all auto-discover files via configuration)
black .                  # Format all Python files
isort .                  # Sort all imports
flake8                   # Check all files (uses .flake8 config)
pylint *.py              # Lint source files in project root

# Run all pre-commit hooks
pre-commit run --all-files

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=tetris --cov-report=html
```

### VS Code Integration

If working in VS Code, use the provided tasks:
- **Ctrl+Shift+P** → "Tasks: Run Task"
- Select "Lint: Fix All Issues" to run the auto-fix script
- Other useful tasks:
  - "Lint: Check Only (No Fix)"
  - "CI: Full Check (Local)"
  - "Test: Run with Coverage"

### Configuration Files

The project uses these configuration files (DO NOT modify without good reason):

- `.pylintrc` - Pylint configuration
- `.flake8` - Flake8 configuration
- `pyproject.toml` - Black, isort, pytest, coverage configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

**All tools auto-discover Python files** based on these configurations. No need to specify file paths manually - the tools handle it automatically and scale as your project grows.

### Summary Checklist for AI Agents

Before marking any task complete:

- [ ] All code changes implemented
- [ ] `python scripts/lint_fix.py --verbose` executed
- [ ] All auto-fixes applied successfully
- [ ] No manual fix issues remaining (or all fixed)
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Code follows project conventions
- [ ] No breaking changes to existing functionality

**FAILURE TO RUN LINTING BEFORE COMPLETION WILL RESULT IN CI FAILURES AND PR REJECTIONS.**

---

## Additional Guidelines for Cloud Coding Agents

When operating as a GitHub Copilot Workspace agent or similar:

1. **Always include the lint fix script in your final steps**
2. **Include the script output in your summary** so the user can see what was fixed
3. **If issues can't be auto-fixed, explicitly list them** in your completion message
4. **Don't close the task** until you've confirmed all quality checks pass
5. **Update documentation** if you add new code patterns or conventions

### Example Completion Message

```
✓ Task completed successfully!

Changes made:
- Added new feature X
- Updated tests for feature X
- Fixed edge case in function Y

Code quality validation:
✓ Black formatting: PASSED
✓ isort import sorting: PASSED
✓ Flake8 linting: PASSED
✓ Pylint checks: PASSED
✓ All tests passing: 15/15

The code is ready for review and merge.
```

This ensures PRs won't fail on code quality checks and maintains high code standards throughout the project.
