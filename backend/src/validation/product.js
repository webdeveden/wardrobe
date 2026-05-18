import { z } from "zod";

export const imageInputSchema = z.object({
  url: z.string().url(),
  alt: z.string().min(1).optional(),
  sortOrder: z.number().int().nonnegative().optional()
});

export const productInputSchema = z.object({
  name: z.string().min(2),
  description: z.string().min(10),
  aisle: z.string().min(1),
  quantity: z.coerce.number().int().nonnegative(),
  categorySlug: z.string().min(2),
  eraSlug: z.string().min(2),
  images: z.array(imageInputSchema).min(1)
});

export const productQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  pageSize: z.coerce.number().int().positive().max(48).default(12),
  search: z.string().optional(),
  category: z.string().optional(),
  era: z.string().optional(),
  sort: z
    .enum(["newest", "aisle_asc", "aisle_desc", "name_asc", "name_desc"])
    .default("newest")
});
