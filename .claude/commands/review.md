Review the current file (or files I specify) against the Wardrobe Catalog project standards.

Automatically detect whether the file is backend or frontend based on its path:
- `backend/` → apply backend checklist
- `frontend/` → apply frontend checklist
- If I specify a file, review that one

## Backend Review Checklist

- [ ] Auth guard: every admin route uses `requireAdmin`, protected routes use `requireAuth`
- [ ] Zod validation: all `req.body` and query params parsed with `.safeParse()` before use
- [ ] No raw SQL: all DB access via Prisma methods only
- [ ] No N+1 queries: relations loaded with `include`/`select`, never inside loops
- [ ] Error handling: every async handler wrapped in try-catch with correct status code
- [ ] Status codes: 201 for create, 200 for get/update, 204 for delete, 400/401/403/404/500 for errors
- [ ] No hardcoded secrets: all secrets via `process.env`
- [ ] Response format: `{ items, total, page, pageSize }` for lists; single object for detail

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
