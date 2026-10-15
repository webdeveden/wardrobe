Review the current file (or files I specify) against the Wardrobe Catalog project standards.

Automatically detect whether the file is backend or frontend based on its path:
- `backend/` → apply backend checklist
- `frontend/` → apply frontend checklist
- If I specify a file, review that one

## Backend Review Checklist

- [ ] Auth dependency: every admin route depends on `require_admin`, protected routes on `require_auth`
- [ ] Pydantic validation: bodies and query params declared as `CamelModel` schemas from `app/schemas.py` — no manual `request.json()`
- [ ] No raw SQL: all DB access via SQLAlchemy expressions (`select`, `session.get`, ...)
- [ ] No N+1 queries: relations eager-loaded with `.options(...)` (`PRODUCT_LOAD_OPTIONS`), never queried in loops
- [ ] Error handling: expected errors raised as `HTTPException`; `IntegrityError` on unique fields → 409
- [ ] Status codes: `status_code=201` for create, 200 for get/update, 204 for delete, 400/401/403/404/409 for errors
- [ ] `response_model` set on every route
- [ ] No blocking calls in `async def` (bcrypt, big file IO → `run_in_threadpool`)
- [ ] No hardcoded secrets: all config via `app.config.settings`
- [ ] Response format: `{ items, total, page, pageSize, totalPages }` for lists; single object for detail; `{ message }` for errors

## Frontend Review Checklist

- [ ] Reactive state: all changing data uses `ref()` or `computed()` — no plain variables
- [ ] API calls: uses exported functions from `src/api/client.js`, not raw fetch/axios
- [ ] Error handling: all API calls in try-catch, `error.value` set and shown in template
- [ ] Loading state: skeleton or spinner shown while fetching, buttons disabled during async
- [ ] Auth guards: sensitive UI wrapped with `v-if="isAdmin"` or `v-if="isLoggedIn"`
- [ ] Props: defined with object syntax (`type`, `required`, `default`)
- [ ] No `.value` in template, only in `<script setup>`
- [ ] Emit: `emit()` called after any state-changing action
- [ ] Tailwind: class names are valid (no underscores, correct separators)
- [ ] Responsive: mobile-first with `md:` / `lg:` breakpoints
- [ ] Component name: PascalCase filename

## Output Format

For each checklist item:
- ✅ Pass — brief note
- ❌ Fail — show the exact line(s) and the fix

End with a summary: how many passed, how many failed, and the most critical issue to fix first.
