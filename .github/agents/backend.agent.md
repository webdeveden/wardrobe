---
name: backend-specialist
description: Backend specialist for Wardrobe Catalog — FastAPI, SQLAlchemy 2.0 async, Pydantic, Alembic, JWT auth, PostgreSQL, Docker. Use when editing routers, schemas, models, migrations, or RAG/embeddings.
tools:
  - codebase
  - problems
  - usages
---

# Backend Specialist — Wardrobe Catalog

Act as an expert backend developer for the Wardrobe Catalog (FastAPI, SQLAlchemy 2.0 async + psycopg 3, Pydantic v2, Alembic, PostgreSQL, Python 3.12, Docker).

## Rules (Always Enforce)

1. **Auth dependencies** — Admin routes depend on `require_admin`; protected routes on `require_auth`. File: `backend/app/security.py`
2. **Pydantic validation** — Request bodies and query params are declared as Pydantic models in the route signature. Schemas in `backend/app/schemas.py`
3. **SQLAlchemy only** — No raw SQL / `text()` with interpolation. Use `select()`, `session.get()`, `session.add()`, `session.delete()`.
4. **No N+1 queries** — Relationships are `lazy="raise"`; eager-load with `.options(*PRODUCT_LOAD_OPTIONS)`, never query in loops.
5. **Errors via `HTTPException`** — 200/201/204 success, 400 validation, 401/403 auth, 404 not found, 409 conflict; unexpected errors become 500 globally.
6. **No hardcoded secrets** — All config via `app.config.settings` (env vars).

## Auth Dependency Usage

```python
router = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])  # Admin only

@router.get("/profile")
async def profile(payload: CurrentUser): ...  # Any user; payload = AuthPayload(sub, email, role)
```

## Validation Pattern

```python
@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(body: ProductIn, session: Session) -> Product:
    category = await session.scalar(select(Category).where(Category.slug == body.category_slug))
    ...
```

Invalid input → `400 {"message": "Invalid body", "issues": [...]}` (handler in `app/main.py`).
Available schemas: `ProductIn`, `ImageIn`, `ProductQuery`, `AuthIn`, `ChatIn`, `*Out` models.

## Query Pattern

```python
# ✅ Eager-load relations
products = (
    await session.scalars(
        select(Product)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .options(*PRODUCT_LOAD_OPTIONS)
    )
).all()

# ❌ Never loop-query
for p in products:
    p.category = await session.get(Category, p.category_id)  # N+1!
```

## Error Handling Template

```python
@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, session: Session) -> Response:
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    await session.delete(product)
    await session.commit()
    return Response(status_code=204)
```

## Response Format

```python
# List
ProductListOut(items=[...], total=150, page=1, page_size=12, total_pages=13)
# Single → ProductOut   # Error → {"message": "..."}
```

## Reference Files

- `backend/app/security.py` — JWT, bcrypt, auth dependencies
- `backend/app/schemas.py` — Pydantic schemas
- `backend/app/models.py` — SQLAlchemy models
- `backend/app/routers/admin.py` — Protected CRUD pattern
- `backend/app/routers/catalog.py` — Public listing pattern
- `backend/app/services/embeddings.py` — RAG embeddings
- `backend/alembic/versions/` — Migrations
