# Contrato de endpoints para la app de mantenimiento

Este documento resume **lo que el frontend espera** del backend. Incluye URL base, contratos de petición/respuesta, códigos esperados y relaciones entre entidades.

## Configuración
- URL base: variable de entorno `VITE_API_BASE_URL` (ejemplo: `http://localhost:3000/api`).
- Cabeceras: el frontend envía `Content-Type: application/json` en todas las peticiones.
- Formato de respuesta: salvo en eliminaciones, se espera JSON válido.
- Errores: ante `response.ok === false` se intenta leer `{ "message": string }` desde el cuerpo; en caso contrario se usa `statusText` para mostrar el error al usuario.
- Autenticación: todas las rutas bajo `/api` requieren cabecera `Authorization: Bearer <token>` emitido por `POST /auth/login`, con expiración configurable vía `AUTH_TOKEN_TTL_SECONDS`. El alcance (`role`, `areas`, `equipos`) se recalcula contra la base de datos del usuario en cada petición para evitar usar claims obsoletos del token.

## Autenticación y alcance
- Roles soportados: `superadministrador`, `administrador`, `maquinista`, `invitado`.
- Claims esperados en el token/sesión:
  - `role`: uno de los cuatro anteriores.
  - `areas: number[]`: IDs de áreas para administradores.
  - `equipos: number[]`: IDs de equipos para maquinistas.
  - `username`: nombre de usuario para trazabilidad.
- Las vistas restringen botones y formularios según estos claims, pero **el backend debe validar el alcance en cada endpoint**.
- Endpoint disponible: `POST /auth/login` con body `{ "username", "password" }` devuelve `{ token, expires_in, user: { username, role, areas, equipos } }`.
- Los usuarios se almacenan de forma persistente con contraseñas hasheadas; la app puede auto-sembrar los usuarios demo (`superadmin`, `admin`, `maquinista`, `invitado`) si la variable `AUTH_BOOTSTRAP_DEMO_USERS` está habilitada.

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
  - Autorización: solo `superadministrador` puede crear/editar/eliminar.

### Áreas
- `GET /plantas/{plantaId}/areas` → `Area[]` de la planta.
- `POST /plantas/{plantaId}/areas` con body `{ nombre }` → área creada (`Area`).
- `PUT /areas/{id}` con body `{ nombre }` → área actualizada (`Area`).
- `DELETE /areas/{id}` → respuesta 204 o cualquier 2xx sin cuerpo.
  - Autorización: `superadministrador` o `administrador` con `area.id` en `areas` (y la planta asociada).

### Equipos
- `GET /areas/{areaId}/equipos` → `Equipo[]` del área.
- `POST /areas/{areaId}/equipos` con body `{ nombre }` → equipo creado (`Equipo`).
- `PUT /equipos/{id}` con body `{ nombre }` → equipo actualizado (`Equipo`).
- `DELETE /equipos/{id}` → respuesta 204 o cualquier 2xx sin cuerpo.
  - Autorización: `superadministrador`; `administrador` si el área está en su alcance; `maquinista` si el equipo está en `equipos` (solo para edición/eliminación).

### Sistemas
- `GET /equipos/{equipoId}/sistemas` → `Sistema[]` del equipo.
- `POST /equipos/{equipoId}/sistemas` con body `{ nombre }` → sistema creado (`Sistema`).
- `PUT /sistemas/{id}` con body `{ nombre }` → sistema actualizado (`Sistema`).
- `DELETE /sistemas/{id}` → respuesta 204 o cualquier 2xx sin cuerpo.
  - Autorización: mismo alcance que el equipo padre.

## Consideraciones adicionales
- Tras crear/actualizar, el frontend vuelve a pedir la lista del nivel para reflejar los cambios; devolver el registro actualizado evita inconsistencias locales.
- Se muestran mensajes de validación si el nombre está vacío en el cliente; el backend puede reforzar estas reglas devolviendo un error con `message` descriptivo.
- Respuestas de error deben seguir el formato `{ "message": string }` para que el frontend muestre feedback coherente.
- El backend valida que `nombre` exista y no esté vacío en todos los POST/PUT; ante incumplir la regla responde 400 con `{ "message": "El campo 'nombre' es obligatorio" }`.
- Autenticación: el endpoint `POST /auth/login` valida usuarios persistentes con contraseñas hasheadas; ajustar la URL en `useAuth` basta para usar este flujo.
