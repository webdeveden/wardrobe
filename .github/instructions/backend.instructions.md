---
name: Backend Rules
description: Enforced rules for all Wardrobe Catalog backend code
applyTo: "backend/src/**"
---

## Auth Guards

- Admin routes must use `requireAdmin` — never just `requireAuth`
- Public routes (catalog, auth) need no guard
- Import from `backend/src/middleware/auth.js`

## Input Validation

- All `req.body` and `req.query` must be parsed with a Zod schema using `.safeParse()` before use
- On failure: `return res.status(400).json({ errors: result.error.flatten() })`
- All schemas live in `backend/src/validation/product.js` — do not define them inline in routes

## Database

- No raw SQL — use Prisma methods only (`findMany`, `findUnique`, `create`, `update`, `delete`, `count`)
- Load relations with `include` upfront — never fetch them inside a loop (N+1)
- New foreign key columns must have a matching `@@index` in `schema.prisma`

## Error Handling

- Every async route handler must have a `try-catch` with a `500` fallback
- Explicit status codes on every response branch: `200/201` success, `400` validation, `401/403` auth, `404` not found, `500` server error
- Check `findUnique` results for `null` and return `404` before accessing properties

## Secrets

- No hardcoded values — all secrets and config via `process.env`
- Never commit `.env` files
