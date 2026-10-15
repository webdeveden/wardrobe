"""Reset catalog data and load mock products. Run with `python -m app.seed`."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import delete, select

from app.db import SessionLocal, engine
from app.models import Category, Era, Product, ProductImage

MOCK_PRODUCTS_PATH = Path(__file__).parent / "data" / "mock-products.json"

ERAS = [("Modern", "modern"), ("Ancient", "ancient")]
CATEGORIES = [("Clothing", "clothing"), ("Photography Props", "photography-props")]


async def main() -> None:
    mock_products = json.loads(MOCK_PRODUCTS_PATH.read_text(encoding="utf-8"))["products"]

    async with SessionLocal() as session, session.begin():
        for model in (ProductImage, Product, Category, Era):
            await session.execute(delete(model))

        session.add_all(Era(name=name, slug=slug) for name, slug in ERAS)
        session.add_all(Category(name=name, slug=slug) for name, slug in CATEGORIES)
        await session.flush()

        category_ids = dict((await session.execute(select(Category.slug, Category.id))).tuples().all())
        era_ids = dict((await session.execute(select(Era.slug, Era.id))).tuples().all())

        for item in mock_products:
            category_id = category_ids.get(item["categorySlug"])
            era_id = era_ids.get(item["eraSlug"])
            if category_id is None or era_id is None:
                raise ValueError(f"Unknown category or era slug for product: {item['slug']}")

            session.add(
                Product(
                    name=item["name"],
                    slug=item["slug"],
                    description=item["description"],
                    aisle=item["aisle"],
                    quantity=item["quantity"],
                    category_id=category_id,
                    era_id=era_id,
                    images=[
                        ProductImage(
                            url=f"https://picsum.photos/seed/{item['slug']}-1/960/1280",
                            alt=f"{item['name']} hero image",
                            sort_order=0,
                        ),
                        ProductImage(
                            url=f"https://picsum.photos/seed/{item['slug']}-2/960/1280",
                            alt=f"{item['name']} detail image",
                            sort_order=1,
                        ),
                    ],
                )
            )

    await engine.dispose()
    print(f"Seeded {len(mock_products)} products")


if __name__ == "__main__":
    asyncio.run(main())
