# Informe técnico: formato de errores para la carga jerárquica de activos

Este informe resume el problema detectado por el frontend durante la carga jerárquica de **Plantas → Áreas → Equipos → Sistemas** y las expectativas de formato de error que debe cumplir la API para evitar mensajes genéricos en la UI.

## Contexto del frontend
- **Framework:** Vue 3 + TypeScript.
- **Módulo afectado:** `useAssetLoading`.
- **Consumo de API:** endpoints REST para plantas, áreas, equipos y sistemas.
- **Clientes HTTP:** funciones asíncronas que usan `fetch` a través del wrapper `request` y esperan respuestas JSON.

## Flujo y manejo de error en el frontend
Durante la carga jerárquica se invocan los endpoints:
- `GET /plantas`
- `GET /plantas/{plantaId}/areas`
- `GET /areas/{areaId}/equipos`
- `GET /equipos/{equipoId}/sistemas`

Si `response.ok === false`, el frontend intenta extraer `errorBody.message` del JSON. Si el cuerpo no es JSON válido, usa `response.statusText` o texto plano y lanza un `Error`, que se muestra al usuario mediante notificaciones (`useNotifier`).

## Problema observado
Cuando el backend no devuelve errores con `{ "message": "..." }`, el frontend muestra mensajes genéricos o poco informativos, dificultando el soporte y la experiencia de usuario.

## Requerimientos para el backend
1. **Formato de error consistente:** todas las respuestas de error deben ser JSON con la propiedad `message`.
   ```json
   {
     "message": "Descripción clara del error"
   }
   ```
2. **Códigos HTTP apropiados:** usar el código que corresponda (`400`, `401`, `403`, `404`, `409`, `500`, etc.).
3. **Cuerpo en errores:** no devolver respuestas vacías ni HTML; siempre incluir JSON con `message`.
4. **Validación clara:** en errores de validación, devolver mensajes específicos por campo.
5. **Ejemplo esperado:**
   ```http
   HTTP/1.1 404 Not Found
   Content-Type: application/json

   {
     "message": "No se encontró el área solicitada"
   }
   ```

## Impacto
Sin el formato anterior, el frontend no puede mostrar errores claros y los usuarios reciben mensajes genéricos, especialmente durante la carga de plantas, áreas, equipos y sistemas.

## Referencias
- `useAssetLoading.ts`
- `apiClient.ts`
- `frontend-api-contract.md`
