# Repository Guidelines

## Project Structure & Module Organization
- `src/entities` define el dominio (plantas, areas, equipos, sistemas).
- `src/use_cases` orquesta casos de uso sobre puertos de repositorio.
- `src/interface_adapters` contiene controladores/presenters para Flask/FastAPI y gateways.
- `src/infrastructure` aloja wiring, configuracion SQLAlchemy, repositorios y logging.
- `src/shared` guarda utilidades transversales (config, logger, helpers).
- `src/interface_adapters/schemas` concentra esquemas Pydantic que validan los payloads con nombres en español y entregan data ya traducida para los casos de uso.
- `tests/` agrupa pruebas unitarias/integracion rapidas; `docs/` tiene contratos y guias.

## Build, Test, and Development Commands
```bash
python -m venv venv && venv\Scripts\activate    # entorno local
pip install -r requirements.txt                  # dependencias (incluye alembic)
python start_ssl.py                               # certificados dev en certs/
alembic upgrade head                              # aplica migraciones
python run.py                                     # levanta API Flask en https://localhost:8000
pytest                                            # ejecuta suite
pytest --cov=src --cov-report=term-missing        # cobertura opcional
```

## Coding Style & Naming Conventions
- Python 3.x, indentacion 4 espacios, PEP 8 como base; tipado opcional preferido en casos de uso y entidades.
- Modulos/clases en ingles (e.g., `SqlAlchemyPlantRepository`), claves JSON en espanol para la API.
- Docstrings breves en espanol; evita logica de dominio en controladores (sigue entidad -> caso de uso -> adaptador -> infraestructura).
- Los esquemas en `src/interface_adapters/schemas` y `_validate_payload` aseguran que los payloads inválidos produzcan 400 y que los datos pasen a los casos de uso en ingles.

## Testing Guidelines
- Framework: `pytest`; archivos `test_*.py` en `tests/`.
- Cubre entidades, repositorios y manejo de errores en controladores.
- Usa/crea fixtures en `tests/conftest.py` para rutas o sesiones SQLAlchemy compartidas.
- Al agregar codigo, extiende cobertura y respeta contratos en `docs/*.md`.

## Commit & Pull Request Guidelines
- Mensajes concisos en imperativo (ej.: `Add CORS information endpoint to Flask application`).
- PRs: objetivo, cambios clave, notas de compatibilidad (DB_*, CORS, TLS), evidencia de pruebas (`pytest`, comandos manuales) y ticket/enlace si aplica.

## Security & Configuration Tips
- Usa `.env.example` como base; nunca subas credenciales. Variables `DB_*` definen conexion y pooling.
- Alembic es el flujo oficial de migraciones y registra su progreso en `alembic_version`. No existe ya un script de bootstrap; usa `alembic upgrade head` en entornos nuevos y `alembic stamp head` solo si llegas desde un esquema preexistente.
- Regenera certificados locales con `python start_ssl.py` si caducan; mantelos en `certs/`.
