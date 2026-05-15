# BotClaw - Especificación Técnica

## 1. Visión General

**Nombre del Proyecto:** BotClaw
**Tipo:** Bot de Telegram / Wrapper de CLI
**Funcionalidad Principal:** Cliente de Telegram que proporciona acceso completo a las capacidades de OpenCode CLI, permitiendo a los usuarios interactuar con OpenCode como si lo usaran localmente.
**Usuarios Objetivo:** Desarrolladores que quieren usar OpenCode desde sus dispositivos móviles a través de Telegram.

## 2. Arquitectura

```
┌─────────────────────┐      ┌─────────────────────┐
│   Usuarios de        │─────►│   Bot de Telegram   │
│   Telegram           │◄──── │   (webhook/polling) │
│   (multi-tenant)    │      └─────────┬───────────┘
└─────────────────────┘                │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌────────────┐     ┌────────────┐     ┌────────────┐
             │ Sesión A   │     │ Sesión B   │     │ Sesión N   │
             │ (usuario A)│     │ (usuario B)│     │ (usuario N)│
             └────────────┘     └────────────┘     └────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
                             ┌─────────────────────┐
                             │   opencode serve     │
                             │   (HTTP API :4097)   │
                             └─────────────────────┘
```

## 3. Componentes

### 3.1 Capa de Bot (Telegram)

- **Framework:** python-telegram-bot
- **Modo:** Webhook (producción) o Polling (desarrollo)
- **Handlers:** Comandos, Mensajes, Callbacks, Voz

### 3.2 Capa de Servicios

| Servicio | Responsabilidad |
|----------|-----------------|
| `OpenCodeClient` | Cliente HTTP para la API de OpenCode |
| `SessionManager` | Crear/gestionar sesiones por usuario |
| `UserManager` | Registro y configuración de usuarios |
| `TTS` | Síntesis de voz con edge-tts |
| `STT` | Reconocimiento de voz con faster-whisper |

### 3.3 Capa de Datos

- **Base de datos:** SQLite (bot.db)
- **Tablas:** users, sessions

## 4. Requisitos del Sistema

- Python 3.11+
- ffmpeg (para convertir audio a formato Opus)
- Virtual environment recomendado

## 5. Dependencias

### Dependencias de Python

```
python-telegram-bot>=20.0
requests>=2.28.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
edge-tts
faster-whisper
```

## 6. Característica de Voz

### STT (Speech to Text)

- **Tecnología:** faster-whisper (reconocimiento local, sin API key)
- **Uso:** El usuario puede enviar mensajes de voz desde Telegram

### TTS (Text to Speech)

- **Tecnología:** edge-tts + ffmpeg
- **Voz por defecto:** es-MX-DaliaNeural
- **Conversión:** Se convierte a formato Opus para compatibilidad con Telegram
- **Activación:** Comando `/voice on` para respuestas en voz

### Flujo de Voz

1. Usuario envía nota de voz → Bot transcribe con faster-whisper
2. Usuario con voz activada (/voice on) → Bot responde con audio generado

## 7. Integración con API

**Documentación de la API:** https://opencode.ai/docs/server/

### Endpoints del Servidor de OpenCode (API v1.14.41)

| Método | Endpoint | Uso |
|--------|----------|-----|
| GET | /session | Listar sesiones (devuelve 0 si CLI abierta) |
| POST | /session | Crear nueva sesión |
| GET | /session?directory=/path | **Filtrar sesiones por directorio** |
| GET | /session/{id} | Obtener detalles de sesión |
| POST | /session/{id}/message | Enviar mensaje al agente |
| POST | /session/{id}/control | Responder preguntas del agente |
| GET | /project | Listar proyectos |
| GET | /mcp | Listar servidores MCP |
| GET | /global/health | Estado del servidor |

### Gestión de Sesiones

- **Filtrar por directorio:** Usar `/session?directory=/path/to/project` para obtener sesiones de un proyecto específico
- **chat_id → session_id** almacenado en SQLite
- Cada usuario tiene sesión independiente con su propio directorio de trabajo
- Las sesiones persisten hasta que se cierran o reinician explícitamente

## 8. Flujo de Usuario

```
1. /start → El bot registra al usuario, crea sesión vacía
2. /init /path → El usuario establece el directorio de trabajo
3. Mensaje → El bot envía a OpenCode, recibe respuesta
4. Pregunta del agente → El bot forwardea al usuario, envía la respuesta
5. /new → Crea sesión nueva, mantiene el mismo directorio
```

## 9. Configuración

Variables de entorno (`.env`):

```
TELEGRAM_BOT_TOKEN=xxx
OPENCODE_SERVER_URL=http://localhost:4097
OPENCODE_SERVER_PASSWORD=opcional
USERS_ALLOWED=user1,user2  # Vacío = permitir todos
LOG_LEVEL=INFO
```

## 10. Comandos

| Comando | Argumentos | Descripción |
|---------|------------|-------------|
| /start | - | Registro y bienvenida |
| /help | - | Mensaje de ayuda |
| /init | `<path>` | Establecer directorio de trabajo |
| /project | - | Mostrar proyecto actual |
| /projects | - | Listar todos los proyectos (desde API) |
| /clone | `<url>` | Clonar repositorio git |
| /new | - | Nueva sesión |
| /sessions | `[path]` | Listar sesiones del proyecto actual o de una ruta específica |
| /use | `<id>` | Seleccionar sesión por ID |
| /last | - | Usar última sesión |
| /status | - | Mostrar estado completo |
| /mcp | - | Mostrar configuración MCP |
| /skills | - | Mostrar skills del proyecto |
| /voice | `[on/off/status]` | Control de modo voz |
| /cancel | - | Cancelar operación |

## 11. Manejo de Errores

- **Errores de conexión:** Reintentar 3 veces, luego notificar al usuario
- **Timeout:** Máximo 60s para respuestas, enviar mensaje "processing"
- **Ruta inválida:** Mostrar error claro, sugerir correcciones
- **Sesión perdida:** Recrear automáticamente, notificar al usuario
- **Excepciones en await:** Todas las llamadas await a API, BD u operaciones externas deben tener try/except. Esto incluye:
  - `server.send_prompt()` - llamadas a API de OpenCode
  - `server.get_session_details()` - consultas a la API
  - `session_manager.save_session()` - operaciones de BD
  - `user_manager.get_user()` - consultas de usuarios
  - Loguear el tipo de excepción y mensaje para debugging
  - Notificar al usuario de errores de forma clara

## 12. Mejoras Futuras

- Menú con botones interactivos
- Panel de administración
- Métricas y logging
- Configuración de servidor MCP
- Soporte para chats de grupo