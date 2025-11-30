# Estado de tareas del proyecto

## Tareas implementadas
- [x] Contrato de API documentado para plantas, áreas, equipos y sistemas, incluyendo rutas, payloads `{ nombre }` y reglas de autorización previstas para cada recurso. Esta guía alinea el backend con las expectativas del frontend.
- [x] Manejo de errores Flask actualizado para responder con cuerpos `{ "message": ... }` en `400 BadRequest`, `404 NotFound` y otros errores HTTP, coherente con el formato que consume el frontend.
- [x] Arquitectura y flujo base de CRUD jerárquico (plantas → áreas → equipos → sistemas) descritos en README y casos de uso conectados en el enrutador de Flask.
- [x] Normalización de respuestas de error en la capa Flask para que cualquier `HTTPException` (p. ej. `405 Method Not Allowed`) devuelva `{ "message": string }` y los errores inesperados se expresen como `{ "message": "Internal server error" }`.
- [x] Autenticación demo vía `/api/auth/login` que emite tokens con claims (`role`, `areas`, `equipos`, `username`) y middleware de autorización aplicado a todos los endpoints CRUD.
- [x] Pruebas automatizadas cubriendo login, autorizaciones por rol y manejo uniforme de errores en Flask, que validan el comportamiento esperado antes de integrar una autenticación real.
- [x] Autenticación persistente con usuarios almacenados en base de datos, contraseñas hasheadas, TTL configurable por `AUTH_TOKEN_TTL_SECONDS` y bootstrap opcional de usuarios demo mediante `AUTH_BOOTSTRAP_DEMO_USERS`.
- [x] Validación de payloads `{ nombre }` en todos los POST/PUT de CRUD con mensaje consistente `{ "message": "El campo 'nombre' es obligatorio" }` cuando falta o está vacío, alineado con el contrato del frontend.

## Tareas en progreso / parcialmente hechas
- [ ] Ninguna registrada.

## Tareas pendientes o incompletas
- [x] Alcance de áreas/equipos vinculado a datos reales al recalcular permisos por usuario desde la base de datos en cada petición.
- [x] Añadir pruebas de integración end-to-end que cubran los roles y alcances (superadministrador, administrador, maquinista, invitado) sobre las operaciones CRUD.
