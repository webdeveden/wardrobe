import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Category, Era, Product
from app.schemas import MetaOut, ProductListOut, ProductOut, ProductQuery
from app.services.products import PRODUCT_LOAD_OPTIONS

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

Session = Annotated[AsyncSession, Depends(get_session)]

SORT_ORDER = {
    "newest": Product.created_at.desc(),
    "aisle_asc": Product.aisle.asc(),
    "aisle_desc": Product.aisle.desc(),
    "name_asc": Product.name.asc(),
    "name_desc": Product.name.desc(),
}


@router.get("/meta", response_model=MetaOut)
async def meta(session: Session) -> MetaOut:
    categories = (await session.scalars(select(Category).order_by(Category.name))).all()
    eras = (await session.scalars(select(Era).order_by(Era.name))).all()
    return MetaOut.model_validate({"categories": categories, "eras": eras})


@router.get("/products", response_model=ProductListOut)
async def list_products(query: Annotated[ProductQuery, Query()], session: Session) -> ProductListOut:
    filters = []
    if query.search:
        filters.append(
            or_(
                Product.name.icontains(query.search, autoescape=True),
                Product.description.icontains(query.search, autoescape=True),
            )
        )
    if query.category:
        filters.append(Product.category.has(Category.slug == query.category))
    if query.era:
        filters.append(Product.era.has(Era.slug == query.era))

    items = (
        await session.scalars(
            select(Product)
            .where(*filters)
            .order_by(SORT_ORDER[query.sort])
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
            .options(*PRODUCT_LOAD_OPTIONS)
        )
    ).all()
    total = await session.scalar(select(func.count()).select_from(Product).where(*filters)) or 0

    return ProductListOut.model_validate(
        {
            "items": items,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": math.ceil(total / query.page_size),
        }
    )


@router.get("/products/{slug}", response_model=ProductOut)
async def get_product(slug: str, session: Session) -> Product:
    product = await session.scalar(
        select(Product).where(Product.slug == slug).options(*PRODUCT_LOAD_OPTIONS)
    )
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product
