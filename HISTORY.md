# BotClaw - Historial del Proyecto

## Resumen del Proyecto

### Bot Core
- [x] Registro de usuarios con SQLite (tabla users)
- [x] Gestión de sesiones (crear, usar, listar, nueva)
- [x] Comandos implementados: `/start`, `/help`, `/init`, `/project`, `/projects`, `/create`, `/clone`, `/new`, `/sessions`, `/use`, `/last`, `/status`, `/mcp`, `/skills`, `/voice`, `/cancel`

### Integración OpenCode
- [x] API v1.14.41 (puerto 4097)
- [x] Enviar prompts al agente
- [x] Manejar preguntas de control (control_request)
- [x] Buscar sesiones por proyecto en la API

### Voz
- [x] STT: faster-whisper (reconocimiento local)
- [x] TTS: edge-tts + ffmpeg (convertir a Opus para Telegram)
- [x] Modo voz guardado en DB (voice_mode column)
- [x] Voz: es-MX-DaliaNeural

### Mejoras de UX
- [x] Contexto de proyecto en mensajes ("[INFO] Proyecto activo: X | Directorio: Y")
- [x] Mostrar model/agent en /status
- [x] Mostrar skills en /project
- [x] /skills comando para listar skills del proyecto

### Documentación
- [x] README.md, SPEC.md, AGENTS.md, HISTORY.md, CHANGELOG.md

---

## Tareas Completadas

### 1. Cargar sesión reciente al cambiar de proyecto
Al hacer /init a un proyecto diferente, buscar la sesión más reciente de ese proyecto en la API y usarla.
**Archivos:** bot/services/session_manager.py, bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-15)

---

### 2. Mostrar fecha de sesión
Añadir fecha de creación/actualización de la sesión en /status y /sessions. Sincronizar created_at y updated_at desde API.
**Archivos:** bot/handlers/commands.py, bot/services/session_manager.py
**Estado:** ✅ Completado (2026-05-14)

---

### 3. Import modules desde bot/
ModuleNotFoundError al ejecutar python main.py desde directorio bot/. Solución: try/except para imports relativos/absolutos.
**Estado:** ✅ Completado (2026-05-10)

---

### 4. Mejorar flujo de mensajes al cambiar proyecto
Al hacer /init, enviar contexto (AGENTS.md, SPEC.md) silenciosamente sin mostrar respuesta del agente.
**Archivos:** bot/handlers/commands.py, bot/handlers/messages.py
**Estado:** ✅ Completado (2026-05-17)

---

### 5. Actualizar estructura de BD
Añadir campos voice_mode, last_access a users; updated_at a sessions.
**Archivos:** user_manager.py, session_manager.py, models/user.py, scripts/migrate_db.py
**Estado:** ✅ Completado (2026-05-12)

---

### 6. Nueva estructura de BD simplificada
Separar users y sessions. users: chat_id, username, voice_mode. sessions: (chat_id, path) PK, session_id, created_at, updated_at, last_access.
**Estado:** ✅ Completado (2026-05-12)

---

### 7. Mejorar formato /sessions y unificar fuentes de datos
Label "Session:" en /sessions, unificar fuentes (API fuente de verdad, BD cache actualizada en /init).
**Archivos:** bot/handlers/commands.py, bot/services/session_manager.py
**Estado:** ✅ Completado (2026-05-14)

---

### 8. Corregir selectable fields en /status
Quitar backticks de Model y Agent en /status (no deben ser seleccionables).
**Archivos:** bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-14)

---

### 9. Añadir label "Session:" en /sessions
Añadir label "Session:" antes del ID en formato: `• Session: \`ses_xxx\``
**Archivos:** bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-12)

---

### 10. Fix /status model/agent error
/status mostraba "(error getting info)" para Model/Agent. Solución: usar get_session_details() en vez de send_prompt().
**Archivos:** bot/handlers/commands.py - status_command()
**Estado:** ✅ Completado (2026-05-14)

---

### 13. Manejo de excepciones en await
Todas las llamadas await a API, BD y operaciones externas deben tener try/except.
**Archivos modificados:** commands.py, session_manager.py, user_manager.py
**Estado:** ✅ Completado (2026-05-15)

---

