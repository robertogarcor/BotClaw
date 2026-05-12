#!/usr/bin/env python3
"""
Migrate bot.db to new structure.

Old:
- users: chat_id, username, working_dir, voice_mode, created_at, last_access
- sessions: chat_id (PK), session_id, working_dir, created_at, updated_at

New:
- users: chat_id (PK), username, voice_mode, created_at
- sessions: (chat_id, path) as PK, session_id, created_at, updated_at, last_access
"""

import sqlite3
import sys
from pathlib import Path


def migrate(db_path: str) -> None:
    if not Path(db_path).exists():
        print(f"BD no existe: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tablas existentes: {tables}")

    cursor.execute("PRAGMA table_info(users)")
    users_cols = {row[1] for row in cursor.fetchall()}
    print(f"Columnas users: {users_cols}")

    cursor.execute("PRAGMA table_info(sessions)")
    sessions_cols = {row[1] for row in cursor.fetchall()}
    print(f"Columnas sessions: {sessions_cols}")

    print("\nMigrando users...")
    if 'last_access' in users_cols:
        cursor.execute("ALTER TABLE users DROP COLUMN last_access")
        print("  - Eliminado last_access de users")

    if 'working_dir' in users_cols:
        cursor.execute("ALTER TABLE users DROP COLUMN working_dir")
        print("  - Eliminado working_dir de users")

    print("\nMigrando sessions...")
    cursor.execute("DROP TABLE IF EXISTS sessions_new")
    cursor.execute("""
        CREATE TABLE sessions_new (
            chat_id INTEGER,
            path TEXT,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (chat_id, path)
        )
    """)
    print("  - Creada nueva tabla sessions")

    cursor.execute("SELECT chat_id, session_id, working_dir, created_at FROM sessions")
    old_sessions = cursor.fetchall()
    
    if old_sessions:
        cursor.executemany(
            "INSERT OR IGNORE INTO sessions_new (chat_id, path, session_id, created_at) VALUES (?, ?, ?, ?)",
            [(s[0], s[2], s[1], s[3]) for s in old_sessions if s[2]]
        )
        print(f"  - Migrados {len(old_sessions)} registros")
    
    cursor.execute("DROP TABLE sessions")
    cursor.execute("ALTER TABLE sessions_new RENAME TO sessions")
    print("  - Renombrada tabla sessions_new -> sessions")

    conn.commit()
    
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    for row in cursor:
        print(f"\n{row[0]}")
    
    conn.close()
    print(f"\n✓ Migración completada: {db_path}")


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/bot.db"
    migrate(db_path)
