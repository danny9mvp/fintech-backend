# AGENTS.md -- fintech-backend

## What this is

A FastAPI backend scaffold for a fintech app. Manages Users, Movements (income/expense), and Movement Categories. JWT auth, SQLAlchemy ORM, Alembic migrations.

## Running

```bash
uvicorn app.main:app --reload
```

## Dependencies

Plain `requirements.txt`, no lockfile. Key packages: fastapi, sqlalchemy, alembic, pyjwt, bcrypt, pydantic-settings.

## Database

- PostgreSQL by default. URL configured via `DATABASE_URL` in `.env`.
- SQLAlchemy 2.x models in `app/model/`.
- Alembic for migrations: `alembic revision --autogenerate -m "msg"` then `alembic upgrade head`.
- Driver: `psycopg2-binary`.

## Project structure

```
app/
  main.py          -- entrypoint, creates tables on import, registers routers
  core/            -- config, database (engine + Base + get_db), security (JWT + bcrypt)
  model/           -- User, Movement, MovementCategory (SQLAlchemy)
  schemas/         -- Pydantic request/response models
  crud/            -- CRUDBase + per-entity CRUD classes
  api/             -- routers: auth, users, categories, movements (all require JWT except auth)
    deps.py        -- get_current_user dependency (HTTPBearer)
```

## Key entities

- **User**: id, email (unique), pwd_hash, username, created_at
- **MovementCategory**: id, name, budget, user_id (FK), created_at. Owned by a User.
- **Movement**: id, user_id (FK), movement_category_id (FK), type, amount, description, created_at. Owned by a User, belongs to a Category.

Ownership enforced at the API layer -- users can only see/edit their own resources.

## Auth

- `POST /auth/register` and `POST /auth/login` return `{"access_token": "...", "token_type": "bearer"}`.
- All other endpoints require `Authorization: Bearer <token>` header.
- Token payload contains `{"sub": "<user_id>"}`.

## Tests

```bash
python -m pytest tests/ -v
```

Uses a separate SQLite file (`test.db`) with `drop_all` between runs. Tests don't require PostgreSQL. Fixtures: `client`, `token`, `auth_header`.

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | No | Register new user |
| POST | /auth/login | No | Login, get JWT |
| GET | /users/me | Yes | Current user profile |
| GET | /users/{id} | No | Get user by ID |
| GET/POST | /categories/ | Yes | List/create categories |
| GET/PATCH/DELETE | /categories/{id} | Yes | Get/update/delete category |
| GET/POST | /movements/ | Yes | List/create movements |
| GET/PATCH/DELETE | /movements/{id} | Yes | Get/update/delete movement |

## Migration workflow

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Gotchas

- No lint, no typecheck, no CI configured.
- `.env` file with `SECRET_KEY` must exist in production.
