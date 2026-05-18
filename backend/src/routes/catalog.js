import { Router } from "express";
import { prisma } from "../db.js";
import { productQuerySchema } from "../validation/product.js";

export const catalogRouter = Router();

catalogRouter.get("/meta", async (_req, res) => {
  const [categories, eras] = await Promise.all([
    prisma.category.findMany({ orderBy: { name: "asc" } }),
    prisma.era.findMany({ orderBy: { name: "asc" } })
  ]);
  res.json({ categories, eras });
});

catalogRouter.get("/products", async (req, res) => {
  const parsed = productQuerySchema.safeParse(req.query);
  if (!parsed.success) {
    return res.status(400).json({ message: "Invalid query", issues: parsed.error.issues });
  }

  const { page, pageSize, search, category, era, sort } = parsed.data;

  const where = {
    ...(search
      ? {
          OR: [
            { name: { contains: search, mode: "insensitive" } },
            { description: { contains: search, mode: "insensitive" } }
          ]
        }
      : {}),
    ...(category ? { category: { slug: category } } : {}),
    ...(era ? { era: { slug: era } } : {})
  };

  const orderBy =
    sort === "aisle_asc"
      ? { aisle: "asc" }
      : sort === "aisle_desc"
      ? { aisle: "desc" }
      : sort === "name_asc"
      ? { name: "asc" }
      : sort === "name_desc"
      ? { name: "desc" }
      : { createdAt: "desc" };

  const [items, total] = await Promise.all([
    prisma.product.findMany({
      where,
      orderBy,
      skip: (page - 1) * pageSize,
      take: pageSize,
      include: {
        category: true,
        era: true,
        images: { orderBy: { sortOrder: "asc" } }
      }
    }),
    prisma.product.count({ where })
  ]);

  return res.json({
    items,
    total,
    page,
    pageSize,
    totalPages: Math.ceil(total / pageSize)
  });
});

catalogRouter.get("/products/:slug", async (req, res) => {
  const item = await prisma.product.findUnique({
    where: { slug: req.params.slug },
    include: {
      category: true,
      era: true,
      images: { orderBy: { sortOrder: "asc" } }
    }
  });

  if (!item) {
    return res.status(404).json({ message: "Product not found" });
  }

  return res.json(item);
});
