---
name: skill-creator
description: Guides the agent in creating new skills following official standards.
---

# Skill Creator

This skill allows you to create and structure new skills consistently within the workspace. Skills are knowledge packages that extend your capabilities.

## When to Use This Skill
- When the user asks you to create a new skill.
- When you need to structure specific knowledge or repetitive workflows.
- When you want to improve documentation of how you perform certain tasks.

## Skill Structure
A skill is organized in a folder within `.agents/skills/` with the following structure:
- `SKILL.md`: The main file with instructions and YAML frontmatter.
- `scripts/`: (Optional) Automation or helper scripts.
- `examples/`: (Optional) Usage examples or reference implementations.
- `resources/`: (Optional) Templates, images, or required assets.

## Instructions to Create a New Skill
1. **Define the purpose**: Ensure the skill has a unique and clear focus.
2. **Create the folder**: `mkdir .agents/skills/<skill-name>`
3. **Write the SKILL.md**:
    - Include frontmatter with `name` and `description` (required).
    - Use Markdown to detail instructions.
    - Be specific about when and how the agent should use the skill.
4. **Add resources**: If the skill requires scripts (e.g., Python, JavaScript, PowerShell), place them in `scripts/`.
5. **Validate**: Ensure the structure is correct and file links work.

## Frontmatter Example in SKILL.md
```yaml
---
name: my-new-skill
description: Brief description of what it does (in third person).
---
```

## Helper Tools

### Linux/Mac
```bash
# Make executable
chmod +x .agents/skills/skill-creator/scripts/scaffold_skill.sh

# Run
.agents/skills/skill-creator/scripts/scaffold_skill.sh skill_name
```

### Windows (PowerShell)
```powershell
# Run
.agents/skills/skill-creator/scripts/scaffold_skill.ps1 -Name skill_name
```