### 14. Fix: Escape de caracteres Markdown en títulos de sesión
Error "Can't parse entities" al usar /sessions o /init con rutas que contienen underscores.
**Archivos modificados:** bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-15)

---

### 15. Sincronizar fechas de BD local con API tras cada interacción
Añadir sync_session_dates_from_api() en session_manager.py.
**Archivos:** bot/services/session_manager.py, bot/handlers/messages.py, bot/handlers/commands.py
**Estado:** ✅ Completado (2026-05-15)

---

### 16. /sessions sin path usa proyecto actual
/sessions sin argumentos lista sesiones del proyecto activo.
**Archivos:** bot/handlers/commands.py - sessions_command()
**Estado:** ✅ Completado (2026-05-15)

---

### 17. Separar commands.py en módulos por secciones
commands.py (+780 líneas) separado en command_base.py, command_project.py, command_sessions.py, command_info.py, command_voice.py.
**Archivos:** bot/handlers/commands.py → módulos
**Estado:** ✅ Completado (2026-05-15)

---

### 18. Fix: /last muestra session ID completo
/last truncaba el session ID a 20 caracteres. Mostrar ID completo.
**Archivos:** bot/handlers/commands.py - last_command()
**Estado:** ✅ Completado (2026-05-15)

---

### 20. Comando /projects para listar todos los proyectos
/projects consulta API GET /project para obtener todos los proyectos (incluidos CLI).
**Archivos:** bot/handlers/commands.py - projects_command()
**Estado:** ✅ Completado (2026-05-15)

---

### 21. Limpieza de BD y scripts obsoletos
Eliminar bot/botclaw.db (0 bytes), renombrar data/bot.db → data/botclaw.db, eliminar scripts de migración antiguos.
**Archivos:** bot/botclaw.db, data/bot.db, scripts/, bot/config/settings.py
**Estado:** ✅ Completado (2026-05-15)

---

### 22. Voz TTS configurable por variable de entorno
TTS_VOICE configurable en .env.
**Archivos:** bot/config/settings.py, bot/services/tts.py, README.md, SPEC.md
**Estado:** ✅ Completado (2026-05-15)

---

### 23. Comando /create para crear directorio y sesión
/create <name|path> crea directorio e inicializa sesión. PROJECTS_BASE_DIR configurable.
**Archivos:** bot/handlers/command_project.py - create_command()
**Estado:** ✅ Completado (2026-05-15)

---

### 24. Fix: Eliminar comandos duplicados en /help
/project y /status aparecían duplicados. Reorganizar secciones.
**Archivos:** bot/handlers/command_base.py - help_command()
**Estado:** ✅ Completado (2026-05-15)

---

### 25. Fix: init_project() no pasa directory como query parameter
init_project() ahora pasa ?directory=path al POST /session. Título: {nombre} - DD/MM/AAAA.
**Archivos:** bot/services/session_manager.py - init_project()
**Estado:** ✅ Completado (2026-05-16)

---

### 26. Fix: create_session() en opencode.py no pasa directory
create_session() ahora pasa ?directory=working_dir al POST /session.
**Archivos:** bot/servers/opencode.py - create_session()
**Estado:** ✅ Completado (2026-05-16)

---

### 27. Fix: Método create_session_with_dir() no existe
Crear método create_session_with_dir() que /new necesita.
**Archivos:** bot/services/session_manager.py, bot/handlers/command_sessions.py
**Estado:** ✅ Completado (2026-05-16)

---

### 29. Fix: get_current_path() no devuelve el proyecto activo correcto
Añadir columna is_active a sessions. get_current_path() usa WHERE is_active=1 en vez de ORDER BY last_access.
**Archivos:** bot/services/session_manager.py
**Estado:** ✅ Completado (2026-05-17)

---

### 30. Mejorar mensaje de /init indicando si se creó sesión nueva o existente
Añadir "🆕 Nueva sesión creada" o "🔄 Sesión existente reutilizada" según is_new.
**Archivos:** bot/handlers/command_project.py - init_command()
**Estado:** ✅ Completado (2026-05-17)

---

### 32. Unificar formato de mensajes en comandos
Dir: → Path: en todos los comandos. Session: `id` siempre seleccionable. Path: `ruta` siempre seleccionable.
**Archivos:** command_sessions.py, command_project.py, command_info.py, callbacks.py
**Estado:** ✅ Completado (2026-05-17)

