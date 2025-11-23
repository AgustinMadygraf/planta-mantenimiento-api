# Contrato de endpoints para la app de mantenimiento

Este documento resume **lo que el frontend espera** del backend. Incluye URL base, contratos de petición/respuesta, códigos esperados y relaciones entre entidades.

## Configuración
- URL base: variable de entorno `VITE_API_BASE_URL` (ejemplo: `http://localhost:3000/api`).
- Cabeceras: el frontend envía `Content-Type: application/json` en todas las peticiones.
- Formato de respuesta: salvo en eliminaciones, se espera JSON válido.
- Errores: ante `response.ok === false` se intenta leer `{ "message": string }` desde el cuerpo; en caso contrario se usa `statusText` para mostrar el error al usuario.

## Modelos usados por la vista
- `Planta`: `{ id: number; nombre: string }`.
- `Area`: `{ id: number; nombre: string; plantaId: number }`.
- `Equipo`: `{ id: number; nombre: string; areaId: number }`.
- `Sistema`: `{ id: number; nombre: string; equipoId: number }`.
- Payloads de creación/edición: `{ nombre: string }`.

## Recursos y jerarquía
Plantas → Áreas → Equipos → Sistemas. Cada nivel se carga en cascada a partir del ID padre. Si un recurso padre se elimina, el frontend limpia la selección y vuelve a pedir la lista correspondiente.

## Contratos por endpoint

### Plantas
- `GET /plantas` → `Planta[]`.
- `POST /plantas` con body `{ nombre }` → planta creada (`Planta`).
- `PUT /plantas/{id}` con body `{ nombre }` → planta actualizada (`Planta`).
- `DELETE /plantas/{id}` → respuesta 204 o cualquier 2xx sin cuerpo.

### Áreas
- `GET /plantas/{plantaId}/areas` → `Area[]` de la planta.
- `POST /plantas/{plantaId}/areas` con body `{ nombre }` → área creada (`Area`).
- `PUT /areas/{id}` con body `{ nombre }` → área actualizada (`Area`).
- `DELETE /areas/{id}` → respuesta 204 o cualquier 2xx sin cuerpo.

### Equipos
- `GET /areas/{areaId}/equipos` → `Equipo[]` del área.
- `POST /areas/{areaId}/equipos` con body `{ nombre }` → equipo creado (`Equipo`).
- `PUT /equipos/{id}` con body `{ nombre }` → equipo actualizado (`Equipo`).
- `DELETE /equipos/{id}` → respuesta 204 o cualquier 2xx sin cuerpo.

### Sistemas
- `GET /equipos/{equipoId}/sistemas` → `Sistema[]` del equipo.
- `POST /equipos/{equipoId}/sistemas` con body `{ nombre }` → sistema creado (`Sistema`).
- `PUT /sistemas/{id}` con body `{ nombre }` → sistema actualizado (`Sistema`).
- `DELETE /sistemas/{id}` → respuesta 204 o cualquier 2xx sin cuerpo.

## Consideraciones adicionales
- Tras crear/actualizar, el frontend vuelve a pedir la lista del nivel para reflejar los cambios; devolver el registro actualizado evita inconsistencias locales.
- Se muestran mensajes de validación si el nombre está vacío en el cliente; el backend puede reforzar estas reglas devolviendo un error con `message` descriptivo.
- Autenticación: actualmente el login es de demostración (sin llamada a API). Si se expone un endpoint real (p. ej. `POST /auth/login`), se podrá integrar añadiendo la llamada dentro del composable `useAuth`.
