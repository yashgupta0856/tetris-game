## Description
<!-- Describe your changes in detail -->

## Type of Change
<!-- Mark the relevant option with an 'x' -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code quality improvement

## How Has This Been Tested?
<!-- Describe the tests you ran to verify your changes -->
- [ ] Existing tests pass: `pytest tests/ -v`
- [ ] Added new tests for new functionality
- [ ] Manually tested gameplay/features

## Code Quality Checklist
<!-- REQUIRED: All items must be checked before merge -->

### Automated Checks
- [ ] Code formatted with Black: `python scripts/lint_fix.py --verbose`
- [ ] Imports sorted with isort: ✓ (included in lint_fix.py)
- [ ] Flake8 checks pass: ✓ (included in lint_fix.py)
- [ ] Pylint checks pass: ✓ (included in lint_fix.py)
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Pre-commit hooks installed and passing: `python scripts/setup_hooks.py`

### Manual Review
- [ ] Code follows project conventions
- [ ] Comments added for complex logic
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or documented if necessary)

## AI Agent Compliance
<!-- If this PR was created/assisted by an AI coding agent -->
- [ ] Followed [CODING_STANDARDS.md](.github/CODING_STANDARDS.md) requirements
- [ ] Ran `python scripts/lint_fix.py --verbose` before completion
- [ ] All linting output reviewed and issues resolved
- [ ] Tests executed and verified passing

## Screenshots (if applicable)
<!-- Add screenshots to help explain your changes -->

## Additional Notes
<!-- Any additional information reviewers should know -->

---

**For Reviewers**:
- Check that CI checks pass (auto-fix workflow may have committed fixes)
- Verify code quality standards are met
- Test functionality if UI/gameplay changes
