#!/usr/bin/env python3
"""
git_commit_helper.py - Generates commit messages with Conventional Commits format
Usage: python git_commit_helper.py [type] [message]
Without arguments: interactive mode
"""

import sys

TYPES = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]

def get_type_interactive() -> str:
    print("Select commit type:")
    for i, t in enumerate(TYPES, 1):
        print(f"{i}) {t}")
    while True:
        try:
            choice = int(input("Option: "))
            if 1 <= choice <= len(TYPES):
                return TYPES[choice - 1]
            print("Invalid option. Try again.")
        except (ValueError, EOFError):
            print("Invalid input.")
            return ""

def get_message() -> str:
    return input("Description (max 50 characters): ").strip()

def main():
    commit_type = sys.argv[1] if len(sys.argv) > 1 else ""
    message = sys.argv[2] if len(sys.argv) > 2 else ""

    if not commit_type:
        commit_type = get_type_interactive()
        if not commit_type:
            print("Error: Commit type is required")
            return 1

    if commit_type not in TYPES:
        print(f"Error: Invalid commit type. Must be one of: {', '.join(TYPES)}")
        return 1

    if not message:
        message = get_message()

    if len(message) > 50:
        print(f"Error: Description is too long ({len(message)} characters). Maximum 50.")
        return 1

    final_message = f"{commit_type}: {message}"

    print()
    print("Suggested commit:")
    print(final_message)
    print()
    print("Suggested git command:")
    print(f'git commit -m "{final_message}"')

    return 0

if __name__ == "__main__":
    sys.exit(main())