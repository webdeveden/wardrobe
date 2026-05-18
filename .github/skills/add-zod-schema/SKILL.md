---
name: add-zod-schema
description: Define and wire up a new Zod validation schema in the Wardrobe Catalog backend. Use this skill when adding input validation for new request bodies, query parameters, or file upload metadata. Ensures schemas are defined centrally, used with safeParse, and return structured error responses.
---

# Add Zod Schema

Use this skill when the user asks to add validation for a new endpoint, request body, or query string.

## Checklist — every schema must have all of these

- [ ] Schema defined in `backend/src/validation/product.js` (central location)
- [ ] Used with `.safeParse()` in the route handler, not `.parse()` (avoids unhandled throws)
- [ ] Failed parse returns `400` with `result.error.flatten()` for structured field errors
- [ ] Optional fields use `.optional()` or `.default()`
- [ ] Numbers from query strings coerced with `z.coerce.number()` (query params are always strings)
- [ ] Enums validated with `z.enum([...])` against known values
- [ ] Exported from the validation file and imported in the route

## File location

- All schemas: `backend/src/validation/product.js`

## Existing schemas (do not duplicate)

- `productInputSchema` — CRUD product fields (name, slug, description, aisle, quantity, categoryId, eraId)
- `productQuerySchema` — Catalog filters and pagination (search, category, era, sort, page, pageSize)
- `imageInputSchema` — Image metadata (url, alt, sortOrder)

## Schema patterns

### Request body

```js
import { z } from "zod";

export const myThingInputSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  quantity: z.number().int().min(0).default(0),
  status: z.enum(["active", "archived"]),
});
```

### Query parameters (always coerce numbers and booleans)

```js
export const myThingQuerySchema = z.object({
  search: z.string().optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(48).default(12),
  status: z.enum(["active", "archived"]).optional(),
});
```

### File upload metadata

```js
export const fileMetaSchema = z.object({
  alt: z.string().max(255).optional(),
  sortOrder: z.coerce.number().int().min(0).default(0),
});
```

## Using safeParse in a route

```js
import { myThingInputSchema } from "../validation/product.js";

router.post("/", requireAdmin, async (req, res) => {
  const result = myThingInputSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten() });
  }

  // result.data is now typed and safe to use
  const { name, description, quantity, status } = result.data;
  // ...
});
```

## `error.flatten()` response shape

```json
{
  "errors": {
    "formErrors": [],
    "fieldErrors": {
      "name": ["Required"],
      "quantity": ["Expected number, received string"]
    }
  }
}
```

## Common mistakes to avoid

- Do NOT use `.parse()` in route handlers — it throws and bypasses your error handler
- Do NOT read `req.query.page` as a number without `z.coerce.number()` — it's always a string
- Do NOT define schemas inline in route files — keep them in `validation/product.js`
- Do NOT forget to export the schema and import it in the route
- Do NOT add `.required()` — fields are required by default in Zod; use `.optional()` to opt out
