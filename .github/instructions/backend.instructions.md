---
name: Backend Rules
description: Enforced rules for all Wardrobe Catalog backend code
applyTo: "backend/**/*.py"
---

## Auth Dependencies

- Admin routes must depend on `require_admin` — never just `require_auth`
- Public routes (catalog, auth, chat) need no dependency
- Import from `app.security` (`require_auth`, `require_admin`, `CurrentUser`, `CurrentAdmin`)

## Input Validation

- Declare request bodies and query params as Pydantic models in the route signature — never read `request.json()` / `request.query_params` directly
- Query models: `query: Annotated[MyQuery, Query()]`
- Invalid input returns `400 {"message", "issues"}` automatically (handler in `app/main.py`)
- All schemas live in `backend/app/schemas.py` and extend `CamelModel` (camelCase JSON)

## Database

- No raw SQL — use SQLAlchemy `select()`, `session.get()`, `session.add()`, `session.delete()`
- Relationships are `lazy="raise"`: eager-load with `.options(...)` (`PRODUCT_LOAD_OPTIONS`), never query inside a loop
- New foreign key columns need an `Index(...)` in the model's `__table_args__`
- Every schema change needs an Alembic revision (`alembic revision --autogenerate -m "..."`)

## Error Handling

- Raise `HTTPException(status, "message")` for expected errors; unexpected exceptions become `500` globally
- Set `response_model` and `status_code` on every route: `200/201/204` success, `400` validation, `401/403` auth, `404` not found, `409` conflict
- Check `session.get()` / `scalar()` results for `None` and raise `404` before use
- Catch `IntegrityError` on commits that can violate unique constraints and return `409`

## Async

- Routes are `async`; wrap blocking/CPU-heavy calls (bcrypt, large file IO) in `run_in_threadpool`

## Secrets

- No hardcoded values — all secrets and config via `app.config.settings` (env vars)
- Never commit `.env` files
