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
**Descripción:** Al hacer /init a un proyecto diferente, buscar la sesión más reciente de ese proyecto en la API y usarla.

**Archivos involucrados:** bot/services/session_manager.py, bot/handlers/commands.py
**Estado:** ⏳ Pendiente

---

### 2. Mostrar fecha de sesión
**Descripción:** Añadir fecha de creación/actualización de la sesión en /status y /sessions. Sincronizar created_at y updated_at desde API.

**Implementación:** /init, /status y /sessions muestran fechas. Fechas no seleccionables. Fix: save_session() preserva created_at de API. Fix: usar get_session_details() en vez de send_prompt() para obtener model/agent.

**Archivos:** bot/handlers/commands.py, bot/services/session_manager.py
**Estado:** ✅ Completado (2026-05-14)

---

### 3. Import modules desde bot/
**Descripción:** ModuleNotFoundError al ejecutar python main.py desde directorio bot/. Solución: try/except para imports relativos/absolutos.
**Estado:** ✅ Completado (2026-05-10)

---

### 4. Mejorar flujo de mensajes al cambiar proyecto
**Descripción:** Al hacer /init, enviar contexto (AGENTS.md, SPEC.md) silenciosamente sin mostrar respuesta del agente.
**Archivos:** bot/handlers/commands.py, bot/handlers/messages.py
**Estado:** ⏳ Pendiente

---

### 5. Actualizar estructura de BD
**Descripción:** Añadir campos voice_mode, last_access a users; updated_at a sessions.
**Archivos:** user_manager.py, session_manager.py, models/user.py, scripts/migrate_db.py
**Estado:** ✅ Completado (2026-05-12)

---

### 6. Nueva estructura de BD simplificada
**Descripción:** Separar users y sessions. users: chat_id, username, voice_mode. sessions: (chat_id, path) PK, session_id, created_at, updated_at, last_access. Flujo /init: consultar API ?directory=/path.
**Estado:** ✅ Completado (2026-05-12)

---

### 7. Mejorar formato /sessions y unificar fuentes de datos
**Descripción:** Label "Session:" en /sessions, unificar fuentes (API fuente de verdad, BD cache actualizada en /init).

**Fuentes:** /init→API, /status→BD local, /sessions→API directa
**Archivos:** bot/handlers/commands.py, bot/services/session_manager.py
**Estado:** ✅ Completado (2026-05-14)

---

### 8. Corregir selectable fields en /status
**Descripción:** Quitar backticks de Model y Agent en /status (no deben ser seleccionables).

**Selectable:** Project, Dir, Session | **No selectable:** Title, Created, Last access, Model, Agent, Mode
**Archivos:** bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-14)

---

### 9. Añadir label "Session:" en /sessions
**Descripción:** Añadir label "Session:" antes del ID en formato: `• Session: \`ses_xxx\``
**Archivos:** bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-12)

---

### 10. Fix /status model/agent error
**Descripción:** /status mostraba "(error getting info)" para Model/Agent. Solución: usar get_session_details() en vez de send_prompt() para obtener info.
**Archivos:** bot/handlers/commands.py - status_command()
**Estado:** ✅ Completado (2026-05-14)

---

### 11. Obtener Mode en /status
**Descripción:** get_session_details() no devuelve el campo "mode". send_prompt() lo devuelve pero puede hacer timeout. Opciones: retry con timeout corto, o aceptar N/A.

**Estado:** ⏳ Pendiente

---

### 12. Lentitud en /init por carga de AGENTS.md y SPEC.md
**Descripción:** El comando /init es lento al cargar el contexto de AGENTS.md y SPEC.md. Posibles soluciones: cargar en background, cachear contenido, o enviar sin esperar respuesta del agente.

**Estado:** ⏳ Pendiente

---

### 13. Manejo de excepciones en await (API, BD)
**Descripción:** Todas las llamadas await a API, BD y operaciones externas deben tener try/except para capturar errores. Evita errores silenciosos y crashes del bot.

**Archivos a revisar:** commands.py, messages.py, session_manager.py, user_manager.py

**Estado:** ⏳ Pendiente

---

## Notas Técnicas

- Puerto de OpenCode: **4097** (no 4096)
- TTS fix: usar `text.strip()` + voz `es-MX-DaliaNeural`
- Arquitectura: Bot = puente, LLM tiene contexto de sesión
- Al hacer /init → cargar sesión más reciente del proyecto (no crear nueva)