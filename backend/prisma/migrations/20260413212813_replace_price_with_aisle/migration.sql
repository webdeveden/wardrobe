/*
  Warnings:

  - You are about to drop the column `price` on the `Product` table. All the data in the column will be lost.

*/
-- DropIndex
DROP INDEX "Product_price_idx";

-- AlterTable
ALTER TABLE "Product" ADD COLUMN "aisle" TEXT;

UPDATE "Product"
SET "aisle" = CASE
  WHEN "slug" = 'victorian-coat' THEN 'A-03'
  WHEN "slug" = 'minimalist-linen-shirt' THEN 'B-11'
  WHEN "slug" = 'bronze-lantern' THEN 'C-07'
  ELSE CONCAT('UNASSIGNED-', "id")
END;

ALTER TABLE "Product"
ALTER COLUMN "aisle" SET NOT NULL,
DROP COLUMN "price";

-- CreateIndex
CREATE INDEX "Product_aisle_idx" ON "Product"("aisle");
