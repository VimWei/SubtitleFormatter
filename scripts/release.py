#!/usr/bin/env python3
"""Release script for SubtitleFormatter

This script automates the version release process including:
- Version bumping using uv
- Changelog updates
- Git commits and tags
- Remote pushing

Usage:
    python scripts/release.py [bump_type]

    bump_type: patch, minor, major, alpha, beta, rc, dev
    Default: patch
"""

import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Optional

VALID_BUMP_TYPES = ["patch", "minor", "major", "alpha", "beta", "rc", "dev"]


def get_project_url() -> str:
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("urls", {}).get("Homepage", "")
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return ""


def get_releases_url() -> str:
    project_url = get_project_url()
    if project_url and project_url.endswith("/"):
        return f"{project_url}releases"
    elif project_url:
        return f"{project_url}/releases"
    else:
        return ""


def run_command(
    cmd: str, check: bool = True, capture_output: bool = True
) -> subprocess.CompletedProcess:
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    return result


def get_current_version() -> str:
    result = run_command("uv version --short")
    return result.stdout.strip()


def check_git_status() -> bool:
    result = run_command("git status --porcelain", capture_output=True)
    output = result.stdout.splitlines()

    allowed_staged = {"pyproject.toml", "uv.lock", "docs/changelog.md"}
    other_staged: list[str] = []
    has_unstaged = False

    for line in output:
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        staged_flag = status[0]
        unstaged_flag = status[1]

        if staged_flag != " ":
            if path not in allowed_staged:
                other_staged.append(path)
        if unstaged_flag != " ":
            has_unstaged = True

    if other_staged:
        print("❌ Found unrelated staged changes that could be mixed into the release commit:")
        for p in other_staged:
            print(f"   - {p}")
        print("Please commit or unstage these before releasing.")
        return False

    if has_unstaged:
        print("ℹ️  Unstaged changes detected. They will NOT be included in the release commit.")

    return True


def _git_output(cmd: str) -> str:
    try:
        result = run_command(cmd, check=True)
        return result.stdout.strip()
    except SystemExit:
        return ""


def _collect_commits_since_last_tag() -> list[str]:
    prev_tag = _git_output("git describe --tags --abbrev=0 2>NUL || true")
    rev_range = f"{prev_tag}..HEAD" if prev_tag else "HEAD~20..HEAD"
    log = _git_output(f"git log --pretty=format:%s --no-merges {rev_range}")
    subjects = [line.strip() for line in log.splitlines() if line.strip()]
    subjects = [s for s in subjects if s != "Style: format with isort/black"]
    return subjects


def update_changelog(new_version: str, bump_type: str) -> None:
    changelog_path = Path("docs/changelog.md")

    if not changelog_path.exists():
        print("⚠️  Warning: changelog.md not found")
        return

    print(f"📝 Updating changelog.md with version {new_version}")

    with open(changelog_path, "r", encoding="utf-8") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")

    change_descriptions = {
        "patch": "Patch release",
        "minor": "Minor release",
        "major": "Major release",
        "alpha": "Alpha pre-release",
        "beta": "Beta pre-release",
        "rc": "Release Candidate",
        "dev": "Development release",
    }

    change_desc = change_descriptions.get(bump_type, f"{bump_type} release")

    commits = _collect_commits_since_last_tag()
    if commits:
        bullets = "\n".join(f"- {c}" for c in commits)
    else:
        bullets = f"- Automated release: {change_desc}"

    version_entry = f"""## [{new_version}] - {today}

{bullets}

"""

    lines = content.split("\n")
    insert_index = 0

    for i, line in enumerate(lines):
        if line.startswith("## [") and "] - " in line:
            insert_index = i
            break

    lines.insert(insert_index, version_entry.strip() + "\n")

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Updated changelog.md with version {new_version}")


def run_tests() -> bool:
    print("🧪 Running tests...")
    try:
        run_command("uv run pytest tests/ --tb=no -q", capture_output=False)
        print("✅ Tests passed")
        return True
    except SystemExit:
        print("❌ Tests failed")
        return False


def _stash_unstaged_if_any() -> tuple[bool, str]:
    status_lines = run_command("git status --porcelain", capture_output=True).stdout.splitlines()
    has_unstaged = any(line and line[1] != " " for line in status_lines)
    has_untracked = any(line.startswith("?? ") for line in status_lines)
    if not has_unstaged and not has_untracked:
        return False, ""
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f"release-temp-{stamp}"
    run_command(f"git stash push -u -k -m {name}")
    return True, name


def _pop_stash_quiet() -> None:
    run_command("git stash pop -q", check=False)


