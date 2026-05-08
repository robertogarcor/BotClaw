# BotClaw - Agent Instructions

## ⚠️ START HERE: Memory Check

**Before starting ANY work on this project, you MUST:**

1. Call `mem_context` - Get recent session context
2. Call `mem_search` with keywords related to your task - Check for prior work

This ensures you know what has been done and avoid duplicating work.

## Project Overview

BotClaw is a Telegram client that interfaces with OpenCode CLI, allowing users to interact with OpenCode from Telegram as if they were using it locally.

## Tech Stack

- **Language**: Python 3.x with virtual environment
- **Bot Framework**: python-telegram-bot
- **Database**: SQLite
- **Backend**: opencode serve (HTTP API)

## Working Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Keep functions small and focused (single responsibility)
- Use meaningful variable and function names

### Project Structure

```
BotClaw/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   └── settings.py
│   ├── handlers/
│   │   ├── commands.py
│   │   ├── messages.py
│   │   └── callbacks.py
│   ├── servers/
│   │   ├── base.py          # Abstract BaseServer
│   │   ├── factory.py       # ServerFactory
│   │   └── opencode.py      # OpenCode implementation
│   ├── services/
│   │   ├── session_manager.py
│   │   └── user_manager.py
│   └── models/
│       ├── user.py
│       └── session.py
├── config/
│   ├── settings.py
│   ├── .env.example
│   └── .env
├── data/
│   └── bot.db
├── tests/
│   └── (pytest tests)
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── SPEC.md
└── AGENTS.md
```

### Key Principles

1. **Multi-tenant**: Each Telegram user has their own session and working directory
2. **Async-first**: Use async/await for I/O operations
3. **Error handling**: Graceful degradation with meaningful error messages
4. **Configuration**: Use environment variables, never hardcode secrets

### Commands to Implement

| Command | Description |
|---------|-------------|
| `/start` | Register user, create initial session |
| `/help` | Show help message |
| `/init <path>` | Set user's working directory |
| `/clone <url>` | Clone git repo and set as project |
| `/cd <path>` | Change working directory (alias of /init) |
| `/new` | Start new OpenCode session |
| `/status` | Show current project and session info |
| `/sessions` | List available OpenCode sessions |
| `/mcp` | Show connected MCP servers |

### OpenCode Integration

- Use `opencode serve` as the backend HTTP server
- **API v1.14.41 endpoints:**
  - `POST /session` - Create new session
  - `POST /session/:id/message` - Send message (body: `{"parts": [{"type": "text", "text": "prompt"}]}`)
  - `GET /session` - List sessions
  - `GET /mcp` - List MCP servers
- Each user gets their own session via `/session` API
- Map chat_id to session_id for session persistence
- Two types of sessions: BotClaw SQLite (chat_id → session_id) vs OpenCode internal

### Testing

- Write unit tests for core services
- Use pytest as test framework
- Mock external dependencies (Telegram API, OpenCode server)

### Documentation

- Keep README.md updated with setup instructions
- Document all new commands in help message
- Update CHANGELOG.md for each release

## Engram Persistent Memory

This project uses Engram for persistent memory across sessions.

### ⚠️ ALWAYS CHECK MEMORY AT START

Before starting any work, you MUST:
1. Call `mem_context` - Get recent session context
2. Call `mem_search` with keywords related to your task - Check for prior work

This ensures you know what has been done and avoid duplicating work.

### Saving Observations (REQUIRED after significant work)

Call `mem_save` after:
- Bug fix completed
- Architecture or design decision made
- Non-obvious discovery about the codebase
- Configuration change or environment setup
- Pattern established (naming, structure, convention)

Format:
- **title**: Short, searchable (e.g., "Fixed session timeout issue")
- **type**: bugfix | decision | architecture | discovery | pattern | config
- **content**: **What**, **Why**, **Where**, **Learned**

### Checking Memory Proactively

When:
- Starting work on something that might have been done before
- User mentions a topic you have no context on
- First message references the project, a feature, or a problem

Call `mem_search` with keywords to check for prior work.

### Session End Protocol

Before ending session, call `mem_session_summary` with:
- Goal: What we were working on
- Instructions: User preferences discovered
- Discoveries: Technical findings
- Accomplished: Completed items
- Next Steps: What remains
- Relevant Files: Key files changed