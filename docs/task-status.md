# Estado de tareas del proyecto

## Tareas implementadas
- [x] Contrato de API documentado para plantas, áreas, equipos y sistemas, incluyendo rutas, payloads `{ nombre }` y reglas de autorización previstas para cada recurso. Esta guía alinea el backend con las expectativas del frontend.
- [x] Manejo de errores Flask actualizado para responder con cuerpos `{ "message": ... }` en `400 BadRequest`, `404 NotFound` y otros errores HTTP, coherente con el formato que consume el frontend.
- [x] Arquitectura y flujo base de CRUD jerárquico (plantas → áreas → equipos → sistemas) descritos en README y casos de uso conectados en el enrutador de Flask.
- [x] Normalización de respuestas de error en la capa Flask para que cualquier `HTTPException` (p. ej. `405 Method Not Allowed`) devuelva `{ "message": string }` y los errores inesperados se expresen como `{ "message": "Internal server error" }`.
- [x] Autenticación demo vía `/api/auth/login` que emite tokens con claims (`role`, `areas`, `equipos`, `username`) y middleware de autorización aplicado a todos los endpoints CRUD.
- [x] Pruebas automatizadas cubriendo login, autorizaciones por rol y manejo uniforme de errores en Flask, que validan el comportamiento esperado antes de integrar una autenticación real.

## Tareas en progreso / parcialmente hechas
- [ ] Ninguna registrada.

## Tareas pendientes o incompletas
- [ ] Sustituir los usuarios/tokenes de demostración por autenticación real (persistencia, hashing de contraseñas, caducidad configurable) y validar sesiones de producción.
- [ ] Revisar el alcance de creación de áreas/equipos cuando existan plantillas de permisos en base de datos y ajustar la lógica a datos reales.
- [ ] Alinear los payloads y respuestas de todos los endpoints CRUD con el contrato documentado, incluyendo validación de `{ nombre }` y uso consistente de mensajes de error.
- [ ] Añadir pruebas de integración end-to-end que cubran los roles y alcances (superadministrador, administrador, maquinista, invitado) sobre las operaciones CRUD.
