# Wardrobe Catalog - AI Coding Instructions

## Project Overview

**Wardrobe House Catalog** is a full-stack e-commerce style inventory management system for wardrobe and photography inventory with AI-powered recommendations.

- **Frontend**: Vue 3, Vite, Tailwind CSS, Pinia (state management), Vue Router
- **Backend**: Express.js 5.x, Prisma ORM, PostgreSQL, Zod validation
- **Runtime**: Bun
- **AI**: OpenAI/OpenRouter embeddings + GPT-4o-mini for RAG-based chat
- **Auth**: JWT (HS256) + bcryptjs for password hashing
- **File Uploads**: Multer (5MB max, 10 file limit)

---

## File Structure Conventions

### Backend (`/backend`)

```
src/
  ├── index.js              # Express server entry
  ├── db.js                 # Prisma client initialization
  ├── middleware/
  │   └── auth.js           # JWT verification & guards (requireAuth, requireAdmin)
  ├── routes/
  │   ├── catalog.js        # Public product listing, search, filters
  │   ├── admin.js          # Protected CRUD operations
  │   ├── auth.js           # Register, login, token refresh
  │   └── chat.js           # RAG-based AI chat endpoint
  ├── validation/
  │   └── product.js        # Zod schemas for all inputs
  └── lib/
      ├── chat.js           # Chat generation with semantic search
      ├── embeddings.js     # Vector embeddings & caching
      └── slug.js           # URL-safe slug conversion
prisma/
  ├── schema.prisma         # Database models & relationships
  ├── seed.js               # Database seeding script
  └── migrations/           # Additive migration history
```

### Frontend (`/frontend`)

```
src/
  ├── main.js               # Vue app entry
  ├── router.js             # Route definitions & guards
  ├── api/
  │   └── client.js         # Axios configuration, token handling
  ├── stores/
  │   ├── auth.js           # User token, role, login status (Pinia)
  │   ├── catalog.js        # Products, filters, pagination (Pinia)
  │   └── chat.js           # Chat history & messages (Pinia)
  ├── views/
  │   ├── CatalogView.vue   # Product grid with filters
  │   ├── ProductDetailView.vue  # Single product page
  │   └── AdminView.vue     # Inventory management
  └── components/
      ├── ProductCard.vue   # Grid item component
      ├── ChatModal.vue     # AI chat interface
      ├── LoginModal.vue    # Authentication dialog
      ├── ProductQrCode.vue # QR code generator
      └── ProductSkeleton.vue  # Loading placeholder
```

---

## Critical Authentication & Validation Patterns

### JWT Authentication

- **Token Storage**: localStorage (key: `wardrobe-auth-token`)
- **Token Format**: Bearer token in `Authorization` header (`Bearer <token>`)
- **Token Payload**: `{ sub: userId, email, role: "USER" | "ADMIN", iat, exp }`
- **Secret**: `process.env.JWT_SECRET` (required in production, `"dev-secret-change-me"` for dev)
- **Algorithm**: HS256
- **Token Expiry**: Always check `exp * 1000 > Date.now()` before using cached token
- **Refresh**: Call `GET /api/auth/me` on app load to refresh token state

### Auth Middleware Usage

```javascript
// In route handlers, ALWAYS use one of these:
export function requireAuth(req, res, next)  // Any authenticated user
export function requireAdmin(req, res, next) // Admin role required
```

### Zod Validation (All Inputs)

- **Location**: `backend/src/validation/product.js`
- **Pattern**: Parse + validate all request bodies, query params, file uploads
- **Example**: `productInputSchema.parse(req.body)` or `.safeParse()` for error handling
- **Schemas available**:
  - `productInputSchema` — CRUD product fields
  - `productQuerySchema` — Catalog filters, pagination, search
  - `imageInputSchema` — Image metadata (url, alt, sortOrder)

### Password Hashing

- **Library**: `bcryptjs`
- **Pattern**: Always hash passwords before storing (never plain text)
- **Verify**: Use `bcryptjs.compare(plainPassword, hash)` in login routes

---

## Key Business Logic Patterns

### API Endpoints

**Public (No Auth Required)**

- `GET /api/catalog/meta` — Categories & eras
- `GET /api/catalog/products` — Paginated products with filters (search, category, era, sort)
- `GET /api/catalog/products/:slug` — Single product detail with images
- `POST /api/chat/message` — RAG chat (sends message, context, receives AI response)
- `POST /api/auth/register` — Create new user account
- `POST /api/auth/login` — Get JWT token

**Protected Admin Routes (requireAdmin)**

