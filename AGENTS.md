# BotClaw - Agent Instructions

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
│   ├── handlers/
│   │   ├── commands.py
│   │   ├── messages.py
│   │   └── callbacks.py
│   ├── services/
│   │   ├── opencode_client.py
│   │   ├── session_manager.py
│   │   └── user_manager.py
│   └── models/
│       ├── user.py
│       └── session.py
├── config/
│   ├── settings.py
│   └── .env.example
├── data/
├── tests/
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── SPEC.md
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
| `/cd <path>` | Change working directory |
| `/new` | Start new OpenCode session |
| `/status` | Show current project and session info |

### OpenCode Integration

- Use `opencode serve` as the backend HTTP server
- Each user gets their own session via `/sessions` API
- Handle control requests (questions from agent) via `/tui/control/next`
- Map chat_id to session_id for session persistence

### Testing

- Write unit tests for core services
- Use pytest as test framework
- Mock external dependencies (Telegram API, OpenCode server)

### Documentation

- Keep README.md updated with setup instructions
- Document all new commands in help message
- Update CHANGELOG.md for each release