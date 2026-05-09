# BotClaw - Technical Specification

## 1. Overview

**Project Name:** BotClaw
**Type:** Telegram Bot / CLI Wrapper
**Core Functionality:** A Telegram client that provides full access to OpenCode CLI capabilities, enabling users to interact with OpenCode as if using it locally.
**Target Users:** Developers who want to use OpenCode from their mobile devices via Telegram.

## 2. Architecture

```
┌─────────────────────┐      ┌─────────────────────┐
│   Telegram Users    │─────►│   Bot Telegram      │
│   (multi-tenant)   │◄──── │   (webhook/polling) │
└─────────────────────┘      └─────────┬───────────┘
                                       │
                   ┌───────────────────┼───────────────────┐
                   │                   │                   │
                   ▼                   ▼                   ▼
            ┌────────────┐     ┌────────────┐     ┌────────────┐
            │ Session A  │     │ Session B  │     │ Session N  │
            │ (user A)   │     │ (user B)   │     │ (user N)   │
            └────────────┘     └────────────┘     └────────────┘
                   │                   │                   │
                   └───────────────────┼───────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  opencode serve     │
                            │  (HTTP API :4096)   │
                            └─────────────────────┘
```

## 3. Components

### 3.1 Bot Layer (Telegram)

- **Framework:** python-telegram-bot
- **Mode:** Webhook (production) or Polling (development)
- **Handlers:** Commands, Messages, Callbacks

### 3.2 Service Layer

| Service | Responsibility |
|---------|----------------|
| `OpenCodeClient` | HTTP client for OpenCode API |
| `SessionManager` | Create/manage sessions per user |
| `UserManager` | User registration and config |

### 3.3 Data Layer

- **Database:** SQLite (bot.db)
- **Tables:** users, sessions

## 4. API Integration

### OpenCode Server Endpoints

| Method | Endpoint | Usage |
|--------|----------|-------|
| POST | /sessions | Create new session |
| GET | /sessions/{id} | Get session info |
| POST | /tui/submit-prompt | Send message to agent |
| GET | /tui/control/next | Get agent questions |
| POST | /tui/control/response | Answer agent questions |
| POST | /tui/execute-command | Run /init, /undo, etc |

### Session Management

- **chat_id → session_id** mapping stored in SQLite
- Each user has independent session with own working directory
- Sessions persist until explicitly closed or reset

## 5. User Flow

```
1. /start → Bot registers user, creates empty session
2. /init /path → User sets working directory
3. Message → Bot sends to OpenCode, receives response
4. Agent question → Bot forwards to user, sends answer back
5. /new → Creates fresh session, keeps same directory
```

## 6. Configuration

Environment variables (`.env`):

```
TELEGRAM_BOT_TOKEN=xxx
OPENCODE_SERVER_URL=http://localhost:4096
OPENCODE_SERVER_PASSWORD=optional
USERS_ALLOWED=user1,user2  # Empty = allow all
LOG_LEVEL=INFO
```

## 7. Commands

| Command | Args | Description |
|---------|------|-------------|
| /start | - | Register and show welcome |
| /help | - | Show help message |
| /init | `<path>` | Set working directory |
| /clone | `<url>` | Clone git repo |
| /new | - | New session |
| /status | - | Show current project |

## 8. Error Handling

- **Connection errors:** Retry 3 times, then notify user
- **Timeout:** 60s max for responses, send "processing" message
- **Invalid path:** Show clear error, suggest fixes
- **Session lost:** Auto-recreate, notify user

## 9. File Structure

```
BotClaw/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── messages.py
│   │   └── callbacks.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── opencode_client.py
│   │   ├── session_manager.py
│   │   └── user_manager.py
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       └── session.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── .env.example
├── data/
│   └── bot.db
├── tests/
│   └── ...
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── SPEC.md
└── AGENTS.md
```

## 10. Dependencies

```
python-telegram-bot>=20.0
requests>=2.28.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
```

## 11. Future Enhancements

- Saved projects list (/projects, /proyecto 1)
- Interactive buttons menu
- Admin panel
- Metrics and logging
- MCP server configuration
- Group chat support