- `GET /api/admin/products` — List all products (with admin filters)
- `POST /api/admin/products` — Create new product
- `PUT /api/admin/products/:id` — Update product
- `DELETE /api/admin/products/:id` — Delete product
- `POST /api/admin/uploads` — Upload images (Multer: 5MB, 10 files max)

### RAG Chat (Semantic Search)

1. User sends message via `POST /api/chat/message`
2. Embeddings library generates vector from user input
3. Semantic search finds top 5 most similar products (cosine similarity)
4. System prompt includes product context + company voice
5. GPT-4o-mini generates response with recommended product links

### Product Slug Generation

- **Pattern**: Lowercase, spaces → hyphens, special chars removed
- **Unique**: Enforced in Prisma schema (`slug` is `@unique`)
- **Usage**: Used in URLs & API routes (e.g., `/products/red-wool-coat`)

### File Upload (Multer)

- **Destination**: `./uploads/` directory
- **Max File Size**: 5MB per file
- **Max Files**: 10 files per request
- **Naming**: `{timestamp}-{uuid}{extension}` (auto-generated)
- **Serving**: Express static middleware serves via `/uploads/{filename}`

### Pagination

- **Default Page Size**: 12 items
- **Max Page Size**: 48 items
- **Query Params**: `page=1`, `pageSize=12`
- **Response**: `{ items: Product[], total: number, page: number, pageSize: number }`

---

## Database Schema (Prisma)

```prisma
User (id, email, passwordHash, role: USER|ADMIN, createdAt, updatedAt)
  └─ Unique: email, role enum

Category (id, name, slug, createdAt, updatedAt)
  └─ Unique: name, slug
  └─ Relation: products[]

Era (id, name, slug, createdAt, updatedAt)
  └─ Unique: name, slug
  └─ Relation: products[]

Product (id, name, slug, description, aisle, quantity, categoryId, eraId, createdAt, updatedAt)
  ├─ Unique: slug
  ├─ Indexes: categoryId, eraId, createdAt, aisle
  ├─ Relations: category, era, images[]
  └─ Cascade Delete: images

ProductImage (id, productId, url, alt, sortOrder)
  ├─ Index: (productId, sortOrder)
  └─ Cascade Delete on product deletion
```

### Key Constraints

- **Products**: Each must have categoryId, eraId (foreign keys)
- **Images**: Each product must have at least 1 image
- **Slug**: Must be unique (used in product URLs)
- **Indexes**: Always present on foreign keys (categoryId, eraId) for query performance

---

## Common AI-Generated Mistakes to Avoid

### Backend

❌ **Missing Auth Guards**

- New admin routes must use `requireAdmin` middleware, not just `requireAuth`
- Chat endpoint is public but should include rate limiting if needed

❌ **Unvalidated Inputs**

- ALWAYS validate request body/params with Zod before accessing
- Use `.safeParse()` for proper error handling
- Example: `const result = productInputSchema.safeParse(req.body); if (!result.success) return res.status(400).json({ errors: result.error.flatten() });`

❌ **Raw SQL Queries**

- NEVER write raw SQL (e.g., `SELECT * FROM products WHERE name LIKE ...`)
- Use Prisma methods: `findMany()`, `findUnique()`, `create()`, `update()`, etc.
- Risk: SQL injection vulnerabilities

❌ **Missing Error Handling**

- All async operations must have try-catch
- Response must include proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Example: `catch (error) { return res.status(500).json({ message: error.message }); }`

❌ **Hardcoded Secrets**

- All secrets (JWT_SECRET, OpenAI API key, etc.) must come from `process.env`
- Never commit `.env` files
- Use `.env.example` as template with placeholder values

❌ **N+1 Queries**

- Load related data with Prisma `include` or `select`, not in loops
- Example: `prisma.product.findMany({ include: { category: true, era: true, images: true } })`
- Never: `const products = await prisma.product.findMany(); for (const p of products) { const cat = await prisma.category.findUnique(...); }`

### Frontend

❌ **Missing Reactive State**

- Always wrap state with `ref()` or `computed()` for reactivity
- If data doesn't update on change, likely missing `ref()`
- Example: `const count = ref(0)` not `const count = 0`

❌ **Hardcoded API URLs**

- Use `import.meta.env.VITE_API_URL ?? "http://localhost:4000/api"`
- Axios client already handles this; use the exported functions

❌ **Missing Error Handling on API Calls**

- All `.then()` chains or `await` calls must have `.catch()` or try-catch
- Example: `try { const data = await getProducts(query); } catch (error) { this.error = error.message; }`
- Missing: UI shows loading forever if request fails

❌ **Missing Auth Checks Before Rendering**

