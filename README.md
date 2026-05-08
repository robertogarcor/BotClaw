# BotClaw

Telegram bot that provides full access to OpenCode CLI capabilities.

## Description

BotClaw allows users to interact with OpenCode from Telegram as if they were using it locally. Each user has their own session and working directory.

## Requirements

- Python 3.11+
- OpenCode CLI installed (`opencode serve`)
- Telegram Bot Token (from @BotFather)

## Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp config/.env.example config/.env
   # Edit .env with your credentials
   ```

4. **Start OpenCode server:**
   ```bash
   opencode serve --port 4096
   ```

5. **Run the bot:**
   ```bash
   python -m bot.main
   ```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and get welcome message |
| `/help` | Show help |
| `/init <path>` | Set your working directory |
| `/clone <url>` | Clone a git repository |
| `/cd <path>` | Change working directory |
| `/new` | Start a new session |
| `/status` | Show current project info |

## Configuration

Edit `config/.env`:

```
TELEGRAM_BOT_TOKEN=your_token_here
OPENCODE_SERVER_URL=http://localhost:4096
OPENCODE_SERVER_PASSWORD=optional
LOG_LEVEL=INFO
```

## License

MIT