# Wardrobe Catalog - AI Coding Instructions

## Project Overview

**Wardrobe House Catalog** is a full-stack e-commerce style inventory management system for wardrobe and photography inventory with AI-powered recommendations.

- **Frontend**: Vue 3, Vite, Tailwind CSS, Pinia (state management), Vue Router
- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.0 async ORM (psycopg 3), Pydantic v2 validation, Alembic migrations
- **Runtime**: Bun (frontend), uvicorn (backend)
- **AI**: OpenRouter embeddings + GPT-4o-mini for RAG-based chat (`openai` Python SDK)
- **Auth**: JWT (HS256, PyJWT) + `bcrypt` for password hashing
- **File Uploads**: multipart form (5MB max per file, 10 file limit, images only)
- **Containers**: Docker Compose (`db`, `backend`, `frontend` via nginx)

---

## File Structure Conventions

### Backend (`/backend`)

```
app/
  ├── main.py               # FastAPI app, CORS, /uploads static mount, error handlers
  ├── config.py             # Settings from env/.env (pydantic-settings)
  ├── db.py                 # Async engine + get_session dependency
  ├── models.py             # SQLAlchemy models (tables keep camelCase column names)
  ├── schemas.py            # Pydantic input/output schemas (camelCase JSON)
  ├── security.py           # JWT, bcrypt, require_auth / require_admin dependencies
  ├── seed.py               # `python -m app.seed`
  ├── data/mock-products.json
  ├── routers/
  │   ├── catalog.py        # Public product listing, search, filters
  │   ├── admin.py          # Protected CRUD + uploads
  │   ├── auth.py           # Register, login, /me token refresh
  │   └── chat.py           # RAG-based AI chat endpoint
  └── services/
      ├── chat.py           # Chat generation with semantic search
      ├── embeddings.py     # Vector embeddings & in-memory cache
      ├── llm.py            # Shared OpenRouter client
      ├── products.py       # PRODUCT_LOAD_OPTIONS (eager loading)
      └── slug.py           # URL-safe slug conversion
alembic/versions/           # Additive migration history
tests/                      # pytest
Dockerfile, docker-entrypoint.sh  # runs `alembic upgrade head` then uvicorn
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
- **Secret**: `JWT_SECRET` env var via `settings.jwt_secret` (required when `ENVIRONMENT=production`, `"dev-secret-change-me"` for dev)
- **Algorithm**: HS256
- **Token Expiry**: Always check `exp * 1000 > Date.now()` before using cached token
- **Refresh**: Call `GET /api/auth/me` on app load to refresh token state

### Auth Dependencies

```python
from app.security import CurrentUser, CurrentAdmin, require_admin

@router.get("/me")
async def me(payload: CurrentUser): ...          # Any authenticated user

router = APIRouter(dependencies=[Depends(require_admin)])  # Admin role required
```

### Pydantic Validation (All Inputs)

- **Location**: `backend/app/schemas.py`
- **Pattern**: Declare the body/query as a Pydantic model in the route signature; FastAPI validates it
- **Errors**: Validation failures return `400 { message, issues }` (handler in `main.py`)
- **JSON casing**: Models extend `CamelModel` — Python uses snake_case, JSON uses camelCase
- **Schemas available**:
  - `ProductIn` — CRUD product fields
  - `ProductQuery` — Catalog filters, pagination, search (`Annotated[ProductQuery, Query()]`)
  - `ImageIn` — Image metadata (url, alt, sortOrder)
  - `AuthIn`, `ChatIn`, and `*Out` response models

### Password Hashing

- **Library**: `bcrypt` (via `hash_password` / `verify_password` in `app/security.py`)
- **Pattern**: Always hash passwords before storing (never plain text)
- **Verify**: `await verify_password(plain, user.password_hash)`; hashes from the old bcryptjs backend still verify

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
- `POST /api/admin/uploads` — Upload images (5MB, 10 files max)

### RAG Chat (Semantic Search)

1. User sends message via `POST /api/chat/message`
2. Embeddings library generates vector from user input
3. Semantic search finds top 5 most similar products (cosine similarity)
4. System prompt includes product context + company voice
5. GPT-4o-mini generates response with recommended product links

### Product Slug Generation

- **Pattern**: Lowercase, spaces → hyphens, special chars removed
- **Unique**: Enforced by the `Product_slug_key` unique index (duplicate → 409)
- **Usage**: Used in URLs & API routes (e.g., `/products/red-wool-coat`)

### File Upload

- **Destination**: `UPLOADS_DIR` (default `./uploads/`; Docker volume at `/app/uploads`)
- **Max File Size**: 5MB per file
- **Max Files**: 10 files per request
- **Naming**: `{timestamp}-{uuid}{extension}` (non-image extensions stored as `.bin`)
- **Serving**: FastAPI `StaticFiles` mount at `/uploads/{filename}`

### Pagination

- **Default Page Size**: 12 items
- **Max Page Size**: 48 items
- **Query Params**: `page=1`, `pageSize=12`
- **Response**: `{ items: Product[], total: number, page: number, pageSize: number }`

---

## Database Schema (SQLAlchemy, `app/models.py`)

Tables were originally created by Prisma; names and camelCase columns are kept as-is.

```text
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

