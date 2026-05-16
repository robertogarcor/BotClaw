# BotClaw

Bot de Telegram que proporciona acceso completo a las capacidades de OpenCode CLI.

## Estado

**Versión:** 0.4.0 - Totalmente funcional

## Descripción

BotClaw permite a los usuarios interactuar con OpenCode desde Telegram como si lo estuvieran usando localmente. Cada usuario tiene su propia sesión y directorio de trabajo.

## Características

- Multi-tenant: Cada usuario de Telegram tiene sesión independiente
- Compatible con API de OpenCode v1.14.41
- Persistencia en SQLite para usuarios y sesiones
- Arquitectura extensible para futuros servidores de IA

## Requisitos

- Python 3.11+
- OpenCode CLI instalado (`opencode serve`)
- Token de Bot de Telegram (de @BotFather)

## Configuración

1. **Crear entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar entorno:**
   ```bash
   cp config/.env.example config/.env
   # Editar .env con tus credenciales
   ```

4. **Iniciar servidor de OpenCode:**
   ```bash
   opencode serve --port 4097
   ```

5. **Ejecutar el bot:**
   ```bash
   python -m bot.main
   ```

## Comandos

| Comando | Descripción |
|---------|-------------|
| /start | Registrarse y obtener mensaje de bienvenida |
| /help | Mostrar ayuda |
| /init <path> | Establecer tu directorio de trabajo |
| /create <name o path> | Crear nuevo directorio de proyecto |
| /clone <url> | Clonar un repositorio git |
| /new | Iniciar una nueva sesión de OpenCode |
| /project | Mostrar proyecto actual |
| /projects | Listar todos los proyectos |
| /status | Mostrar información del proyecto actual |
| /sessions [path] | Listar sesiones disponibles de OpenCode |
| /use <id> | Seleccionar sesión por ID |
| /last | Usar última sesión |
| /mcp | Mostrar servidores MCP disponibles |
| /skills | Mostrar skills del proyecto |
| /voice on/off/status | Activar/desactivar respuestas de voz |
| /cancel | Cancelar operación actual |

## Configuración

Editar `config/.env`:

```
TELEGRAM_BOT_TOKEN=tu_token_aqui
OPENCODE_SERVER_URL=http://localhost:4097
OPENCODE_SERVER_PASSWORD=opcional
USERS_ALLOWED=user1,user2
USER_IDS_ALLOWED=123456789,987654321
TTS_VOICE=es-MX-DaliaNeural
PROJECTS_BASE_DIR=~/projects
LOG_LEVEL=INFO
```

## Arquitectura

```
Usuarios de Telegram → BotClaw → Servidor de OpenCode (HTTP)
                              ↓
                      SQLite (users + sessions)
```

## Licencia

MIT