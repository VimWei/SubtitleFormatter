# SubtitleFormatter Version Management Guide

## Overview

This guide explains how SubtitleFormatter manages versions using `uv`, the release workflow, and how to keep version information consistent across the project.

## Quick Start

### Daily release
```bash
# Patch release (most common)
uv run python scripts/release.py patch

# Minor release
uv run python scripts/release.py minor

# Major release
uv run python scripts/release.py major
```

### Inspect version
```bash
# Show current version
uv version

# Preview bump result (no changes applied)
uv version --dry-run --bump minor
```

### Use version in code
```python
from subtitleformatter.version import get_version, get_app_title

version = get_version()  # "0.1.0"
title = get_app_title()  # "SubtitleFormatter v0.1.0"
```

## Principles

### 1. Single Source of Truth
- Primary source: `[project] version` in `pyproject.toml`
- All other places read from `pyproject.toml`
- Avoid duplicating version strings

### 2. Semantic Versioning
Follow [SemVer](https://semver.org/):
- MAJOR: incompatible API changes
- MINOR: backwards-compatible features
- PATCH: backwards-compatible bug fixes

## uv version management

### Basic commands
```bash
uv version
uv version --short
uv version 0.2.0
uv version --output-format json
```

### Automatic bump
- Changes only `pyproject.toml`
- May re-lock and sync env (use `--frozen`, `--no-sync` as needed)
- Does not run tests or changelog updates

```bash
uv version --bump patch
uv version --bump minor
uv version --bump major
uv version --bump alpha
uv version --bump beta
uv version --bump rc
uv version --bump dev
```

### Preview mode
```bash
uv version --dry-run --bump minor
```

## Automated release

### Release script steps
`scripts/release.py` automates:
1. Check git status
2. Run tests
3. Check code quality (black + isort) with optional auto-fix
4. Preview version change
5. Confirm release
6. Update version (uv)
7. Update changelog
8. Commit pyproject.toml/uv.lock/docs/changelog.md
9. Create git tag
10. Push to origin

### Before running
1. Commit changes you want in this release
2. Unstage unrelated changes you do not want in the release commit
3. Do not manually edit `pyproject.toml`/`uv.lock`/`docs/changelog.md` – the script updates them

### Using the script
```bash
uv run python scripts/release.py patch
uv run python scripts/release.py minor
uv run python scripts/release.py major
uv run python scripts/release.py alpha
```

### Handling code style failures
If formatting checks fail during step 3, choose `y` at the prompt to auto-fix, or run manually:
```bash
git stash push -u -k -m release-temp-<timestamp>
uv run isort .
uv run black .
uv run black --check .
uv run isort --check-only .
git add .
git commit -m "Style: format with isort/black"
git stash pop -q
uv run isort .
uv run black .
```

## Version module
Use `src/subtitleformatter/version.py` for consistent version access:
```python
from subtitleformatter.version import (
    get_version,
    get_version_display,
    get_full_version_info,
)
```

## GitHub Actions
- `.github/workflows/release.yml`: Publishes GitHub release on tag push, verifies version and attaches notes from `docs/changelog.md`
- `.github/workflows/version-check.yml`: Checks version consistency and changelog format on PRs and main pushes

## Files to include in Git
```bash
scripts/release.py
.github/workflows/
src/subtitleformatter/version.py
docs/version_management_guide.md
docs/changelog.md
```

---

Last updated: 2025-10-14
