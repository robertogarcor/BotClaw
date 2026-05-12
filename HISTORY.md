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

### 7. Mejorar formato /sessions y unificar fuentes de datos
**Descripción:** 
1. Añadir label "Session:" antes del ID en /sessions ✅
2. Unificar fuentes de datos:
   - `/init`: muestra datos de API (fuente de verdad) ✅
   - `/status`: usa BD local (sincronizada con API en /init) ✅
   - `/sessions`: consulta API directamente ✅
3. Entender el concepto de "last access" en el flujo

**Fuentes de datos:**
- API = fuente de verdad para sesiones
- BD local = cache que se actualiza en /init path en /init path

**Archivos modificados:**
- `bot/handlers/commands.py` - sessions_command() - añadido label "Session:"
- `bot/services/session_manager.py` - save_session() ahora acepta updated_at de API

**Pendiente:** Entender "last access" en el flujo completo

**Estado:** ⏳ En progreso

---

### 1. Cargar sesión reciente al cambiar de proyecto
**Descripción:** Al hacer /init a un proyecto diferente, buscar la sesión más reciente de ese proyecto en la API y usarla (en lugar de crear una nueva o reutilizar la anterior).

**Archivos involucrados:**
- `bot/services/session_manager.py`
- `bot/handlers/commands.py`

**Estado:** ⏳ Pendiente

---

### 2. Mostrar fecha de sesión
**Descripción:** Añadir fecha de creación/actualización de la sesión en los comandos /status y /sessions.

**Implementación:**
- /init: muestra Session, Title, Created, Last access (de API, formato DD-MM-YYYY HH:MM)
- /status: muestra Session, Title, Created, Last access (de BD local, sincronizada con API)
- /sessions: muestra Created y Last access (de API directamente)
- Fechas no seleccionables, Session y Title seleccionables
- /init y /status ahora muestran fechas consistentes (sincronizadas desde API)

**Archivos involucrados:**
- `bot/handlers/commands.py` - init_command(), status_command(), sessions_command()
- `bot/services/session_manager.py` - save_session() ahora acepta updated_at de API
- `bot/models/session.py` - campo updated_at

**Bug fix:** created_at y updated_at ahora se preservan de la API (antes INSERT OR REPLACE los sobreescribía)

**Estado:** ✅ Completado (2026-05-12)

---

### 3. Import modules desde bot/
**Descripción:** Al ejecutar `python main.py` desde directorio bot/ falla con ModuleNotFoundError. El import `from bot.config.settings` no funciona porque Python no encuentra el paquete 'bot' desde dentro del directorio bot/.

**Solución implementada:** Usar try/except para imports relativos o absolutos según contexto.

**Estado:** ✅ Completado (2026-05-10)

---

### 5. Actualizar estructura de BD
**Descripción:** Añadir campos faltantes a las tablas de la BD: users (voice_mode, last_access), sessions (updated_at).

**Archivos modificados:**
- `bot/services/user_manager.py` - Añadidos métodos para voice_mode y last_access
- `bot/services/session_manager.py` - Añadido campo updated_at
- `bot/models/user.py` - Añadido campo last_access
- `scripts/migrate_db.py` - Script de migración para BD existente

**Estado:** ✅ Completado (2026-05-12)

---

### 6. Nueva estructura de BD simplificada
**Descripción:** Rediseñar la estructura de BD para separar users y sessions. Users solo tiene chat_id, username, voice_mode. Sessions tiene (chat_id, path) como PK.

**Cambios:**
- users: chat_id (PK), username, voice_mode
- sessions: (chat_id, path) como PK, session_id, created_at, updated_at, last_access
- Flujo /init: consultar API con ?directory=/path, guardar sesión en BD local
- El código de handlers actualizado para usar session_manager.get_current_path()

**Archivos modificados:**
- `bot/models/session.py` - Nuevo modelo con path
- `bot/models/user.py` - Simplificado
- `bot/services/session_manager.py` - Nueva estructura con métodos init_project, get_sessions_from_api, get_current_path
- `bot/services/user_manager.py` - Simplificado
- `bot/handlers/commands.py` - Actualizado init, status, project, skills, sessions
- `bot/handlers/messages.py` - Actualizado para usar session_manager
- `bot/handlers/callbacks.py` - Actualizado para usar save_session
- `scripts/migrate_to_new_schema.py` - Script de migración

**Estado:** ✅ Completado (2026-05-12)

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