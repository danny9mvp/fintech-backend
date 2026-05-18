# Fintech Backend

API REST para una aplicación fintech. Construida con FastAPI, SQLAlchemy, PostgreSQL y JWT.

## Requisitos

- Python 3.14+
- PostgreSQL 16+
- Docker y Docker Compose (opcional)

## Configuración local

```bash
cp .env.example .env
# Editar DATABASE_URL y SECRET_KEY en .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up --build -d
```

## Endpoints

Documentación interactiva (OpenAPI): `/docs` o `/redoc`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | /ping | No | Health check |
| POST | /auth/register | No | Registro |
| POST | /auth/login | No | Login |
| POST | /auth/refresh | No | Renovar tokens |
| POST | /auth/logout | No | Cerrar sesión |
| GET | /users/me | Sí | Perfil actual |
| GET/POST | /categories/ | Sí | Listar/crear categorías |
| GET/PATCH/DELETE | /categories/{id} | Sí | CRUD categoría |
| GET/POST | /movements/ | Sí | Listar/crear movimientos |
| GET/PATCH/DELETE | /movements/{id} | Sí | CRUD movimiento |

## AI Usage

### Herramientas utilizadas

Se utilizó OpenCode (agente basado en Claude) como asistente de desarrollo durante todo el proyecto. Las tareas incluyeron:

- Scaffolding inicial del proyecto (estructura de directorios, modelos, CRUD base, routers, esquemas)
- Diseño e implementación de la estrategia de refresh tokens y logout
- Configuración de Docker Compose para despliegue multi-contenedor
- Corrección de bugs (timezone en consultas a DB, conexión entre contenedores)
- Escritura de pruebas unitarias
- Documentación y scripts de despliegue

### Ejemplos concretos

**1. Implementación de refresh tokens.** Pedí implementar un endpoint de logout con una estrategia de refresh tokens. El asistente propuso tres opciones (token blacklist, token versioning, client-side) y una cuarta alternativa con refresh tokens + rotación. Se implementó la opción de refresh tokens, incluyendo modelo, CRUD, servicio, controlador y migración de Alembic. Las pruebas unitarias cubren los casos de refresh exitoso, token revocado, token expirado y logout.

**2. Scaffolding del proyecto.** Pedí crear la estructura completa del backend desde cero. El asistente generó el esqueleto del proyecto con FastAPI, SQLAlchemy, JWT y Alembic, incluyendo la separación en capas (modelos, CRUD, servicios, controladores, esquemas).

```
app/
  main.py
  core/         (config, database, security)
  model/        (User, Movement, MovementCategory)
  schemas/      (Pydantic request/response)
  crud/         (CRUDBase + CRUD por entidad)
  service/      (lógica de negocio)
  api/          (routers + dependencias de auth)
tests/
  conftest.py   (cliente de prueba, fixtures)
  test_auth.py
alembic/        (migraciones)
```

**3. Configuración de Docker Compose.** Pedí desplegar el backend junto con PostgreSQL y el frontend Angular en contenedores separados. El asistente generó los Dockerfiles, docker-compose.yml con redes compartidas, configuración de nginx para el frontend y un script de despliegue. Se encontraron errores de conexión que se resolvieron iterativamente (envío de variables de entorno vs archivo .env, `alembic.ini` con host hardcodeado).

### Sugerencia modificada

El asistente propuso usar `depends_on` en ambos docker-compose files para controlar el orden de inicio. Lo rechacé porque `depends_on` entre proyectos separados de Compose no funciona: cada archivo solo conoce sus propios servicios. En su lugar se usa un script externo con un loop `until curl` que espera a que el backend responda antes de iniciar el frontend.

### Valoración

El uso del asistente aceleró significativamente el desarrollo, especialmente en tareas de integración (Docker, autenticación) que requieren coordinar múltiples archivos. La calidad del código se mantuvo gracias a las revisiones y correcciones iterativas. El mayor beneficio fue la velocidad para prototipar y detectar edge cases. La principal desventaja fue depender de la precisión de las indicaciones para evitar configuraciones incorrectas (como variables de entorno mal resueltas).
