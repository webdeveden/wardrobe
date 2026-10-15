import time
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile

from app.config import settings
from app.db import get_session
from app.models import Category, Era, Product, ProductImage
from app.schemas import ProductIn, ProductOut, UploadedFileOut, UploadOut
from app.security import require_admin
from app.services.embeddings import invalidate_product_embeddings
from app.services.products import PRODUCT_LOAD_OPTIONS
from app.services.slug import to_slug

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])

Session = Annotated[AsyncSession, Depends(get_session)]

MAX_FILES = 10
MAX_FILE_SIZE = 5 * 1024 * 1024
# Only keep extensions that browsers will treat as images; anything else is stored as .bin
# so an upload can't be served back as HTML/JS from our origin.
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".bmp"}
CHUNK_SIZE = 1024 * 1024


def _stored_filename(original_name: str) -> str:
    extension = Path(original_name).suffix.lower()
    if extension not in IMAGE_EXTENSIONS:
        extension = ".bin"
    return f"{int(time.time() * 1000)}-{uuid.uuid4()}{extension}"


async def _save_upload(upload: UploadFile, destination: Path) -> None:
    with destination.open("wb") as out:
        while chunk := await upload.read(CHUNK_SIZE):
            out.write(chunk)


@router.post(
    "/uploads",
    response_model=UploadOut,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "files": {"type": "array", "items": {"type": "string", "format": "binary"}}
                        },
                    }
                }
            }
        }
    },
)
async def upload_images(request: Request) -> UploadOut:
    # The form is parsed here (after require_admin ran) rather than via a File() param,
    # which FastAPI would parse before the auth dependency.
    async with request.form(max_files=MAX_FILES) as form:
        uploads = [f for f in form.getlist("files") if isinstance(f, UploadFile)]
        # Non-image files are skipped silently, as multer's fileFilter did.
        images = [f for f in uploads if (f.content_type or "").startswith("image/")]

        for upload in images:
            if upload.size is not None and upload.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    f"{upload.filename} exceeds the 5MB limit",
                )

        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        base_url = str(request.base_url).rstrip("/")
        saved: list[UploadedFileOut] = []
        for upload in images:
            filename = _stored_filename(upload.filename or "")
            await _save_upload(upload, settings.uploads_dir / filename)
            saved.append(
                UploadedFileOut(url=f"{base_url}/uploads/{filename}", original_name=upload.filename or "")
            )

    return UploadOut(files=saved)


@router.get("/products", response_model=list[ProductOut])
async def list_products(session: Session) -> list[Product]:
    return list(
        (
            await session.scalars(
                select(Product).order_by(Product.created_at.desc()).options(*PRODUCT_LOAD_OPTIONS)
            )
        ).all()
    )


async def _resolve_category_and_era(session: AsyncSession, body: ProductIn) -> tuple[Category, Era]:
    category = await session.scalar(select(Category).where(Category.slug == body.category_slug))
    era = await session.scalar(select(Era).where(Era.slug == body.era_slug))
    if category is None or era is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown category or era")
    return category, era


def _apply(product: Product, body: ProductIn, category: Category, era: Era) -> None:
    product.name = body.name
    product.slug = to_slug(body.name)
    product.description = body.description
    product.aisle = body.aisle
    product.quantity = body.quantity
    product.category_id = category.id
    product.era_id = era.id
    product.images = [
        ProductImage(
            url=image.url,
            alt=image.alt,
            sort_order=image.sort_order if image.sort_order is not None else index,
        )
        for index, image in enumerate(body.images)
    ]


async def _commit_product(session: AsyncSession, product_id: int) -> Product:
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A product with this name (slug) already exists"
        ) from None
    invalidate_product_embeddings()
    session.expunge_all()
    product = await session.scalar(
        select(Product).where(Product.id == product_id).options(*PRODUCT_LOAD_OPTIONS)
    )
    assert product is not None
    return product


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductIn, session: Session) -> Product:
    category, era = await _resolve_category_and_era(session, body)
    product = Product()
    _apply(product, body, category, era)
    session.add(product)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A product with this name (slug) already exists"
        ) from None
    return await _commit_product(session, product.id)


@router.put("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, body: ProductIn, session: Session) -> Product:
    category, era = await _resolve_category_and_era(session, body)
    product = await session.scalar(
        select(Product).where(Product.id == product_id).options(*PRODUCT_LOAD_OPTIONS)
    )
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

    # Replacing the collection deletes the old images (delete-orphan) in the same transaction.
    _apply(product, body, category, era)
    return await _commit_product(session, product_id)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: Session) -> Response:
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

    await session.delete(product)
    await session.commit()
    invalidate_product_embeddings()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