- Admin routes should guard with `isAdmin` computed
- Example: `<button v-if="isAdmin" @click="deleteProduct">Delete</button>`
- Missing: Users can see UI elements but requests will 403

❌ **Tailwind CSS Typos**

- Common mistakes: `flex-col` (correct), `flex_col` (incorrect), `w-1/3` (correct), `w-33` (incorrect)
- Use Tailwind IntelliSense extension to verify class names
- Unstyled elements usually mean typo in class name

### Database

❌ **Missing Indexes on Foreign Keys**

- Prisma auto-indexes, but always verify: `@@index([categoryId, eraId])` in schema
- Missing indexes cause slow queries on large datasets

❌ **Schema Drift**

- Never manually edit database schema via SQL
- Always create migrations: `bun run prisma migrate dev --name "description"`
- Verify with `prisma migrate status` before pushing

❌ **Breaking Migrations**

- Migrations are additive only—cannot delete columns without data loss consideration
- If adding `@unique` constraint to existing non-unique column: data must be clean first
- Test migrations on dev database before deploying

---

## Verification Checklist

### Before Submitting New Code

**Backend Routes**

- [ ] Route has correct HTTP method (GET/POST/PUT/DELETE)
- [ ] Auth guard applied (`requireAuth` or `requireAdmin`)
- [ ] Input validated with Zod (`.safeParse()` with error handling)
- [ ] Response includes status code (200, 201, 400, 401, 403, 404, 500)
- [ ] Async errors handled with try-catch
- [ ] No hardcoded secrets (use `process.env`)
- [ ] No raw SQL queries
- [ ] Related data loaded with Prisma `include` (no N+1)
- [ ] Returns valid JSON with consistent structure

**Frontend Components**

- [ ] All state wrapped with `ref()` or `computed()`
- [ ] Props validated with JSDoc `@typedef` or Zod
- [ ] API calls wrapped in try-catch or `.catch()`
- [ ] Loading & error states displayed to user
- [ ] Auth checks before rendering sensitive UI
- [ ] Tailwind classes spelled correctly
- [ ] Responsive design (mobile-first)
- [ ] No console errors or warnings
- [ ] Component name capitalized (Vue convention)

**Database Migrations**

- [ ] Migration file is additive (adds/modifies, never deletes)
- [ ] Foreign key indexes present (`@@index`)
- [ ] `@unique` constraints used when needed (slug, email)
- [ ] @updated datetime field uses `@updatedAt`
- [ ] Cascade delete configured for dependent records
- [ ] Migration tested locally with real data (if applicable)
- [ ] No schema drift between local and schema.prisma

### Local Testing

```bash
# Run migrations
cd backend && bun run prisma migrate dev

# Seed database (if needed)
bun run prisma db seed

# Start backend dev server
bun run dev

# Start frontend dev server
cd ../frontend && bun run dev

# Check for errors
# - Backend: No 500 errors in console
# - Frontend: No errors in browser console
# - Database: Verify data in Prisma Studio
bun run prisma studio
```

---

## Environment Variables

### Backend (`.env`)

```
DATABASE_URL=postgresql://user:password@localhost:5432/wardrobe
JWT_SECRET=your-secret-key-here
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Frontend (`.env.local` or Vite config)

```
VITE_API_URL=http://localhost:4000/api
```

---

## Quick Reference

| Task                    | Pattern                                                         | File                                |
| ----------------------- | --------------------------------------------------------------- | ----------------------------------- |
| Add API route           | Use requireAuth/requireAdmin, Zod validation, try-catch         | `backend/src/routes/*.js`           |
| Create component        | Use ref/computed, handle loading/error, call API with try-catch | `frontend/src/components/*.vue`     |
| Modify schema           | Add migration with `prisma migrate dev --name "..."`            | `backend/prisma/schema.prisma`      |
| Add validation          | Define Zod schema in `validation/product.js`, parse in routes   | `backend/src/validation/product.js` |
| Handle auth in frontend | Use `authToken`, `authUser`, `isAdmin` computed from auth store | `frontend/src/stores/auth.js`       |
| Generate embeddings     | Use `EmbeddingsManager` from `lib/embeddings.js`                | `backend/src/lib/embeddings.js`     |
| Search products         | Use semantic search from `lib/chat.js` context                  | `backend/src/lib/chat.js`           |

---

## Additional Resources

- **Prisma Docs**: https://www.prisma.io/docs
- **Vue 3 Docs**: https://vuejs.org/guide/
- **Express Docs**: https://expressjs.com
- **Zod Docs**: https://zod.dev
- **Tailwind CSS**: https://tailwindcss.com
