# BotClaw - Agent Instructions

## ⚠️ START HERE: Memory Check

1. Call `mem_context` - Get recent session context
2. Call `mem_search` with keywords related to your task - Check for prior work

## Project Overview

Telegram bot that interfaces with OpenCode CLI. Each Telegram user has their own session and working directory (multi-tenant).

## Tech Stack

- Python 3.x + virtual environment
- python-telegram-bot
- SQLite (users + sessions tables)
- `opencode serve` on port **4097** (not 4096)

## Key Architecture

- `bot/handlers/` - commands.py, messages.py, voice.py, callbacks.py
- `bot/services/` - session_manager.py, user_manager.py, tts.py, stt.py
- `bot/servers/` - opencode.py (API v1.14.41)

## Commands

| Command | Description |
|---------|-------------|
| `/init <path>` | Set working directory |
| `/project` | Show current project |
| `/clone <url>` | Clone git repo |
| `/new` | Start new session |
| `/sessions` | List sessions for current project |
| `/use <id>` | Select session by ID |
| `/last` | Use last session |
| `/skills` | Show project skills |
| `/voice [on/off/status]` | Toggle voice responses |
| `/status` | Show status with project, git, voice mode |
| `/start`, `/help`, `/mcp` | Standard commands |

## Project Context in Messages

When user sends a message, the bot prefixes it with `[Proyecto: <name>]` so the agent knows the active project.

## Voice Feature

- STT: faster-whisper (local, no API key)
- TTS: edge-tts + ffmpeg (convert to Opus for Telegram)
- Voice mode stored in SQLite (`voice_mode` column)

**TTS**: Use `text.strip()` + voice `es-MX-DaliaNeural`

## Common Issues

- "Connection refused" on port 4096 → server runs on 4097
- TTS returns empty file → use `text.strip()` + es-MX-DaliaNeural voice

## Engram Memory Protocol

- Start: `mem_context` + `mem_search`
- After bug fix or significant work: `mem_save`
- End session: `mem_session_summary`

## Testing

```bash
pytest tests/ -v
```