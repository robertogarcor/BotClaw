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

- `bot/handlers/` - commands.py, messages.py, voice.py
- `bot/services/` - session_manager.py, user_manager.py, tts.py, stt.py
- `bot/servers/` - opencode.py (API v1.14.41)

## Voice Feature

- STT: faster-whisper (local, no API key)
- TTS: edge-tts + ffmpeg (convert to Opus for Telegram)
- Voice mode stored in SQLite (`voice_mode` column), NOT in memory

**TTS bug fix**: Always use `text.strip()` before edge-tts, voice `es-MX-DaliaNeural` (not es-ES-ElenaNeural)

## Commands

| Command | Description |
|---------|-------------|
| `/init <path>` | Set working directory (auto-loads AGENTS.md + SPEC.md into session) |
| `/clone <url>` | Clone git repo |
| `/new` | Start new session |
| `/sessions` | List TUI sessions |
| `/voice [on/off/status]` | Toggle voice responses |
| `/start`, `/help`, `/status`, `/mcp` | Standard commands |



## Common Issues

- "Connection refused" on port 4096 → server runs on 4097, check config/.env
- Voice mode not persisting → voice_mode saved in SQLite, not memory (fixed)
- TTS returns empty file → use `text.strip()` + es-MX-DaliaNeural voice

## Engram Memory Protocol

- Start: `mem_context` + `mem_search`
- After bug fix or significant work: `mem_save`
- End session: `mem_session_summary`

## Testing

```bash
pytest tests/ -v
```