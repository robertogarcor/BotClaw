#!/usr/bin/env python3
"""
update_changelog.py - Generates CHANGELOG.md from Git history
Usage: python update_changelog.py [changelog_file]
Default: CHANGELOG.md
"""

import subprocess
import sys
import os

def get_git_log() -> list:
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h|%ad|%s", "--date=short"],
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stdout.strip():
            return []
        return result.stdout.strip().split("\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def update_changelog(changelog_file: str = "CHANGELOG.md") -> int:
    commits = get_git_log()

    if not commits:
        print("No commits found.")
        return 1

    lines = ["# Changelog", ""]
    current_date = None

    for commit in commits:
        parts = commit.split("|")
        if len(parts) < 3:
            continue

        hash_part, date, subject = parts[0], parts[1], parts[2]

        if date != current_date:
            lines.append(f"## [{date}]")
            current_date = date

        lines.append(f"- {subject} ({hash_part})")

    with open(changelog_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    count = len([c for c in commits if c.strip()])
    print(f"Updated {changelog_file} with {count} commits.")
    return 0

if __name__ == "__main__":
    changelog_file = sys.argv[1] if len(sys.argv) > 1 else "CHANGELOG.md"
    sys.exit(update_changelog(changelog_file))