- New admin routes must depend on `require_admin`, not just `require_auth`
- Chat endpoint is public but should include rate limiting if needed

❌ **Unvalidated Inputs**

- Never read `await request.json()` directly — declare a Pydantic model parameter
- Add constraints with `Annotated[..., Field(...)]` in `schemas.py`

❌ **Raw SQL Queries**

- NEVER write raw SQL strings or `text()` with interpolated values
- Use SQLAlchemy `select()`, `session.get()`, `session.add()`, etc.

❌ **Missing Error Handling**

- Raise `HTTPException(status, "message")` for expected errors (rendered as `{ "message": ... }`)
- Unexpected exceptions are logged and returned as `500 { "message": "Internal server error" }`
- Catch `IntegrityError` for unique-constraint races and return 409

❌ **Hardcoded Secrets**

- All secrets (JWT_SECRET, OPENROUTER_API_KEY, etc.) come from env via `app/config.py`
- Never commit `.env` files; use `.env.example` as template

❌ **N+1 Queries / Lazy Loads**

- Relationships are `lazy="raise"`: accessing an unloaded relation throws
- Load related data with `.options(*PRODUCT_LOAD_OPTIONS)` (joinedload/selectinload)
- Never query inside a loop over results

❌ **Blocking the Event Loop**

- Routes are `async`; run CPU-bound or blocking calls (bcrypt, file IO on big files) via `run_in_threadpool`

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

- Declare indexes in the model's `__table_args__` (e.g. `Index("Product_categoryId_idx", "categoryId")`)

❌ **Schema Drift**

- Never manually edit the database schema via SQL
- Edit `app/models.py`, then `alembic revision --autogenerate -m "description"` and review the file
- Verify with `alembic current` / `alembic check` before pushing

❌ **Breaking Migrations**

- Migrations are additive only—cannot delete columns without data loss consideration
- If adding a unique constraint to an existing non-unique column: data must be clean first
- Test migrations on dev database before deploying

---

## Verification Checklist

### Before Submitting New Code

**Backend Routes**

- [ ] Route has correct HTTP method (GET/POST/PUT/DELETE)
- [ ] Auth dependency applied (`require_auth` or `require_admin`)
- [ ] Inputs declared as Pydantic models (no manual `request.json()`)
- [ ] `response_model` and `status_code` set (200, 201, 204, 400, 401, 403, 404, 409, 500)
- [ ] Expected errors raised as `HTTPException`
- [ ] No hardcoded secrets (use `settings`)
- [ ] No raw SQL queries
- [ ] Related data eager-loaded (no lazy loads / N+1)
- [ ] Unit test added in `backend/tests/` where practical

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
- [ ] Foreign key indexes present
- [ ] Unique constraints used when needed (slug, email)
- [ ] `updatedAt` set via `onupdate=utcnow`
- [ ] Cascade delete configured for dependent records
- [ ] Migration tested locally (`alembic upgrade head` and `alembic downgrade -1`)

### Local Testing

```bash
# Full stack in Docker (app on :8080, API on :4000)
docker compose up -d --build
docker compose exec backend python -m app.seed

# Or: DB in Docker, backend on host with hot reload
docker compose up -d db
cd backend && source .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --port 4000
pytest

# Frontend dev server
cd frontend && bun run dev
```

---

## Environment Variables

### Backend (`backend/.env`)

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wardrobe_catalog
JWT_SECRET=your-secret-key-here          # required when ENVIRONMENT=production
OPENROUTER_API_KEY=sk-or-...
FRONTEND_ORIGIN=http://localhost:5173    # comma-separated CORS origins
ENVIRONMENT=development
```

Docker Compose overrides `DATABASE_URL`, `PORT`, `FRONTEND_ORIGIN` and `UPLOADS_DIR`.

### Frontend (`.env.local` or Vite config)

```
VITE_API_URL=http://localhost:4000/api   # Docker build uses /api (nginx proxy)
```

---

## Quick Reference

| Task                    | Pattern                                                         | File                                |
| ----------------------- | --------------------------------------------------------------- | ----------------------------------- |
| Add API route           | `require_auth`/`require_admin` dependency, Pydantic models, `HTTPException` | `backend/app/routers/*.py`      |
| Create component        | Use ref/computed, handle loading/error, call API with try-catch | `frontend/src/components/*.vue`     |
| Modify schema           | Edit models, `alembic revision --autogenerate -m "..."`          | `backend/app/models.py`             |
| Add validation          | Define Pydantic model in `schemas.py`, use as route parameter   | `backend/app/schemas.py`            |
| Handle auth in frontend | Use `authToken`, `authUser`, `isAdmin` computed from auth store | `frontend/src/stores/auth.js`       |
| Generate embeddings     | `get_product_embeddings()` / `invalidate_product_embeddings()`  | `backend/app/services/embeddings.py`|
| Search products         | `find_relevant_products()`                                      | `backend/app/services/embeddings.py`|

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Alembic**: https://alembic.sqlalchemy.org
- **Vue 3 Docs**: https://vuejs.org/guide/
- **Pydantic**: https://docs.pydantic.dev
- **Tailwind CSS**: https://tailwindcss.com
