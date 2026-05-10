# BotClaw - Historial del Proyecto

## Tareas REALIZADAS

### Bot Core
- [x] Registro de usuarios con SQLite (tabla users)
- [x] Gestión de sesiones (crear, usar, listar, nueva)
- [x] Comandos implementados:
  - `/start` - Registro y bienvenida
  - `/help` - Ayuda
  - `/init <path>` - Establecer directorio de trabajo
  - `/project` - Mostrar proyecto actual
  - `/clone <url>` - Clonar repositorio git
  - `/new` - Nueva sesión
  - `/sessions` - Listar sesiones del proyecto
  - `/use <id>` - Seleccionar sesión por ID
  - `/last` - Usar última sesión
  - `/status` - Mostrar estado completo
  - `/mcp` - Mostrar configuración MCP
  - `/skills` - Mostrar skills del proyecto
  - `/voice [on/off/status]` - Control de voz
  - `/cancel` - Cancelar operación

### Integración OpenCode
- [x] API v1.14.41 (puerto 4097)
- [x] Enviar prompts al agente
- [x] Manejar preguntas de control (control_request)
- [x] Buscar sesiones por proyecto en la API

### Voz
- [x] STT: faster-whisper (reconocimiento local)
- [x] TTS: edge-tts + ffmpeg (convertir a Opus para Telegram)
- [x] Modo voz guardado en DB (voice_mode column)
- [x] Voz: es-MX-DaliaNeural ( voz )

### Mejoras de UX
- [x] Contexto de proyecto en mensajes ("[INFO] Proyecto activo: X | Directorio: Y")
- [x] Mostrar model/agent en /status
- [x] Mostrar skills en /project
- [x] /skills comando para listar skills del proyecto

### Documentación
- [x] README.md
- [x] SPEC.md (reorganizado)
- [x] AGENTS.md (simplificado)
- [x] HISTORY.md (nuevo)
- [x] CHANGELOG.md

---

## Tareas PENDIENTES

### 1. Cargar sesión reciente al cambiar de proyecto
**Descripción:** Al hacer /init a un proyecto diferente, buscar la sesión más reciente de ese proyecto en la API y usarla (en lugar de crear una nueva o reutilizar la anterior).

**Archivos involucrados:**
- `bot/services/session_manager.py`
- `bot/handlers/commands.py`

**Estado:** ⏳ Pendiente

---

### 2. Mostrar fecha de sesión
**Descripción:** Añadir fecha de creación/actualización de la sesión en los comandos /status y /sessions.

**Archivos involucrados:**
- `bot/handlers/commands.py`
- `bot/services/session_manager.py`

**Estado:** ⏳ Pendiente

---

### 3. Import modules desde bot/
**Descripción:** Al ejecutar `python main.py` desde directorio bot/ falla con ModuleNotFoundError. El import `from bot.config.settings` no funciona porque Python no encuentra el paquete 'bot' desde dentro del directorio bot/.

**Solución implementada:** Usar try/except para imports relativos o absolutos según contexto.

**Estado:** ✅ Completado (2026-05-10)

---

### 4. Mejorar flujo de mensajes al cambiar proyecto
**Descripción:** Al hacer /init, enviar el contexto (AGENTS.md, SPEC.md) silenciosamente sin mostrar la respuesta del agente. Solo mostrar la respuesta cuando el usuario hable.

**Archivos involucrados:**
- `bot/handlers/commands.py`
- `bot/handlers/messages.py`

**Estado:** ⏳ Pendiente

---

## Notas Técnicas

- Puerto de OpenCode: **4097** (no 4096)
- TTS fix: usar `text.strip()` + voz `es-MX-DaliaNeural`
- Arquitectura: Bot = puente, LLM tiene contexto de sesión
- Al hacer /init → cargar sesión más reciente del proyecto (no crear nueva)