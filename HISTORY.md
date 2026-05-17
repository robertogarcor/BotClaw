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
**Estado:** ✅ Completado (2026-05-17)

---

### 28. Comando `/rename` para cambiar título de sesión
**Descripción:** Crear comando `/rename <nuevo_titulo>` que permita cambiar el título de la sesión actual de OpenCode.

**Implementación:**
- Usar PATCH `/session/{session_id}` con body `{"title": "nuevo_titulo"}`
- Validar que hay sesión activa
- Enviar confirmación con nuevo título
- Actualizar `/help` con el nuevo comando

**Archivos:** bot/handlers/command_sessions.py, bot/servers/opencode.py, bot/handlers/command_base.py

**Estado:** ⏳ Pendiente

---

### 29. Fix: `get_current_path()` no devuelve el proyecto activo correcto
**Descripción:** `get_current_path()` usa `ORDER BY last_access DESC` para determinar el proyecto activo. Pero `last_access` se rellena con el `updated_at` de la API de OpenCode (puede ser antiguo), no con el momento real de la interacción del usuario. Esto hace que `/sessions` sin argumentos muestre sesiones del proyecto equivocado.

**Ejemplo del bug:**
1. `/init BotClaw` → last_access = 22:41 (reciente en API)
2. `/init agent-kit` → last_access = 11:53 (antiguo en API)
3. `/sessions` → muestra BotClaw porque tiene last_access más reciente

**Implementación:**
- Añadir columna `is_active INTEGER DEFAULT 0` a tabla `sessions`
- Crear método `set_active_path(chat_id, path)` que:
  - `UPDATE sessions SET is_active=0 WHERE chat_id=?`
  - `UPDATE sessions SET is_active=1 WHERE chat_id=? AND path=?`
- `get_current_path()` cambia a `SELECT path WHERE chat_id=? AND is_active=1`
- `init_project()` llama a `set_active_path()` tras guardar sesión
- Mantener `last_access` para mostrar fechas en `/status` (no eliminar)

**Archivos:** bot/services/session_manager.py - `_init_db()`, `save_session()`, `get_current_path()`, nuevo `set_active_path()`, `init_project()`

**Estado:** ✅ Completado (2026-05-17)

---

### 30. Mejorar mensaje de `/init` indicando si se creó sesión nueva o existente
**Descripción:** `/init` siempre muestra el mismo mensaje ("configurado") tanto si reutiliza una sesión existente como si crea una nueva. El usuario debe saber si se creó una sesión nueva o se reutilizó una existente.

**Implementación:**
- En `command_project.py`, `init_command()` ya recibe `is_new` de `init_project()`
- Si `is_new=True` → añadir mensaje "🆕 Nueva sesión creada"
- Si `is_new=False` → añadir mensaje "🔄 Sesión existente reutilizada"
- Diferenciar visualmente ambos casos en el mensaje al usuario

**Archivos:** bot/handlers/command_project.py - init_command()

**Estado:** ⏳ Pendiente

---

### 31. Investigar por qué `/create` no registra proyecto en la tabla `project` de OpenCode
**Descripción:** Al crear un proyecto nuevo con `/create`, la sesión se crea correctamente pero con `projectID="global"`. No aparece en `GET /project` ni en `/projects` del bot. OpenCode solo registra proyectos en la tabla `project` cuando se abren desde el TUI, no vía API.

**Hallazgos actuales:**
- BotClaw y agent-kit tienen `projectID` específico (se abrieron desde TUI)
- testprueba tiene `projectID="global"` (solo creado vía API)
- Tener `.git` no es suficiente, el TUI debe inicializarlo

**Opciones a evaluar:**
1. `/create` hace `git init` automáticamente al crear directorio
2. `/projects` también incluye sesiones con `projectID="global"` que tengan directorio propio
3. Investigar si la API tiene otro endpoint para registrar proyectos

**Archivos:** bot/handlers/command_project.py, bot/handlers/command_info.py

**Estado:** ⏳ Pendiente

---

### 32. Unificar formato de mensajes en comandos
**Descripción:** Los comandos usan labels y formatos inconsistentes. Unificar:

- `Dir:` → `Path:` en todos los comandos
- `Session: \`id\`` siempre seleccionable
- `Path: \`ruta\`` siempre seleccionable
- `/use`: añadir Session ID al mensaje
- `/last`: añadir Title, cambiar `ID:` → `Session:`

**Archivos:** command_sessions.py, command_project.py, command_info.py

**Estado:** ⏳ Pendiente

---

### 34. `/last` siempre muestra la sesión más reciente del proyecto activo
**Descripción:** `/last` actualmente respeta la sesión configurada con `/use`. Debe cambiar para siempre mostrar la sesión más reciente del proyecto activo, ignorando `/use`.

**Implementación:**
- Eliminar rama de `continue_session(saved_session)` en `last_command()`
- Usar `get_sessions_from_api(path)` + ordenar por `time.updated DESC`
- Tomar la primera sesión (más reciente)
- Unificar mensaje de respuesta

**Archivos:** bot/handlers/command_sessions.py - last_command()

**Estado:** ✅ Completado (2026-05-17)

---

## Notas Técnicas

- Puerto de OpenCode: **4097** (no 4096)
- TTS fix: usar `text.strip()` + voz `es-MX-DaliaNeural`
- Arquitectura: Bot = puente, LLM tiene contexto de sesión
- Al hacer /init → cargar sesión más reciente del proyecto (no crear nueva)