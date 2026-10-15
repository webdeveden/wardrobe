---
name: alembic-migration
description: Modify the SQLAlchemy models and create an Alembic database migration for the Wardrobe Catalog. Use this skill when adding models, columns, relations, indexes, or constraints. Enforces additive-only migrations, correct index placement, Prisma-compatible naming, and safe deployment practices.
---

# Alembic Migration

Use this skill when the user asks to change the database schema, add a model, add a column, add a relation, or create a migration.

## Checklist — every migration must have all of these

- [ ] Migration is additive — adds or modifies, never removes columns/tables without deliberate data-loss review
- [ ] Foreign keys have an `Index(...)` in `__table_args__`
- [ ] Unique indexes on slug, email, and other business-unique fields
- [ ] New tables follow the existing naming: PascalCase table, camelCase columns, `<Table>_pkey`, `<Table>_<col>_key`, `<Table>_<col>_idx`, `<Table>_<col>_fkey`
- [ ] Timestamps use `_created_at()` / `_updated_at()` helpers from `models.py`
- [ ] Cascade delete configured (`ondelete="CASCADE"` on the child FK, `cascade="all, delete-orphan"` + `passive_deletes=True` on the parent relationship)
- [ ] New relationships declared with `lazy="raise"`
- [ ] Revision created with `--autogenerate` and then **reviewed by hand** (autogenerate misses some changes, e.g. enum values)
- [ ] `alembic upgrade head` and `alembic downgrade -1` both tested locally
- [ ] `app/seed.py` updated if new required fields are added to seeded models

## File locations

- Models: `backend/app/models.py`
- Migrations: `backend/alembic/versions/`
- Alembic env: `backend/alembic/env.py` (reads `DATABASE_URL` via `app.config.settings`)
- Seeder: `backend/app/seed.py`

## Commands (run from `backend/` with the venv active)

```bash
# Create a new migration after editing models.py
alembic revision --autogenerate -m "add condition to product"

# Apply / inspect
alembic upgrade head
alembic current
alembic check          # fails if models and DB have drifted

# Roll back one step
alembic downgrade -1

# Re-seed
python -m app.seed

# In Docker (migrations also run automatically on container start)
docker compose exec backend alembic upgrade head
```

## Existing schema shape

```text
User         (id, email, passwordHash, role: Role[USER|ADMIN], createdAt, updatedAt)  unique: email
Category     (id, name, slug, createdAt, updatedAt)                                     unique: name, slug
Era          (id, name, slug, createdAt, updatedAt)                                     unique: name, slug
Product      (id, name, slug, description, aisle, quantity, categoryId, eraId, createdAt, updatedAt)
             unique: slug; indexes: categoryId, eraId, createdAt, aisle
ProductImage (id, productId → Product ON DELETE CASCADE, url, alt?, sortOrder)
             index: (productId, sortOrder)
```

## Adding a new column (safe pattern)

```python
class Product(Base):
    # existing fields ...
    condition: Mapped[str | None] = mapped_column(Text, nullable=True)  # nullable = safe on populated tables
```

Then:

```bash
alembic revision --autogenerate -m "add condition to product"
```

## Adding a new model with a relation

```python
class Tag(Base):
    __tablename__ = "Tag"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="Tag_pkey"),
        Index("Tag_slug_key", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(Text)
```

## Common mistakes to avoid

- Do NOT change the database by hand — always go through a revision
- Do NOT edit a revision that has already been applied anywhere; add a new one
- Do NOT add a unique index to a column that currently has duplicates — clean the data first
- Do NOT add a non-nullable column to a populated table without a `server_default`
- Do NOT omit indexes on foreign key columns
- Do NOT rename existing tables/columns to snake_case — the DB keeps its original Prisma-era names
