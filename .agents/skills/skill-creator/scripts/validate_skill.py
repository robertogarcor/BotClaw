#!/usr/bin/env python3
"""
validate_skill.py - Validates basic skill structure
Usage: python validate_skill.py <skill-path>
"""

import os
import sys
import re
import glob

def validate_skill(skill_path: str) -> int:
    if not skill_path:
        print("Error: Skill path is required")
        print("Usage: python validate_skill.py <skill-path>")
        return 1

    if not os.path.isdir(skill_path):
        print(f"Error: Directory does not exist: {skill_path}")
        return 1

    skill_file = os.path.join(skill_path, "SKILL.md")

    if not os.path.isfile(skill_file):
        print(f"Error: SKILL.md not found in {skill_path}")
        return 1

    print(f"Validating skill: {skill_path}")

    with open(skill_file, "r", encoding="utf-8-sig") as f:
        content = f.read()

    if content.startswith("---"):
        frontmatter = content[:content.find("---", 3) + 3]
    else:
        frontmatter = ""

    if not frontmatter:
        print("Error: Missing frontmatter (---) in SKILL.md")
        return 1

    if not re.search(r"^name:", frontmatter, re.MULTILINE):
        print("Error: Missing 'name:' in frontmatter")
        return 1

    if not re.search(r"^description:", frontmatter, re.MULTILINE):
        print("Error: Missing 'description:' in frontmatter")
        return 1

    line_count = content.count("\n") + 1
    if line_count > 500:
        print(f"Warning: SKILL.md has {line_count} lines (>500). Consider splitting into multiple .md files.")

    scripts_dir = os.path.join(skill_path, "scripts")
    if os.path.isdir(scripts_dir):
        for script in glob.glob(os.path.join(scripts_dir, "*.sh")):
            if not os.access(script, os.X_OK):
                print(f"Warning: {script} is not executable (run: chmod +x)")

    print("Validation passed!")
    return 0

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(validate_skill(path))