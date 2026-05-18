---
name: code-review
description: Review Wardrobe Catalog code changes for correctness, security, and project conventions. Use this skill when the user asks to review a file, a diff, or a PR. Checks backend routes, Vue components, Prisma schema changes, and Zod validation against the project's standards.
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

- [ ] Every non-public route uses `requireAuth` or `requireAdmin`
- [ ] Admin routes use `requireAdmin`, not just `requireAuth`
- [ ] All `req.body` / `req.query` input parsed with a Zod schema before use
- [ ] `.safeParse()` used (not `.parse()`) with a 400 response on failure
- [ ] No secrets hardcoded — all from `process.env`
- [ ] No raw SQL — only Prisma ORM methods

### Correctness

- [ ] All async route handlers have `try-catch` with a 500 fallback
- [ ] Response includes an explicit status code on every branch
- [ ] Prisma errors don't leak stack traces to the client
- [ ] `findUnique` results checked for `null` before use (return 404 if missing)

### Performance

- [ ] Related data fetched with `include`, never inside a loop
- [ ] `findMany` calls have a `take` limit to avoid unbounded results
- [ ] New foreign key columns have a matching `@@index` in schema.prisma

### Conventions

- [ ] Route file is in the correct location (`catalog.js`, `admin.js`, `auth.js`, `chat.js`)
- [ ] New Zod schemas added to `backend/src/validation/product.js`, not inline
- [ ] Response shape is consistent `{ data }` or `{ message }` — not a mix

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

- [ ] Migration is additive (no dropped columns without deliberate review)
- [ ] Non-nullable columns added to existing tables have a `@default`
- [ ] `@unique` not added to a column that currently has duplicates
- [ ] `onDelete: Cascade` on the child relation field (not the parent)
- [ ] `@@index` present on all foreign key columns

---

## How to report findings

For each issue found, output:

```
[SEVERITY] File:line — Description of the problem
Suggestion: what to change
```

Severity levels: **CRITICAL** (security / data loss), **HIGH** (correctness bug), **MEDIUM** (performance / missing guard), **LOW** (convention / style).

Only flag real issues. Do not invent problems or add suggestions beyond what's needed to fix the identified issue.
