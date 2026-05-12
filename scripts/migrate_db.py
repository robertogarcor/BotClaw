#!/usr/bin/env python3
"""
Migrate bot.db to add new fields:
- users: voice_mode, last_access
- sessions: updated_at
"""

import sqlite3
import sys
from pathlib import Path

def migrate(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check existing columns in users
    cursor.execute("PRAGMA table_info(users)")
    users_columns = [col[1] for col in cursor.fetchall()]

    if 'voice_mode' not in users_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN voice_mode TEXT DEFAULT 'off'")
        print("✓ Added voice_mode to users")

    if 'last_access' not in users_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN last_access TIMESTAMP")
        print("✓ Added last_access to users")

    # Check existing columns in sessions
    cursor.execute("PRAGMA table_info(sessions)")
    sessions_columns = [col[1] for col in cursor.fetchall()]

    if 'updated_at' not in sessions_columns:
        cursor.execute("ALTER TABLE sessions ADD COLUMN updated_at TIMESTAMP")
        print("✓ Added updated_at to sessions")

    conn.commit()
    conn.close()
    print(f"\n✓ Migration completed: {db_path}")

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/bot.db"
    migrate(db_path)