---

### 34. /last siempre muestra la sesión más reciente del proyecto activo
Eliminar rama continue_session. Usar get_sessions_from_api(path) + ordenar por time.updated DESC.
**Archivos:** bot/handlers/command_sessions.py - last_command()
**Estado:** ✅ Completado (2026-05-17)

---

## Tareas Pendientes

### 11. Obtener Mode en /status
get_session_details() no devuelve el campo "mode". send_prompt() lo devuelve pero puede hacer timeout.
**Estado:** ⏳ Pendiente

---

### 12. Eliminar carga de contexto en /init
El LLM ya puede leer AGENTS.md/SPEC.md por su cuenta. Se eliminó la lógica de leer y enviar archivos al LLM en /init.
**Archivos:** bot/handlers/command_project.py - init_command()
**Estado:** ✅ Completado (2026-05-17)

---

### 19. Mejorar comando /clone
Mejorar /clone: auto-hacer /init después de clonar, soportar repos privados con SSH, mostrar progreso, validar URL.
**Archivos:** bot/handlers/command_project.py - clone_command()
**Estado:** ⏳ Pendiente

---

### 28. Comando /rename para cambiar título de sesión
Crear comando /rename <nuevo_titulo> usando PATCH /session/{session_id}.
**Archivos:** bot/handlers/command_sessions.py, bot/servers/opencode.py, bot/handlers/command_base.py
**Estado:** ✅ Completado (2026-05-17)

---

### 31. Investigar por qué /create no registra proyecto en la tabla project de OpenCode
/create crea sesión con projectID="global". OpenCode solo registra proyectos en tabla project cuando se abren desde TUI.
**Opciones:** 1) /create hace git init, 2) /projects incluye sesiones globales, 3) Investigar otro endpoint.
**Archivos:** bot/handlers/command_project.py, bot/handlers/command_info.py
**Estado:** ⏳ Pendiente

---

### 33. Limpiar texto para TTS más natural
El TTS pronuncia literalmente el markdown del agente. Añadir clean_text_for_tts() para eliminar backticks, asteriscos, links, headers.
**Archivos:** bot/services/tts.py
**Estado:** ✅ Completado (2026-05-17)

---

### 35. Añadir init_project_git() en opencode.py
Nuevo método que llama a POST /project/git/init?directory=path. Hace git init + registra proyecto en OpenCode.
**Archivos:** bot/servers/opencode.py
**Estado:** ⏳ Pendiente

---

### 36. Modificar init_project() para usar /project/git/init
Cuando is_new=True: llamar a init_project_git() antes de crear la sesión. Así el proyecto se registra en OpenCode y aparece en /projects.
**Archivos:** bot/services/session_manager.py - init_project()
**Estado:** ⏳ Pendiente

---

### 37. Crear templates AGENTS.md y SPEC.md
Funciones helper para generar archivos template al crear proyecto nuevo. AGENTS.md con secciones de arquitectura, convenciones, comandos. SPEC.md con propósito, requisitos, estado.
**Archivos:** bot/services/session_manager.py
**Estado:** ⏳ Pendiente

---

### 38. Simplificar /projects tras registro automático
Los proyectos creados desde el bot ya aparecen en GET /project. Simplificar la lógica de sesiones globales (mantener como fallback).
**Archivos:** bot/handlers/command_project.py - projects_command()
**Estado:** ⏳ Pendiente

---

### 39. Validar comportamiento de /project/git/init
Probar qué pasa si el directorio ya tiene .git. ¿Devuelve error o retorna proyecto existente? Determinar si /init también puede usarlo para registrar proyectos no registrados (caso TUI).
**Archivos:** bot/servers/opencode.py, bot/services/session_manager.py
**Estado:** ⏳ Pendiente

---

## Notas Técnicas

- Puerto de OpenCode: **4097** (no 4096)
- TTS fix: usar `text.strip()` + voz `es-MX-DaliaNeural`
- Arquitectura: Bot = puente, LLM tiene contexto de sesión
- Al hacer /init → cargar sesión más reciente del proyecto (no crear nueva)
