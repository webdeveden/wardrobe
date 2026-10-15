---
name: add-pydantic-schema
description: Define and wire up a new Pydantic validation schema in the Wardrobe Catalog backend. Use this skill when adding input validation for new request bodies, query parameters, or response shapes. Ensures schemas are defined centrally, use camelCase JSON aliases, and produce the project's standard 400 error response.
---

# Add Pydantic Schema

Use this skill when the user asks to add validation for a new endpoint, request body, query string, or response.

## Checklist — every schema must have all of these

- [ ] Schema defined in `backend/app/schemas.py` (central location)
- [ ] Extends `CamelModel` so JSON uses camelCase while Python uses snake_case
- [ ] Used as a typed route parameter (body) or `Annotated[Model, Query()]` (query) — FastAPI validates it
- [ ] Constraints declared with `Annotated[..., Field(...)]` (`min_length`, `ge`, `le`, ...)
- [ ] Optional fields typed `X | None = None` or given a default
- [ ] Fixed value sets use `Literal[...]` (or an `enum.Enum`)
- [ ] Output models used as `response_model=` on the route

## File location

- All schemas: `backend/app/schemas.py`

## Existing schemas (do not duplicate)

- `ProductIn` — CRUD product fields (name, description, aisle, quantity, categorySlug, eraSlug, images)
- `ImageIn` — Image metadata (url, alt, sortOrder)
- `ProductQuery` — Catalog filters and pagination (page, pageSize, search, category, era, sort)
- `AuthIn`, `ChatIn` — Auth and chat bodies
- `ProductOut`, `ProductListOut`, `CategoryOut`, `EraOut`, `MetaOut`, `AuthOut`, `UploadOut`, `ChatOut` — Responses

Reusable field types: `EmailStr` (from pydantic), `Url`, `UtcDatetime` (serializes as ISO 8601 with `Z`).

## Schema patterns

### Request body

```python
class MyThingIn(CamelModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    description: str | None = None
    quantity: Annotated[int, Field(ge=0)] = 0
    status: Literal["active", "archived"]
```

### Query parameters (strings are coerced to int/bool automatically)

```python
class MyThingQuery(CamelModel):
    search: str | None = None
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=48)] = 12   # ?pageSize=...
    status: Literal["active", "archived"] | None = None
```

### Response

```python
class MyThingOut(CamelModel):
    id: int
    name: str
    created_at: UtcDatetime
```

## Using it in a route

```python
from app.schemas import MyThingIn, MyThingOut, MyThingQuery

@router.post("/things", response_model=MyThingOut, status_code=status.HTTP_201_CREATED)
async def create_thing(body: MyThingIn, session: Session) -> Thing:
    thing = Thing(name=body.name, quantity=body.quantity)
    ...

@router.get("/things", response_model=list[MyThingOut])
async def list_things(query: Annotated[MyThingQuery, Query()], session: Session): ...
```

## Validation error response shape

Produced by the handler in `app/main.py`:

```json
{
  "message": "Invalid body",
  "issues": [
    { "path": ["body", "quantity"], "message": "Input should be greater than or equal to 0", "type": "greater_than_equal" }
  ]
}
```

## Common mistakes to avoid

- Do NOT parse `await request.json()` manually — declare the model as a parameter
- Do NOT subclass `BaseModel` directly for API schemas — use `CamelModel` or the JSON casing breaks
- Do NOT define schemas inline in router files — keep them in `schemas.py`
- Do NOT use `HttpUrl` for stored URLs — it normalizes them (e.g. adds a trailing slash); use the `Url` type
