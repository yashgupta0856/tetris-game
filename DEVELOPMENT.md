# Development Guide

## Code Quality Standards

Automated code quality enforcement using Black, isort, Flake8, Pylint, pytest, and pre-commit hooks.

## Quick Start

### Auto-Fix All Issues (Required Before Commit)

```bash
python scripts/lint_fix.py --verbose
```

Auto-discovers files via `pyproject.toml`, `.flake8`, `.pylintrc`. Solution scales automatically.

### Pre-Commit Hooks

```bash
python scripts/setup_hooks.py  # Auto-check on git commit
```

### VS Code Tasks

**Ctrl+Shift+P** → "Tasks: Run Task" → "Lint: Fix All Issues" (or Check Only, Full CI Check)

## AI Coding Agents

**Mandatory**: Read `.github/CODING_STANDARDS.md`. Always run `python scripts/lint_fix.py --verbose` before task completion.

## Manual Commands

```bash
# All commands auto-discover files
black .           # Format
isort .           # Sort imports
flake8            # Style check
pylint *.py       # Lint source files
pytest tests/ -v  # Test
pytest tests/ -v --cov=tetris --cov-report=html  # Coverage
```

## CI/CD Workflows

1. **Auto-Fix** (`.github/workflows/autofix.yml`): Fixes formatting on PRs, commits fixes back
2. **CI** (`.github/workflows/ci.yml`): Tests on Python 3.8-3.12, validates quality, must pass for merge
3. **Release** (`.github/workflows/release.yml`): Builds packages, creates releases

## PR Requirements

✅ Pass linting ✅ Pass tests ✅ Maintain coverage ✅ Follow standards

## Troubleshooting

**Tools not found**: `pip install black isort flake8 pylint pre-commit`

**Pre-commit fails**: Run `python scripts/lint_fix.py --verbose`, commit again

**CI fails**: Pull latest (auto-fix may have committed), run lint script, fix manually, test, push

**Module not found**: Activate venv, `pip install -e .`

## Best Practices

1. Run linting before commits
2. Use pre-commit hooks
3. Write tests for new features
4. Keep functions <50 lines
5. Document complex logic

## Configuration Files

- `.pylintrc`, `.flake8`, `pyproject.toml` (tool configs)
- `.pre-commit-config.yaml` (git hooks)

See [`.github/CODING_STANDARDS.md`](.github/CODING_STANDARDS.md) for AI agent requirements.
