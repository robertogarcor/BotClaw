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

**Implementación:** /init consulta la API con ?directory=/path, ordena por updated_at y usa la sesión más reciente. Si no hay sesiones, crea una nueva.

**Archivos involucrados:** bot/services/session_manager.py, bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-15)

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

**Implementación:**
- `commands.py`: Añadido try/except a new_command, use_command, last_command, mcp_command, sessions_command, init_command
- `session_manager.py`: Añadido try/except a init_project() (POST a API)
- `user_manager.py`: Añadido try/except a get_user, create_user, set_voice_mode (operaciones BD)
- Todos los except loguean `type(e).__name__: e` y notifican al usuario

**Archivos modificados:** commands.py, session_manager.py, user_manager.py

**Estado:** ✅ Completado (2026-05-15)

---

### 14. Fix: Escape de caracteres Markdown en títulos de sesión
**Descripción:** Error "Can't parse entities: can't find end of the entity" al usar /sessions o /init con rutas que contienen underscores (`_`). Los títulos de sesión como "BotClaw session for /home/administrador/Projects/BotClaw" contienen `_` que Telegram interpreta como inicio de cursiva en Markdown.

**Implementación:** Escapar caracteres `_`, `*`, `` ` ``, `[`, `]`, `(`, `)` en todos los títulos antes de enviar a Telegram.

**Archivos modificados:** bot/handlers/commands.py - sessions_command, status_command, use_command, last_command

**Estado:** ✅ Completado (2026-05-15)

---

### 15. Sincronizar fechas de BD local con API tras cada interacción
**Descripción:** La BD local se desactualiza respecto a la API porque cada interacción con el agente actualiza `updated_at` en la API pero no en la BD. `/status` lee de BD y muestra fechas viejas.

**Implementación:**
- Añadir `sync_session_dates_from_api()` en `session_manager.py` que consulta `get_session_details()` y actualiza BD
- Llamar a `sync_session_dates_from_api()` tras `send_prompt()` y `send_control_response()` en `messages.py`
- Llamar a `sync_session_dates_from_api()` en `sessions_command()` al listar sesiones

**Archivos:** bot/services/session_manager.py, bot/handlers/messages.py, bot/handlers/commands.py

**Estado:** ✅ Completado (2026-05-15)

---

### 16. /sessions sin path usa proyecto actual
**Descripción:** Actualmente `/sessions` requiere siempre un path. Añadir opción de usar `/sessions` sin argumentos para listar sesiones del proyecto activo (el del último `/init`).

**Implementación:**
- Si `/sessions` tiene argumentos → usar path proporcionado (comportamiento actual)
- Si `/sessions` sin argumentos → usar `session_manager.get_current_path(chat_id)`
- Si no hay path configurado → pedir que haga `/init` primero

**Archivos:** bot/handlers/commands.py - sessions_command()

**Estado:** ✅ Completado (2026-05-15)

---

### 17. Separar commands.py en módulos por secciones
**Descripción:** commands.py tiene +780 líneas con todos los handlers en un solo fichero. Separar en módulos más pequeños por tipo de funcionalidad para mejorar mantenibilidad.

**Estructura propuesta:**
```
bot/handlers/
├── command_base.py       ← start, help, cancel
├── command_project.py    ← init, project, projects, clone
├── command_sessions.py   ← sessions, use, last, new
├── command_info.py       ← status, mcp, skills
└── command_voice.py      ← voice_command
```

**Archivos:** bot/handlers/commands.py → command_base.py, command_project.py, command_sessions.py, command_info.py, command_voice.py

**Estado:** ✅ Completado (2026-05-15)

---

### 18. Fix: /last muestra session ID completo
**Descripción:** `/last` truncaba el session ID a 20 caracteres (`[:20]`). Mostrar ID completo con formato code para que sea seleccionable y copiable.

**Archivos:** bot/handlers/commands.py - last_command()

**Estado:** ✅ Completado (2026-05-15)

---

### 19. Revisar comando /clone
**Descripción:** Revisar el comando `/clone` para soportar clonar repositorios locales y remotos. Actualmente solo soporta URLs remotas de git. Eliminar uso de `set_working_dir` que ya no existe.

**Archivos:** bot/handlers/commands.py - clone_command()

**Estado:** ⏳ Pendiente

---

### 20. Comando /projects para listar todos los proyectos
**Descripción:** Crear nuevo comando `/projects` (plural) que liste todos los proyectos del usuario. El comando `/project` (singular) actual se mantiene para mostrar el proyecto activo.

**Implementación:**
- `/projects` → consulta API GET /project para obtener todos los proyectos (incluidos CLI)
- Filtra proyecto "global"
- Para cada proyecto, obtiene sesión más reciente via API
- Muestra nombre, path, sesión y último acceso
- Mantener `/project` como está (muestra proyecto actual)
- Actualizado /help con /projects

**Archivos:** bot/handlers/commands.py - projects_command()

**Estado:** ✅ Completado (2026-05-15)

---

### 21. Limpieza de BD y scripts obsoletos
**Descripción:** Tras la simplificación de la BD hay archivos que ya no valen:
- `bot/botclaw.db` → archivo vacío (0 bytes), eliminar
- `data/bot.db` → renombrar a `data/botclaw.db` (nombre más claro)
- `scripts/migrate_db.py` → migración antigua, eliminar
- `scripts/migrate_to_new_schema.py` → migración antigua, eliminar
- Actualizar `DATABASE_PATH` en `settings.py` a `data/botclaw.db`

**Archivos:** bot/botclaw.db (eliminar), data/bot.db → data/botclaw.db (renombrar), scripts/ (limpiar), bot/config/settings.py

**Estado:** ✅ Completado (2026-05-15)

---

### 22. Voz TTS configurable por variable de entorno
**Descripción:** La voz del TTS (`es-MX-DaliaNeural`) está hardcodeada. Hacerla configurable mediante variable de entorno `TTS_VOICE` para poder cambiarla fácilmente sin modificar código.

**Implementación:**
- Añadir `TTS_VOICE` a `settings.py` con valor por defecto `es-MX-DaliaNeural`
- Actualizar `bot/services/tts.py` para usar la variable de entorno
- Documentar en README.md y SPEC.md

**Archivos:** bot/config/settings.py, bot/services/tts.py, README.md, SPEC.md, config/.env.example

**Estado:** ✅ Completado (2026-05-15)

---

### 23. Comando /create para crear directorio y sesión
**Descripción:** Crear comando `/create <path>` que cree el directorio del proyecto (si no existe) e inicialice una nueva sesión de OpenCode para él.

**Implementación:**
- Crear directorio con `os.makedirs(path, exist_ok=True)`
- Llamar a `init_project()` para crear sesión
- Enviar mensaje de confirmación con path y session_id
- Similar a `/init` pero crea el directorio si no existe

**Archivos:** bot/handlers/commands.py - añadir create_command()

**Estado:** ⏳ Pendiente

---

## Notas Técnicas

- Puerto de OpenCode: **4097** (no 4096)
- TTS fix: usar `text.strip()` + voz `es-MX-DaliaNeural`
- Arquitectura: Bot = puente, LLM tiene contexto de sesión
- Al hacer /init → cargar sesión más reciente del proyecto (no crear nueva)