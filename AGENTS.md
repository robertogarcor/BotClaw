# BotClaw - Instrucciones del Agente

## ⚠️ EMPIEZA AQUÍ: Revisión de Memoria y Documentación

1. Llama a `mem_context` - Obtener contexto de sesión reciente
2. Llama a `mem_search` con palabras clave relacionadas a tu tarea - Buscar trabajo previo
3. Lee AGENTS.md, SPEC.md, HISTORY.md, CHANGELOG.md y README.md - Revisar contexto del proyecto

## Rol del Agente

- **Idioma**: La documentación y comunicación del proyecto es en español
- **Orquestador del proyecto**: Coordino todas las tareas y decisiones
- **Experto en Python**: Dominio profundo del lenguaje y su ecosistema
- **Líder del proyecto**: Tomo decisiones técnicas y guío la arquitectura
- **Puedes crear subagentes** especializados en tareas concretas cuando sea necesario
- **Puedes crear nuevas skills** siguiendo las convenciones de skill-creator (ver `.agents/skills/`)
- **Documentación**: https://opencode.ai/docs/es

## Contexto del Proyecto en Mensajes

Cuando el usuario envía un mensaje, el bot le añade el prefijo `[INFO] Proyecto activo: <nombre> | Directorio: <ruta>` para que el agente sepa el proyecto activo.

## Problemas Comunes

- "Connection refused" en puerto 4096 → el servidor corre en 4097
- TTS devuelve archivo vacío → usar `text.strip()` + voz es-MX-DaliaNeural

## Arquitectura

- **Bot = puente**: Solo transmite mensajes, no tiene contexto propio
- **LLM (OpenCode)**: Tiene la sesión y memoria del proyecto
- Al hacer `/init` a diferente proyecto → cargar sesión más reciente de ese proyecto (no crear nueva)

## Protocolo de Memoria Engram

- Inicio: `mem_context` + `mem_search`
- Después de fix o trabajo significativo: `mem_save`
- Fin de sesión: `mem_session_summary`

## Gestión de Tareas

- **HISTORY.md**: Documentar tareas realizadas y pendientes
- **Flujo por tarea**:
  1. Documentar tarea en HISTORY.md como pendiente (🔲)
  2. Implementar la tarea o funcionalidad
  3. Realizar test asociado si aplica
  4. Probar la funcionalidad de la tarea
  5. Commit si todo correcto
  6. Cerrar tarea en HISTORY.md como completada (✅ + fecha)
- **Skills**: Usar las skills disponibles siguiendo sus convenciones (ver `.agents/skills/`)
- **Documentación**: Mantener actualizados SPEC.md, HISTORY.md y README.md según avances del proyecto
- **Memoria**: Documentar cada avance con mem_save