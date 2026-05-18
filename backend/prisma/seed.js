import "dotenv/config";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PrismaClient } from "../src/generated/prisma/index.js";
import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL ?? "",
  ssl: {
    rejectUnauthorized: false,
  },
});

const prisma = new PrismaClient({
  adapter: new PrismaPg(pool),
});

/**
 * @typedef {{ name: string, slug: string, description: string, aisle: string, quantity: number, categorySlug: string, eraSlug: string }} MockProduct
 */

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const mockProductsPath = path.join(currentDir, "mock-products.json");

function loadMockProducts() {
  const raw = readFileSync(mockProductsPath, "utf-8");
  const parsed = /** @type {{ products: MockProduct[] }} */ (JSON.parse(raw));
  return parsed.products;
}

async function main() {
  const mockProducts = loadMockProducts();

  await prisma.productImage.deleteMany();
  await prisma.product.deleteMany();
  await prisma.category.deleteMany();
  await prisma.era.deleteMany();

  await Promise.all([
    prisma.era.create({ data: { name: "Modern", slug: "modern" } }),
    prisma.era.create({ data: { name: "Ancient", slug: "ancient" } }),
  ]);

  await Promise.all([
    prisma.category.create({ data: { name: "Clothing", slug: "clothing" } }),
    prisma.category.create({
      data: { name: "Photography Props", slug: "photography-props" },
    }),
  ]);

  const [categories, eras] = await Promise.all([
    prisma.category.findMany(),
    prisma.era.findMany(),
  ]);

  const categoryIdBySlug = new Map(
    categories.map((category) => [category.slug, category.id]),
  );
  const eraIdBySlug = new Map(eras.map((era) => [era.slug, era.id]));

  await prisma.product.createMany({
    data: mockProducts.map((product) => {
      const categoryId = categoryIdBySlug.get(product.categorySlug);
      const eraId = eraIdBySlug.get(product.eraSlug);

      if (!categoryId || !eraId) {
        throw new Error(
          `Unknown category or era slug for product: ${product.slug}`,
        );
      }

      return {
        name: product.name,
        slug: product.slug,
        description: product.description,
        aisle: product.aisle,
        quantity: product.quantity,
        categoryId,
        eraId,
      };
    }),
  });

  const products = await prisma.product.findMany();
  for (const product of products) {
    await prisma.productImage.createMany({
      data: [
        {
          productId: product.id,
          url: `https://picsum.photos/seed/${product.slug}-1/960/1280`,
          alt: `${product.name} hero image`,
          sortOrder: 0,
        },
        {
          productId: product.id,
          url: `https://picsum.photos/seed/${product.slug}-2/960/1280`,
          alt: `${product.name} detail image`,
          sortOrder: 1,
        },
      ],
    });
  }
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (error) => {
    console.error(error);
    await prisma.$disconnect();
    process.exit(1);
  });
