# Wardrobe House Catalog

A split web app for managing and presenting wardrobe + photography inventory with an e-commerce style experience.

## Stack

- Frontend: Vue 3, Vite, Tailwind CSS, Pinia (JavaScript + JSDoc, Bun)
- Backend: FastAPI, SQLAlchemy 2 (async, psycopg 3), Pydantic, Alembic
- Database: PostgreSQL
- AI: OpenRouter embeddings + `gpt-4o-mini` for RAG chat
- Containers: Docker + Docker Compose

## Project Structure

- `frontend`: customer-facing catalog + admin interface (served by nginx in Docker)
- `backend`: API (`app/`), migrations (`alembic/`), tests (`tests/`)
- `docker-compose.yml`: Postgres + backend + frontend

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env   # set JWT_SECRET and OPENROUTER_API_KEY
docker compose up -d --build
docker compose exec backend python -m app.seed   # optional: load mock products
```

- App: http://localhost:8080 (nginx proxies `/api` and `/uploads` to the backend)
- API: http://localhost:4000 (interactive docs at http://localhost:4000/docs)

Migrations run automatically when the backend container starts (`RUN_MIGRATIONS=false` disables this).

Host ports are configurable if the defaults are taken: `DB_PORT`, `BACKEND_PORT`, `FRONTEND_PORT`
(e.g. `DB_PORT=55432 docker compose up -d`). Compose always points the backend at the bundled
database; set `BACKEND_DATABASE_URL` to use another one.

## Local development (without Docker for the app)

Start only the database: `docker compose up -d db`

Backend (Python 3.11+):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 4000
pytest
```

Frontend:

```bash
cd frontend
bun install
bun run dev
```

Frontend runs at `http://localhost:5173` and calls the backend at `http://localhost:4000/api`.

## Database migrations

```bash
cd backend
alembic revision --autogenerate -m "describe change"   # after editing app/models.py
alembic upgrade head
```

Existing databases created by the old Prisma backend are compatible: the baseline migration
detects the existing tables and only records its revision.

## Promoting a user to admin

Register through the UI, then set `role = 'ADMIN'` on that row in the `"User"` table. The frontend
picks up the new role on next load (`GET /api/auth/me` re-issues the token).

## API Endpoints

- `GET /api/health`
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/catalog/meta`
- `GET /api/catalog/products` (`page`, `pageSize`, `search`, `category`, `era`, `sort`)
- `GET /api/catalog/products/{slug}`
- `POST /api/chat/message`
- Admin (requires an ADMIN token):
  - `GET /api/admin/products`, `POST /api/admin/products`
  - `PUT /api/admin/products/{id}`, `DELETE /api/admin/products/{id}`
  - `POST /api/admin/uploads` (multipart `files`, up to 10 images, 5MB each)
