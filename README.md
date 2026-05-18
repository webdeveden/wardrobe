# Wardrobe House Catalog

A split web app for managing and presenting wardrobe + photography inventory with an e-commerce style experience.

## Stack

- Frontend: Vue 3, TypeScript, Vite, Tailwind CSS
- Backend: Express, TypeScript, Prisma ORM, Zod
- Database: PostgreSQL
- Package manager/runtime: Bun

## Project Structure

- `frontend`: customer-facing catalog + admin interface
- `backend`: API, validation, and Prisma data access

## 1) Prerequisites

- Bun installed (`bun --version`)
- Docker (optional but recommended for local Postgres)

## 2) Start PostgreSQL

From repository root:

```bash
docker compose up -d
```

## 3) Configure Backend Environment

Copy the example file:

```bash
cd backend
cp .env.example .env
```

## 4) Install Dependencies

```bash
cd backend && bun install
cd ../frontend && bun install
```

## 5) Run Prisma Migration + Seed

```bash
cd backend
bun run prisma:migrate --name init
bun run prisma:seed
```

## 6) Start Applications

Run backend:

```bash
cd backend
bun run dev
```

Run frontend in another terminal:

```bash
cd frontend
bun run dev
```

Frontend runs at `http://localhost:5173` and backend at `http://localhost:4000`.

## Features Implemented

- Product listing grid
- Filter by category and era
- Sort by newest, name, and price
- Search by keyword
- Product detail page with image gallery
- Admin create/update/delete for products

## API Endpoints

- `GET /api/health`
- `GET /api/catalog/meta`
- `GET /api/catalog/products`
- `GET /api/catalog/products/:slug`
- `GET /api/admin/products`
- `POST /api/admin/products`
- `PUT /api/admin/products/:id`
- `DELETE /api/admin/products/:id`
