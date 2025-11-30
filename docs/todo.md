[x] Documentar contrato de API y requisitos del frontend
[x] Documentar expectativas de manejo de errores en la carga jerárquica
[x] Ajustar ScopeAuthorizer.filter_areas para aceptar el contexto de planta
[>] Auditar el resto de endpoints para asegurar respuestas de error JSON consistentes
    - Revisar todos los endpoints CRUD (plantas, áreas, equipos, sistemas) y autenticación
    - Verificar que devuelvan `{ "message": "..." }` en errores y el status HTTP adecuado
    - Corregir cualquier endpoint que no cumpla el formato
