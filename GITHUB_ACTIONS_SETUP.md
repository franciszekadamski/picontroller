# GitHub Actions - Code Quality Checks Setup

This guide explains how to set up and use GitHub Actions for code quality checks in your project.

## What was Created

### 1. `.github/workflows/code-quality.yml`
**Default workflow - Non-blocking checks**
- Runs on every push to `main` or `6-refactor-code-for-attrs-and-linters` branches
- Runs on all pull requests to `main` or `6-refactor-code-for-attrs-and-linters`
- Reports issues but doesn't fail the build (`continue-on-error: true`)
- Checks both `hub/` and `pico/` directories

**Tools used:**
- **Pylint**: Code quality checker (minimum score: 8.0)
- **MyPy**: Static type checker
- **Flake8**: Style guide enforcement (max line length: 120)

### 2. `.github/workflows/code-quality-strict.yml`
**Strict workflow - Blocking checks**
- Manually triggered via GitHub Actions UI
- Runs only on `main` branch by default
- **Fails the build** if any check fails
- Use this for critical merge checks

### 3. `setup.cfg`
**Configuration file**
- Centralizes tool settings for pylint, mypy, and flake8
- Prevents need to pass parameters to each command
- Shared across local development and CI/CD

## How to Use

### Automatic Checks (Default)
The default workflow runs automatically on every push and pull request:

```
Your Code
   ↓
Push to GitHub
   ↓
Workflow Triggers
   ↓
Runs: pylint, mypy, flake8
   ↓
Reports Results (but passes)
   ↓
✅ Merge allowed
```

**View Results:**
1. Go to your GitHub repository
2. Click "Actions" tab
3. Click the latest workflow run
4. Expand each tool to see detailed output

### Strict Checks (Manual)
Trigger manually for critical reviews:

1. Go to GitHub repo → "Actions" tab
2. Select "Code Quality Checks (Strict)"
3. Click "Run workflow"
4. **Workflow FAILS if any issues found**

## Local Development - Run Checks Before Push

### Install Tools Locally
```bash
pip install pylint mypy flake8
```

### Run Checks on Your Machine
```bash
# Check code quality
pylint hub/ pico/ --fail-under=8.0

# Check type hints
mypy hub/ pico/ --ignore-missing-imports

# Check style
flake8 hub/ pico/ --max-line-length=120 --extend-ignore=E203,W503
```

Or all at once:
```bash
pylint hub/ pico/ && mypy hub/ pico/ && flake8 hub/ pico/
```

## Customization

### Change Branches
Edit `.github/workflows/code-quality.yml` and adjust:
```yaml
on:
  push:
    branches: [ main, 6-refactor-code-for-attrs-and-linters ]  # Add/remove branches
  pull_request:
    branches: [ main, 6-refactor-code-for-attrs-and-linters ]
```

### Change Python Version
Edit both workflow files:
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']  # Test multiple versions
```

### Adjust Tool Settings
Edit `setup.cfg`:
```ini
[pylint]
max-line-length = 120          # Change line length
disable = C0111,C0103,R0903   # Add/remove disabled rules
```

### Add Project Requirements
Create/update `requirements.txt` with your dependencies:
```bash
pytest==7.4.0
requests==2.31.0
```

The workflow automatically installs these if file exists.

### Make Checks Blocking (Strict by Default)
Edit `code-quality.yml` and remove `continue-on-error: true`:
```yaml
- name: Run Pylint on hub/
  # Remove this line: continue-on-error: true
  run: |
    pylint hub/ --fail-under=8.0
```

Now workflow will **fail** if any check fails.

## Tool Explanations

### Pylint
- **What it does**: Analyzes code quality, style, and potential bugs
- **Output**: Score 0-10 (higher is better)
- **Common issues**: Missing docstrings, unused variables, naming conventions
- **Threshold**: Set to 8.0 (pass if score ≥ 8.0)

### MyPy
- **What it does**: Checks type hints for correctness
- **Output**: Lists type mismatches and missing annotations
- **Common issues**: Type incompatibilities, missing return types
- **Your code**: Already has comprehensive type hints! ✅

### Flake8
- **What it does**: Enforces PEP 8 style guide
- **Output**: Lists style violations
- **Common issues**: Line too long, extra whitespace, import ordering
- **Line length**: Set to 120 characters (generous for readability)

## Troubleshooting

### Workflow Doesn't Run
- Check you pushed to the correct branch (`main` or `6-refactor-code-for-attrs-and-linters`)
- Go to "Actions" tab to see if workflow is listed
- If missing, check `.github/workflows/code-quality.yml` exists

### False Positives in Type Checking
Add type ignore comments for legitimate cases:
```python
value = external_library_function()  # type: ignore
```

### Want to Skip a File/Directory
Edit workflows to exclude:
```yaml
run: |
  pylint hub/ pico/ --ignore=migrations,tests
```

### Tool Conflicts
If tools disagree (rare), prioritize in order:
1. MyPy (type safety - most critical)
2. Pylint (code quality)
3. Flake8 (style - least critical)

## GitHub Actions Console Output Example

```
✅ Run Pylint on hub/
  Score: 8.5/10 - PASSED

⚠️  Run MyPy on hub/
  Success: no issues found

✅ Run Flake8 on hub/
  Success: 0 issues

✅ Run Pylint on pico/
  Score: 9.2/10 - PASSED

...
```

## Next Steps

1. **Push to GitHub** - Workflows will run automatically
2. **Check Results** - Go to Actions tab to view detailed output
3. **Adjust Settings** - Customize `setup.cfg` for your preferences
4. **Run Locally** - Use same commands on your machine before pushing

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
