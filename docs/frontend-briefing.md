# Informe para frontend: estado del backend y expectativas de integración

Este informe resume los cambios recientes del backend y lo que debe esperar/ajustar el frontend para mantenerse alineado.

## Autenticación y sesión
- **Flujo disponible:** `POST /api/auth/login` recibe `{ "username", "password" }` y responde `{ token, expires_in, user: { username, role, areas, equipos } }`.
- **Persistencia:** los usuarios se almacenan en BD con contraseñas hasheadas; se pueden sembrar usuarios demo mediante `AUTH_BOOTSTRAP_DEMO_USERS`.
- **Claims y alcance:** en cada petición el backend recalcula `role`, `areas` y `equipos` desde la BD antes de autorizar, por lo que el frontend debe reenviar el token vigente y refrescarlo cuando expire (`expires_in`).
- **Cabecera requerida:** `Authorization: Bearer <token>` en todas las rutas `/api`.

## Autorización por rol
- Roles soportados: `superadministrador`, `administrador`, `maquinista`, `invitado`.
- El backend aplica el alcance en cada endpoint: solo `superadministrador` puede CRUD de plantas; áreas y equipos se limitan según `areas`/`equipos` del usuario; `invitado` es solo lectura.
- Si el alcance no es suficiente, la respuesta es `403` con `{ "message": "..." }`.

## Contratos CRUD y validaciones
- Modelos esperados por la UI: `Planta { id, nombre }`, `Area { id, nombre, plantaId }`, `Equipo { id, nombre, areaId }`, `Sistema { id, nombre, equipoId }`.
- Payloads de creación/edición: `{ nombre: string }`; el backend valida que `nombre` exista y no esté vacío y devuelve `400` con `{ "message": "El campo 'nombre' es obligatorio" }` si falla.
- Endpoints devuelven JSON del recurso creado/actualizado; las eliminaciones responden 204 (sin cuerpo).

## Manejo de errores y formato de respuestas
- Todas las excepciones HTTP (400, 401, 403, 404, 405) y errores inesperados retornan `{ "message": string }` en JSON.
- El frontend debería mostrar `message` cuando `response.ok` sea falso y caer en `statusText` solo si no hay cuerpo JSON.

## Recomendaciones para el frontend
- Apuntar `VITE_API_BASE_URL` a la URL donde esté desplegado `/api`.
- Refrescar datos tras crear/editar para reflejar el recurso que el backend devuelve.
- Gestionar expiración de token usando `expires_in` y volver a loguear cuando sea necesario.
- Mantener las restricciones de UI basadas en `role`/`areas`/`equipos`, pero considerar que el backend puede rechazar acciones fuera de alcance.
