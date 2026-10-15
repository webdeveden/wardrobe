---
name: code-review
description: Review Wardrobe Catalog code changes for correctness, security, and project conventions. Use this skill when the user asks to review a file, a diff, or a PR. Checks FastAPI routes, Vue components, SQLAlchemy/Alembic schema changes, and Pydantic validation against the project's standards.
---

# Code Review

Use this skill when the user asks to review code, check a diff, or audit a file before merging.

## Review order

1. **Security** — auth guards, input validation, secrets, SQL injection
2. **Correctness** — logic bugs, missing error handling, wrong status codes
3. **Performance** — N+1 queries, missing indexes, unbounded queries
4. **Conventions** — project patterns, naming, file placement
5. **Style** — Tailwind typos, missing reactivity wrappers, unused imports

---

## Backend review checklist

### Auth & security

- [ ] Every non-public route depends on `require_auth` or `require_admin`
- [ ] Admin routes use `require_admin`, not just `require_auth`
- [ ] All bodies / query params declared as Pydantic models (no manual `request.json()`)
- [ ] File uploads parsed after the auth dependency runs, with size/count/type limits
- [ ] No secrets hardcoded — all from `app.config.settings`
- [ ] No raw SQL or `text()` with interpolated values — only SQLAlchemy expressions

### Correctness

- [ ] Expected failures raised as `HTTPException`; unique-constraint `IntegrityError` → 409 with rollback
- [ ] `response_model` and `status_code` set on the route decorator
- [ ] Database errors don't leak stack traces to the client (global handler returns a generic 500)
- [ ] `session.get()` / `scalar()` results checked for `None` before use (404 if missing)
- [ ] No blocking calls inside `async def` (use `run_in_threadpool`)

### Performance

- [ ] Related data eager-loaded with `.options(...)`, never queried inside a loop
- [ ] List queries have a `.limit()` to avoid unbounded results
- [ ] New foreign key columns have a matching `Index(...)` in the model's `__table_args__`

### Conventions

- [ ] Route is in the correct router (`app/routers/catalog.py`, `admin.py`, `auth.py`, `chat.py`)
- [ ] New schemas added to `backend/app/schemas.py` and extend `CamelModel`, not defined inline
- [ ] Errors use the `{ message }` shape; success bodies match a declared `*Out` model
- [ ] Admin writes that change products call `invalidate_product_embeddings()`

---

## Frontend review checklist

### Reactivity

- [ ] All mutable state uses `ref()` or `reactive()` — no plain `let`/`const` for state
- [ ] Derived values use `computed()` — not recomputed in the template
- [ ] Props declared with `defineProps`, not accessed from `$attrs`

### API & error handling

- [ ] API calls use the Axios client from `src/api/client.js` — no hardcoded URLs
- [ ] All `await` calls inside `try-catch`
- [ ] `loading` ref toggled around every async call, reset in `finally`
- [ ] `error` ref displayed in the template so the user sees failures

### Auth

- [ ] Admin-only UI elements guarded with `v-if="isAdmin"`
- [ ] Routes that require auth have a navigation guard in `router.js`

### Style

- [ ] Tailwind class names are valid (no underscores, no made-up utilities)
- [ ] Component file name is PascalCase and matches the component name

---

## Database / schema review checklist

- [ ] Every model change has an Alembic revision in `backend/alembic/versions/`, reviewed by hand
- [ ] Migration is additive (no dropped columns without deliberate review)
- [ ] Non-nullable columns added to existing tables have a `server_default`
- [ ] Unique index not added to a column that currently has duplicates
- [ ] `ondelete="CASCADE"` on the child FK; parent relationship uses `passive_deletes=True`
- [ ] Indexes present on all foreign key columns
- [ ] `downgrade()` implemented

---

## How to report findings

For each issue found, output:

```
[SEVERITY] File:line — Description of the problem
Suggestion: what to change
```

Severity levels: **CRITICAL** (security / data loss), **HIGH** (correctness bug), **MEDIUM** (performance / missing guard), **LOW** (convention / style).

Only flag real issues. Do not invent problems or add suggestions beyond what's needed to fix the identified issue.
