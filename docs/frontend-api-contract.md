# Contrato de consumo del frontend (Vue 3 + TypeScript)

Este documento resume los requerimientos que el frontend de Planta Mantenimiento espera de la API. Úsalo como guía para mantener compatibilidad cuando se ajusten endpoints, modelos o manejo de sesión.

## Modelos esperados
- **Planta**: `{ id: number; nombre: string }`
- **Área**: `{ id: number; nombre: string; plantaId: number }`
- **Equipo**: `{ id: number; nombre: string; areaId: number }`
- **Sistema**: `{ id: number; nombre: string; equipoId: number }`
- **Payloads de creación/actualización**: `{ nombre: string }`

## Endpoints consumidos
Las rutas se exponen bajo el prefijo público de la API (p. ej. `/api`). Los DELETE pueden responder `204 No Content`; el resto siempre debe retornar JSON.

### Plantas
- `GET /plantas` → listar plantas.
- `POST /plantas` con `{ nombre }` → crear planta.
- `PUT /plantas/{id}` con `{ nombre }` → actualizar planta.
- `DELETE /plantas/{id}` → eliminar planta.

### Áreas
- `GET /plantas/{plantaId}/areas` → listar áreas de una planta.
- `POST /plantas/{plantaId}/areas` con `{ nombre }` → crear área.
- `PUT /areas/{id}` con `{ nombre }` → actualizar área.
- `DELETE /areas/{id}` → eliminar área.

### Equipos
- `GET /areas/{areaId}/equipos` → listar equipos de un área.
- `POST /areas/{areaId}/equipos` con `{ nombre }` → crear equipo.
- `PUT /equipos/{id}` con `{ nombre }` → actualizar equipo.
- `DELETE /equipos/{id}` → eliminar equipo.

### Sistemas
- `GET /equipos/{equipoId}/sistemas` → listar sistemas de un equipo.
- `POST /equipos/{equipoId}/sistemas` con `{ nombre }` → crear sistema.
- `PUT /sistemas/{id}` con `{ nombre }` → actualizar sistema.
- `DELETE /sistemas/{id}` → eliminar sistema.

## Autenticación y sesión
- `POST /auth/login` debe responder con `{ token, refresh_token, expires_in, user }` donde `user` incluye `username`, `role`, `areas`, `equipos`.
- `POST /auth/refresh` recibe `refresh_token` y devuelve un nuevo `token`.
- Los JWT deben incluir el claim `exp` y validarse en cada request.
- El rol y el alcance (IDs de áreas/equipos) deben aplicarse en la autorización de cada endpoint.

## Manejo de errores
- Si la respuesta HTTP no es exitosa, el cuerpo esperado es `{ message }`.
- Si no hay JSON, se debe usar `response.statusText` o texto plano coherente.
- El frontend muestra estos errores mediante toasts; mantener mensajes claros y en español.

## Consideraciones adicionales
- Habilitar CORS para el dominio del frontend (por defecto `http://localhost:5173`).
- Mantener coherencia de estructura y naming entre respuestas de éxito y error.
- Comunicar cualquier cambio en modelos, endpoints o autenticación al equipo frontend.

## Referencias
- Consumo centralizado: `request` (wrapper sobre `fetch`).
- Modelos: `types.ts`.
- Permisos y alcance: `permissions.ts`.
- Ejemplo de carga jerárquica: `useAssetLoading`.
- Stub local para pruebas: `apiClient.ts`.
