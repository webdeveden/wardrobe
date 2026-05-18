import { mkdirSync } from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { Router } from "express";
import multer from "multer";
import { prisma } from "../db.js";
import { toSlug } from "../lib/slug.js";
import { productInputSchema } from "../validation/product.js";
import { requireAdmin } from "../middleware/auth.js";

export const adminRouter = Router();
adminRouter.use(requireAdmin);

const uploadsDir = path.resolve(process.cwd(), "uploads");
mkdirSync(uploadsDir, { recursive: true });

const upload = multer({
  storage: multer.diskStorage({
    destination: (_req, _file, callback) => {
      callback(null, uploadsDir);
    },
    filename: (_req, file, callback) => {
      const extension = path.extname(file.originalname) || ".bin";
      callback(null, `${Date.now()}-${randomUUID()}${extension}`);
    },
  }),
  fileFilter: (_req, file, callback) => {
    callback(null, file.mimetype.startsWith("image/"));
  },
  limits: {
    files: 10,
    fileSize: 5 * 1024 * 1024,
  },
});

adminRouter.post("/uploads", upload.array("files", 10), (req, res) => {
  const files = Array.isArray(req.files) ? req.files : [];
  const baseUrl = `${req.protocol}://${req.get("host")}`;

  return res.status(201).json({
    files: files.map((file) => ({
      url: `${baseUrl}/uploads/${file.filename}`,
      originalName: file.originalname,
    })),
  });
});

adminRouter.get("/products", async (_req, res) => {
  try {
    const items = await prisma.product.findMany({
      orderBy: { createdAt: "desc" },
      include: {
        category: true,
        era: true,
        images: { orderBy: { sortOrder: "asc" } },
      },
    });
    res.json(items);
  } catch (error) {
    console.error("Error fetching products:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

adminRouter.post("/products", async (req, res) => {
  try {
    const parsed = productInputSchema.safeParse(req.body);
    if (!parsed.success) {
      return res
        .status(400)
        .json({ message: "Invalid body", issues: parsed.error.issues });
    }

    const data = parsed.data;
    const [category, era] = await Promise.all([
      prisma.category.findUnique({ where: { slug: data.categorySlug } }),
      prisma.era.findUnique({ where: { slug: data.eraSlug } }),
    ]);

    if (!category || !era) {
      return res.status(400).json({ message: "Unknown category or era" });
    }

    const created = await prisma.product.create({
      data: {
        name: data.name,
        slug: toSlug(data.name),
        description: data.description,
        aisle: data.aisle,
        quantity: data.quantity,
        categoryId: category.id,
        eraId: era.id,
        images: {
          create: data.images.map((image, index) => ({
            url: image.url,
            alt: image.alt,
            sortOrder: image.sortOrder ?? index,
          })),
        },
      },
      include: {
        category: true,
        era: true,
        images: { orderBy: { sortOrder: "asc" } },
      },
    });

    return res.status(201).json(created);
  } catch (error) {
    console.error("Error creating product:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

adminRouter.put("/products/:id", async (req, res) => {
  try {
    const productId = Number(req.params.id);
    if (Number.isNaN(productId)) {
      return res.status(400).json({ message: "Invalid id" });
    }

    const parsed = productInputSchema.safeParse(req.body);
    if (!parsed.success) {
      return res
        .status(400)
        .json({ message: "Invalid body", issues: parsed.error.issues });
    }

    const data = parsed.data;
    const [category, era] = await Promise.all([
      prisma.category.findUnique({ where: { slug: data.categorySlug } }),
      prisma.era.findUnique({ where: { slug: data.eraSlug } }),
    ]);

    if (!category || !era) {
      return res.status(400).json({ message: "Unknown category or era" });
    }

    const existing = await prisma.product.findUnique({
      where: { id: productId },
    });
    if (!existing) {
      return res.status(404).json({ message: "Product not found" });
    }

    const updated = await prisma.$transaction(async (tx) => {
      await tx.productImage.deleteMany({ where: { productId } });
      return tx.product.update({
        where: { id: productId },
        data: {
          name: data.name,
          slug: toSlug(data.name),
          description: data.description,
          aisle: data.aisle,
          quantity: data.quantity,
          categoryId: category.id,
          eraId: era.id,
          images: {
            create: data.images.map((image, index) => ({
              url: image.url,
              alt: image.alt,
              sortOrder: image.sortOrder ?? index,
            })),
          },
        },
        include: {
          category: true,
          era: true,
          images: { orderBy: { sortOrder: "asc" } },
        },
      });
    });

    return res.json(updated);
  } catch (error) {
    console.error("Error updating product:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

adminRouter.delete("/products/:id", async (req, res) => {
  try {
    const productId = Number(req.params.id);
    if (Number.isNaN(productId)) {
      return res.status(400).json({ message: "Invalid id" });
    }

    const existing = await prisma.product.findUnique({
      where: { id: productId },
    });
    if (!existing) {
      return res.status(404).json({ message: "Product not found" });
    }

    await prisma.product.delete({ where: { id: productId } });
    return res.status(204).send();
  } catch (error) {
    console.error("Error deleting product:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});
