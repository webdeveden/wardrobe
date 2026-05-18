---
name: Frontend Rules
description: Enforced rules for all Wardrobe Catalog frontend code
applyTo: "frontend/src/**"
---

## Reactive State

- All mutable state must use `ref()` or `reactive()` — never plain `let`/`const` for template data
- Derived values must use `computed()` — not recalculated inline in the template
- Always use `.value` when reading or writing a `ref` inside `<script setup>`

## API Calls

- Use exported functions from `frontend/src/api/client.js` only — no raw `fetch()` or direct `axios` calls
- No hardcoded URLs — the Axios client handles base URL via `import.meta.env.VITE_API_URL`
- Every API call must be wrapped in `try-catch` with an `error` ref set on failure
- Toggle a `loading` ref before and after every async operation; always reset it in `finally`

## Auth

- Admin-only UI must use `v-if="isAdmin"` — never rely on the API returning 403 as the only guard
- Import auth state from `frontend/src/stores/auth.js`

## Props

- Declare props with `defineProps` using object syntax (`type`, `required`, `default`)
- Do not access `$attrs` directly when props are the right tool

## Style

- Tailwind class names must be valid — use hyphens not underscores, check IntelliSense
- Show a loading state (skeleton or spinner) while any async operation is in progress
- Show an error message in the template when `error.value` is set — never fail silently