def _auto_fix_code_style() -> bool:
    print("🛠️  Attempting to auto-fix style (isort + black)...")
    try:
        run_command("uv run isort .", capture_output=False)
        run_command("uv run black .", capture_output=False)
        print("✅ Auto-fix completed")

        print("🔍 Re-checking after auto-fix...")
        run_command("uv run black --check .", capture_output=False)
        run_command("uv run isort --check-only .", capture_output=False)
        print("✅ Re-check passed")

        print("\n📦 Creating 'Style: format with isort/black' commit (release snapshot)...")
        run_command("git add .")
        run_command('git commit -m "Style: format with isort/black"')
        print("📦 Style commit created on release snapshot\n")

        return True
    except SystemExit:
        print("❌ Auto-fix failed")
        return False


def check_code_quality() -> bool:
    print("🔍 Checking code quality...")

    print("🧩 Preparing release snapshot (stash unstaged/untracked, keep index)...")
    stashed, _stash_name = _stash_unstaged_if_any()
    if stashed:
        print("🧩 Release snapshot ready (working tree now reflects what will be released)")
    else:
        print("🧩 No unstaged/untracked changes found; using current tree as release snapshot")
    try:
        try:
            run_command("uv run black --check .", capture_output=False)
            print("✅ Black formatting check passed")
            run_command("uv run isort --check-only .", capture_output=False)
            print("✅ Import sorting check passed")
            return True
        except SystemExit:
            print("❌ Code quality checks failed\n")
            try_fix = input("🔧 Auto-fix with isort+black on release snapshot? (y/N): ")
            if try_fix.lower() != "y":
                return False

            if not _auto_fix_code_style():
                return False

            print("✅ Code quality checks passed after auto-fix")
            return True
    finally:
        if stashed:
            print("\n🔁 Restoring your unstaged changes from stash...")
            _pop_stash_quiet()

        print("\n♻️  Sync formatting in working tree (no commit)...")
        run_command("uv run isort .", capture_output=False)
        run_command("uv run black .", capture_output=False)
        print("♻️  Workspace formatting synced")


def release(bump_type: str = "patch") -> None:
    print(f"🚀 Starting {bump_type} release...")
    print("=" * 50)

    if bump_type not in VALID_BUMP_TYPES:
        print(f"❌ Invalid bump type: {bump_type}")
        print(f"Valid types: {', '.join(VALID_BUMP_TYPES)}")
        sys.exit(1)

    print("1. Checking git status...")
    if not check_git_status():
        print("❌ Please commit or stash your changes before releasing")
        sys.exit(1)
    print("✅ Git working directory is clean")

    print("\n2. Running tests...")
    if not run_tests():
        print("❌ Tests failed. Please fix tests before releasing")
        sys.exit(1)

    print("\n3. Checking code quality...")
    if not check_code_quality():
        print("❌ Code quality checks failed. Please fix issues before releasing")
        sys.exit(1)

    print(f"\n4. Previewing version change...")
    result = run_command(f"uv version --dry-run --bump {bump_type}")
    print(f"📋 {result.stdout.strip()}")

    print(f"\n5. Confirmation")
    confirm = input("🤔 Continue with release? (y/N): ")
    if confirm.lower() != "y":
        print("❌ Release cancelled")
        return

    print(f"\n6. Updating version...")
    run_command(f"uv version --bump {bump_type}")

    new_version = get_current_version()
    print(f"✅ New version: {new_version}")

    print(f"\n7. Updating changelog...")
    update_changelog(new_version, bump_type)

    print(f"\n8. Committing changes...")
    run_command("git add pyproject.toml uv.lock docs/changelog.md")
    run_command(f'git commit -m "Bump version to {new_version}"')
    print("✅ Changes committed")

    print(f"\n9. Creating tag...")
    run_command(f"git tag v{new_version}")
    print(f"✅ Tag v{new_version} created")

    print(f"\n10. Pushing to remote...")
    run_command("git push origin main --tags")
    print("✅ Pushed to remote")

    print(f"\n🎉 Release {new_version} completed successfully!")

    releases_url = get_releases_url()
    if releases_url:
        print(f"📦 View releases: {releases_url}")


def show_help() -> None:
    print(__doc__)
    print(f"\nValid bump types:")
    for bump_type in VALID_BUMP_TYPES:
        print(f"  - {bump_type}")


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            show_help()
            return
        bump_type = sys.argv[1]
    else:
        bump_type = "patch"

    try:
        release(bump_type)
    except KeyboardInterrupt:
        print("\n❌ Release cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
