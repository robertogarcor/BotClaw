# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-05-08

### Fixed
- OpenCode API v1.14.41 compatibility (endpoints changed from plural to singular)
  - /sessions → /session
  - /tui/submit-prompt → /session/:id/message
  - Body format: {"parts": [{"type": "text", "text": prompt}]}
- Timeout issues increased to 30s
- Multiple connection and JSON decode errors
- Fixed .env path loading in settings.py

### Added
- Engram persistent memory integration documented in AGENTS.md
- Logging throughout the OpenCode server client
- Better error handling and messages

### Changed
- Bot now fully functional with OpenCode server
- Users can interact with OpenCode from Telegram

## [0.3.1] - 2026-05-08

### Added
- Support for user_id filtering in addition to username
- USER_IDS_ALLOWED config option in settings.py
- Updated .env.example with USER_IDS_ALLOWED

## [0.3.0] - 2026-05-08

### Added
- Core bot implementation complete
- bot/config/settings.py - Configuration module
- bot/models/user.py - User data model
- bot/models/session.py - Session data model
- bot/servers/base.py - Abstract base class for AI servers
- bot/servers/factory.py - Factory for creating server instances
- bot/servers/opencode.py - OpenCode server implementation
- bot/services/user_manager.py - User management with SQLite
- bot/services/session_manager.py - Session management with SQLite
- bot/handlers/commands.py - Command handlers (/start, /help, /init, etc)
- bot/handlers/messages.py - Message handler for prompts
- bot/handlers/callbacks.py - Callback query handler
- bot/main.py - Bot entry point

### Architecture
- Extensible server architecture (BaseServer → OpenCode → future servers)
- Multi-tenant: each Telegram user has own session and working directory
- SQLite database for users and sessions persistence
- Async-ready design with clean separation of concerns

## [0.2.0] - 2026-05-08

### Added
- Python virtual environment (.venv/)
- Dependencies installed (python-telegram-bot, requests, python-dotenv, sqlalchemy)
- config/.env.example - Configuration template
- config/.env - Runtime configuration file
- Git initialized with initial commit

## [0.1.0] - 2026-05-08

### Added
- Initial project structure
- AGENTS.md with agent instructions
- SPEC.md with technical specification
- README.md with setup instructions
- requirements.txt with dependencies
- .gitignore file

### Project Structure
- bot/ directory with main.py and handlers/
- services/ for OpenCode client, session and user managers
- models/ for database models
- config/ for settings and environment variables

### Commands Planned
- /start, /help, /init, /clone, /cd, /new, /status

## [0.0.0] - 2026-05-03

### Added
- Project conception and planning
- Viability analysis session