---
name: github-committer
description: Standardizes GitHub commit creation using Conventional Commits with a 50-character limit.
---

# GitHub Committer

This skill ensures all commits in the repository follow a professional, readable, and consistent standard.

## When to Use This Skill
- Whenever you need to make a commit of changes in Git.
- When collaborating on projects that require structured commit messages.

## Commit Message Format
The mandatory format is:
`type: description`

### Types
| Type | Description |
| :--- | :--- |
| **feat** | A new feature |
| **fix** | A bug fix |
| **docs** | Documentation changes |
| **style** | Changes that do not affect code meaning (spacing, formatting) |
| **refactor** | Code change that neither fixes a bug nor adds a feature |
| **test** | Add or correct tests |
| **chore** | Changes to build process or auxiliary tools |

### Critical Rules
1. **Length**: The description (after type) must not exceed **50 characters**.
2. **Imperative**: Use imperative mood in the description (e.g., "add button" instead of "added button").
3. **Lowercase**: The type must be lowercase.

## Correct Example
`feat: add quick save button`

## Tools

### Linux/Mac
```bash
# Make executable
chmod +x .agents/skills/github-committer/scripts/git-commit-helper.sh

# Interactive mode
.agents/skills/github-committer/scripts/git-commit-helper.sh

# With arguments: type message
.agents/skills/github-committer/scripts/git-commit-helper.sh feat "add button"
```

### Windows (PowerShell)
```powershell
# Run
.agents/skills/github-committer/scripts/git-commit-helper.ps1

# With arguments
.agents/skills/github-committer/scripts/git-commit-helper.ps1 -Type feat -Message "add button"
```