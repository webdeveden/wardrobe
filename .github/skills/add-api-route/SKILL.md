---
name: add-api-route
description: Add a new Express.js API route to the Wardrobe Catalog backend. Use this skill when creating public catalog endpoints or protected admin routes. Ensures auth guards, Zod validation, try-catch, and consistent response shapes are always applied.
---

# Add API Route

Use this skill when the user asks to add, create, or scaffold a new backend API endpoint.

## Checklist — every route must have all of these

- [ ] Correct HTTP method (`GET`, `POST`, `PUT`, `DELETE`)
- [ ] Auth guard: `requireAuth` for any logged-in user, `requireAdmin` for admin-only routes
- [ ] Input validated with a Zod schema using `.safeParse()` — never trust raw `req.body` or `req.query`
- [ ] Explicit HTTP status codes on every response path (200, 201, 400, 401, 403, 404, 500)
- [ ] Async handler wrapped in `try-catch` with a 500 fallback
- [ ] No raw SQL — use Prisma methods (`findMany`, `findUnique`, `create`, `update`, `delete`)
- [ ] Related data fetched with `include`, never in a loop (no N+1 queries)
- [ ] No hardcoded secrets — read from `process.env`
- [ ] Returns JSON with a consistent shape

## File locations

- Public routes (no auth): `backend/src/routes/catalog.js`
- Admin routes: `backend/src/routes/admin.js`
- Auth routes: `backend/src/routes/auth.js`
- Chat/RAG: `backend/src/routes/chat.js`
- Validation schemas: `backend/src/validation/product.js`
- Auth middleware: `backend/src/middleware/auth.js`

## Route template

```js
import { Router } from "express";
import { requireAdmin } from "../middleware/auth.js";
import { myInputSchema } from "../validation/product.js";
import { db } from "../db.js";

const router = Router();

router.post("/", requireAdmin, async (req, res) => {
  const result = myInputSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten() });
  }

  try {
    const record = await db.someModel.create({
      data: result.data,
      include: { relatedModel: true },
    });
    return res.status(201).json(record);
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
});

export default router;
```

## Auth guards

```js
import { requireAuth, requireAdmin } from "../middleware/auth.js";

router.get("/me", requireAuth, handler);      // any authenticated user
router.delete("/:id", requireAdmin, handler); // admin role required
```

## Pagination pattern

```js
const { page = 1, pageSize = 12 } = result.data;
const [items, total] = await Promise.all([
  db.product.findMany({ skip: (page - 1) * pageSize, take: pageSize }),
  db.product.count(),
]);
return res.json({ items, total, page, pageSize });
```

## Common mistakes to avoid

- Do NOT skip the auth guard on admin routes
- Do NOT access `req.body` fields before Zod parses them
- Do NOT write `SELECT * FROM ...` — use Prisma
- Do NOT fetch relations inside a loop — use `include`
