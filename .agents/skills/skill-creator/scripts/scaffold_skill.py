#!/usr/bin/env python3
"""
scaffold_skill.py - Creates the structure of a new skill
Usage: python scaffold_skill.py <skill_name>
"""

import os
import sys
import re

def create_skill(name: str):
    if not name:
        print("Error: Skill name is required")
        print("Usage: python scaffold_skill.py <skill_name>")
        return 1

    skill_path = f"skills/{name}"

    if os.path.exists(skill_path):
        print(f"Error: Skill '{name}' already exists at {skill_path}")
        return 1

    os.makedirs(f"{skill_path}/scripts", exist_ok=True)
    os.makedirs(f"{skill_path}/examples", exist_ok=True)
    os.makedirs(f"{skill_path}/resources", exist_ok=True)

    template = f"""---
name: {name}
description: Description of the skill {name}.
---

# {name}

## When to use this skill
- 

## How to use it
- 
"""

    with open(f"{skill_path}/SKILL.md", "w", encoding="utf-8") as f:
        f.write(template)

    print(f"Skill structure '{name}' created successfully at {skill_path}")
    return 0

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(create_skill(name))