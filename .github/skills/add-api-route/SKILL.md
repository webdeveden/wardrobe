---
name: add-api-route
description: Add a new FastAPI route to the Wardrobe Catalog backend. Use this skill when creating public catalog endpoints or protected admin routes. Ensures auth dependencies, Pydantic validation, HTTPException errors, eager loading, and consistent response models are always applied.
---

# Add API Route

Use this skill when the user asks to add, create, or scaffold a new backend API endpoint.

## Checklist — every route must have all of these

- [ ] Correct HTTP method decorator (`@router.get/post/put/delete`)
- [ ] Auth dependency: `require_auth` for any logged-in user, `require_admin` for admin-only routes
- [ ] Inputs declared as Pydantic models — never read `request.json()` or raw query params
- [ ] `response_model=` and `status_code=` set on the decorator
- [ ] Expected errors raised as `HTTPException(status, "message")` (404 for missing rows, 409 for conflicts)
- [ ] No raw SQL — use SQLAlchemy `select()`, `session.get()`, `session.add()`, `session.delete()`
- [ ] Related data eager-loaded with `.options(...)`, never in a loop (relations are `lazy="raise"`)
- [ ] No hardcoded secrets — read from `app.config.settings`
- [ ] Router registered in `app/main.py` with `app.include_router(...)` if it's a new file
- [ ] Test added in `backend/tests/`

## File locations

- Public routes (no auth): `backend/app/routers/catalog.py`
- Admin routes: `backend/app/routers/admin.py` (router-level `require_admin`)
- Auth routes: `backend/app/routers/auth.py`
- Chat/RAG: `backend/app/routers/chat.py`
- Schemas: `backend/app/schemas.py`
- Auth dependencies: `backend/app/security.py`

## Route template

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Product
from app.schemas import ProductOut
from app.security import require_admin
from app.services.products import PRODUCT_LOAD_OPTIONS

router = APIRouter(prefix="/api/things", tags=["things"], dependencies=[Depends(require_admin)])

Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("/{product_id}", response_model=ProductOut)
async def get_thing(product_id: int, session: Session) -> Product:
    product = await session.scalar(
        select(Product).where(Product.id == product_id).options(*PRODUCT_LOAD_OPTIONS)
    )
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product
```

## Auth dependencies

```python
from app.security import CurrentAdmin, CurrentUser

@router.get("/me")
async def me(payload: CurrentUser): ...          # any authenticated user

@router.delete("/{id}")
async def remove(id: int, admin: CurrentAdmin): ...  # admin role required
```

## Pagination pattern

```python
filters = [...]
items = (
    await session.scalars(
        select(Product).where(*filters)
        .offset((query.page - 1) * query.page_size).limit(query.page_size)
        .options(*PRODUCT_LOAD_OPTIONS)
    )
).all()
total = await session.scalar(select(func.count()).select_from(Product).where(*filters)) or 0
return ProductListOut.model_validate(
    {"items": items, "total": total, "page": query.page, "page_size": query.page_size,
     "total_pages": math.ceil(total / query.page_size)}
)
```

## Common mistakes to avoid

- Do NOT skip the auth dependency on admin routes
- Do NOT read `request.json()` before Pydantic validates it
- Do NOT write `text("SELECT ...")` — use SQLAlchemy expressions
- Do NOT access relationships you didn't eager-load (it raises)
- Do NOT call blocking functions directly in `async def` — use `run_in_threadpool`
- Do NOT forget `invalidate_product_embeddings()` after admin writes that change products
