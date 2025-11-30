# Informe para equipo frontend: ausencia de header Authorization en /api/plantas

## Resumen del síntoma
- Tras un login exitoso contra `/api/auth/login`, las peticiones `GET /api/plantas` devuelven `401 Unauthorized` con el mensaje "Falta token de autenticación".
- Los logs del backend muestran que las peticiones a `/api/plantas` llegan **sin** header `Authorization`, mientras el login se procesa correctamente.

## Evidencias desde el backend
- El middleware de Flask registra cada petición (excepto `OPTIONS`) e indica cuando llega sin `Authorization`, listando los headers presentes. Esto confirma que `GET /api/plantas` no trae el header al servidor. 
- El servicio de autenticación devuelve `401` con el mensaje observado cuando el header falta, antes de intentar validar el token.

## Interpretación
- No hay indicios de que el backend esté rechazando el token por firma, expiración o rol: el login genera y decodifica tokens correctamente. El problema es que el token no está siendo enviado o no alcanza al backend en `GET /api/plantas`.
- Esto apunta a la capa cliente o a algún intermediario (proxy/CORS) que omite o elimina el header `Authorization` entre el navegador y Flask.

## Acciones recomendadas para frontend
1. **Verificar que el cliente HTTP adjunte el header** en la primera carga tras el login (sin depender de `skipAuth`). Inspeccionar en el navegador (Network tab) que `Authorization: Bearer <token>` aparece en la request real.
2. **Confirmar configuración de CORS/fetch:** si se usa `credentials: 'include'`, que no haya restricciones que impidan enviar `Authorization`. Revisar que el `mode` y `credentials` de fetch/Axios no bloqueen headers personalizados.
3. **Revisar el almacenamiento del token en sesión** y el flujo de reactividad: asegurar que el hook/composable exponga el token antes de disparar `loadPlantas` (p.ej., evitar condiciones de carrera al inicializar la sesión).
4. **Probar con cURL o Postman** desde la misma máquina donde corre el frontend, usando el token emitido por el login. Si funciona, el problema está en cómo el frontend construye o envía la petición desde el navegador.
5. **Revisar proxies o dev-servers** (Vite, webpack dev server) por reglas que puedan eliminar `Authorization` al hacer proxy a `https://localhost:8000`.

## Próximos pasos sugeridos
- Reproducir el flujo en el navegador con la consola de red abierta y capturar si el header está ausente. 
- Si el header está presente en la request del navegador pero no llega al backend, revisar el proxy o la configuración TLS/HTTPS. 
- Una vez confirmado que el header llega, verificar si persiste algún 401 diferente (firma o expiración) y ajustar en consecuencia.
