---
name: prisma-migration
description: Modify the Prisma schema and create a database migration for the Wardrobe Catalog. Use this skill when adding models, columns, relations, indexes, or constraints. Enforces additive-only migrations, correct index placement, and safe deployment practices.
---

# Prisma Migration

Use this skill when the user asks to change the database schema, add a model, add a column, add a relation, or create a migration.

## Checklist — every migration must have all of these

- [ ] Migration is additive — adds or modifies, never removes columns/tables without deliberate data-loss review
- [ ] Foreign keys have `@@index` entries for query performance
- [ ] `@unique` used on slug, email, and any other business-unique fields
- [ ] Timestamps use `@default(now())` for `createdAt` and `@updatedAt` for `updatedAt`
- [ ] Cascade delete configured for records that must not outlive their parent
- [ ] Migration created with `prisma migrate dev`, never by hand-editing SQL
- [ ] Seeder updated if new required fields are added to existing seeded models
- [ ] `prisma migrate status` checked before deploying

## File locations

- Schema: `backend/prisma/schema.prisma`
- Migrations: `backend/prisma/migrations/`
- Seeder: `backend/prisma/seed.js`

## Commands

```bash
# Create a new migration (run from backend/)
bun run prisma migrate dev --name "add-column-to-product"

# Check migration state
bun run prisma migrate status

# Apply migrations in production
bun run prisma migrate deploy

# Inspect data in Prisma Studio
bun run prisma studio

# Re-seed the database
bun run prisma db seed
```

## Existing schema shape

```prisma
model User {
  id           Int      @id @default(autoincrement())
  email        String   @unique
  passwordHash String
  role         Role     @default(USER)
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt
}

model Product {
  id          Int            @id @default(autoincrement())
  name        String
  slug        String         @unique
  description String?
  aisle       String?
  quantity    Int            @default(0)
  categoryId  Int
  eraId       Int
  createdAt   DateTime       @default(now())
  updatedAt   DateTime       @updatedAt
  category    Category       @relation(fields: [categoryId], references: [id])
  era         Era            @relation(fields: [eraId], references: [id])
  images      ProductImage[]

  @@index([categoryId])
  @@index([eraId])
  @@index([createdAt])
  @@index([aisle])
}

model ProductImage {
  id        Int     @id @default(autoincrement())
  productId Int
  url       String
  alt       String?
  sortOrder Int     @default(0)
  product   Product @relation(fields: [productId], references: [id], onDelete: Cascade)

  @@index([productId, sortOrder])
}
```

## Adding a new column (safe pattern)

```prisma
model Product {
  // existing fields ...
  condition String? // nullable = safe to add without a default
}
```

Then run:
```bash
bun run prisma migrate dev --name "add-condition-to-product"
```

## Adding a new model with relations

```prisma
model Tag {
  id       Int       @id @default(autoincrement())
  name     String    @unique
  slug     String    @unique
  products Product[] @relation("ProductTags")
}
```

Add to `Product`:
```prisma
tags Tag[] @relation("ProductTags")
```

## Common mistakes to avoid

- Do NOT edit migration SQL files by hand
- Do NOT add `@unique` to an existing column that has duplicates — clean the data first
- Do NOT add a non-nullable column without a `@default` to a populated table
- Do NOT omit `@@index` on foreign key columns
- Do NOT use `onDelete: Cascade` on the parent side — it belongs on the child relation field
