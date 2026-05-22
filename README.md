# BotClaw

Bot de Telegram que proporciona acceso completo a las capacidades de OpenCode CLI.

## Estado

**Versión:** 0.5.0 - Totalmente funcional

## Descripción

BotClaw permite a los usuarios interactuar con OpenCode desde Telegram como si lo estuvieran usando localmente. Cada usuario tiene su propia sesión y directorio de trabajo.

## Características

- Multi-tenant: Cada usuario de Telegram tiene sesión independiente
- Compatible con API de OpenCode v1.14.41+
- Persistencia en SQLite para usuarios y sesiones
- Arquitectura extensible para futuros servidores de IA
- Voz: STT (faster-whisper) + TTS (edge-tts + ffmpeg)
- Creación de proyectos con templates de contexto automáticos

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

### Base
| Comando | Descripción |
|---------|-------------|
| `/start` | Registrarse y obtener mensaje de bienvenida |
| `/help` | Mostrar lista completa de comandos disponibles |
| `/cancel` | Cancelar operación en curso |

### Proyecto
| Comando | Descripción |
|---------|-------------|
| `/init <path>` | Inicializar o cambiar a un proyecto existente. Crea sesión si no existe |
| `/create <name\|path>` | Crear nuevo proyecto: directorio, git init, templates de contexto y sesión |
| `/clone <url>` | Clonar repositorio git e inicializar automáticamente. Soporta HTTPS y SSH |
| `/project` | Mostrar información del proyecto actual (path, sesión, git) |
| `/projects` | Listar todos los proyectos registrados y sesiones globales |

### Sesión
| Comando | Descripción |
|---------|-------------|
| `/new` | Crear una nueva sesión de OpenCode para el proyecto actual |
| `/sessions [path]` | Listar sesiones disponibles (del proyecto actual o de un path específico) |
| `/use <id>` | Seleccionar una sesión existente por su ID |
| `/last` | Usar automáticamente la sesión más reciente del proyecto activo |
| `/rename <titulo>` | Cambiar el título de la sesión actual |

### Información
| Comando | Descripción |
|---------|-------------|
| `/status` | Mostrar estado completo: proyecto, sesión, modelo, agente, modo, git, voz |
| `/mode` | Alternar modo del agente entre `build` y `plan` |
| `/mcp` | Listar servidores MCP conectados y su estado |
| `/skills` | Mostrar skills disponibles en el directorio `.agents/skills` del proyecto |

### Voz
| Comando | Descripción |
|---------|-------------|
| `/voice on` | Activar respuestas de voz (TTS) |
| `/voice off` | Desactivar respuestas de voz |
| `/voice status` | Mostrar estado actual del modo de voz |

## Context Files

Al crear un proyecto con `/create`, se generan automáticamente los siguientes archivos de contexto:

| Archivo | Propósito |
|---------|-----------|
| `AGENTS.md` | Instrucciones para el agente + referencia a otros archivos de contexto |
| `PRODUCT.md` | Visión del producto, reglas de negocio y experiencia de usuario |
| `ARCHITECTURE.md` | Arquitectura técnica, estructura y estándares de código |
| `SPEC.md` | Especificación de la tarea actual (dinámico, se limpia tras cada tarea) |
| `HISTORY.md` | Historial de trabajo completado (acumulativo, nunca se borra) |

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

## Testing

```bash
.venv/bin/python3 -m pytest tests/ -v
```

## Licencia

MIT
