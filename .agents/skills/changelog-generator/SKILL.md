---
name: changelog-generator
description: Automatically maintains a CHANGELOG.md file based on Git commit history.
---

# ChangeLog Generator

This skill allows generating and maintaining an up-to-date `CHANGELOG.md` file by extracting information directly from Git repository commits.

## When to Use This Skill
- After making one or several commits to reflect changes in the history.
- When the user requests to see a summary of recent changes.
- When preparing a new version or release of the project.

## How to Use It

### Linux/Mac
```bash
# Make executable
chmod +x .agents/skills/changelog-generator/scripts/update_changelog.sh

# Run
.agents/skills/changelog-generator/scripts/update_changelog.sh

# Customize output file
.agents/skills/changelog-generator/scripts/update_changelog.sh HISTORY.md
```

### Windows (PowerShell)
```powershell
# Run
powershell -ExecutionPolicy Bypass -File .agents/skills/changelog-generator/scripts/update_changelog.ps1

# Customize output file
powershell -ExecutionPolicy Bypass -File .agents/skills/changelog-generator/scripts/update_changelog.ps1 -ChangelogFile "HISTORY.md"
```

## Changelog Structure
The generated file follows a simple and readable format:
- Level 2 headers with the commit date `## [YYYY-MM-DD]`.
- Change list with commit message and short hash `- Message (hash)`.

## Considerations
- The skill assumes the repository uses Git.
- Descriptive commit messages improve the quality of `CHANGELOG.md`.