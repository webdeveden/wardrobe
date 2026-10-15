"""Product embeddings, cached in memory, and cosine-similarity semantic search."""

import asyncio
import logging
import math
from dataclasses import dataclass

from sqlalchemy import select

from app.config import settings
from app.db import SessionLocal
from app.models import Product
from app.services.llm import get_llm_client
from app.services.products import PRODUCT_LOAD_OPTIONS

logger = logging.getLogger(__name__)

EMBEDDING_BATCH_SIZE = 64


@dataclass(frozen=True)
class ProductEmbedding:
    product_id: int
    embedding: list[float]
    text: str


@dataclass(frozen=True)
class RelevantProduct:
    product: Product
    similarity: float


_cache: list[ProductEmbedding] | None = None
# Bumped on invalidation so an in-flight rebuild doesn't store stale results.
_generation = 0
_lock = asyncio.Lock()


def invalidate_product_embeddings() -> None:
    """Drop the cache after catalog changes; it's rebuilt lazily on the next search."""
    global _cache, _generation
    _cache = None
    _generation += 1


def _product_text(product: Product) -> str:
    return (
        f"Product: {product.name}\n"
        f"Description: {product.description}\n"
        f"Category: {product.category.name}\n"
        f"Era: {product.era.name}\n"
        f"Aisle: {product.aisle}\n"
        f"Quantity: {product.quantity}"
    )


async def get_product_embeddings() -> list[ProductEmbedding]:
    """Embed every product once and cache the result for the lifetime of the process."""
    global _cache
    if _cache is not None:
        return _cache

    async with _lock:
        if _cache is not None:
            return _cache
        generation = _generation

        logger.info("Generating product embeddings...")
        async with SessionLocal() as session:
            products = (await session.scalars(select(Product).options(*PRODUCT_LOAD_OPTIONS))).all()

        client = get_llm_client()
        embeddings: list[ProductEmbedding] = []
        for start in range(0, len(products), EMBEDDING_BATCH_SIZE):
            batch = products[start : start + EMBEDDING_BATCH_SIZE]
            texts = [_product_text(p) for p in batch]
            try:
                response = await client.embeddings.create(model=settings.embedding_model, input=texts)
            except Exception:
                logger.exception("Failed to embed products %s", [p.id for p in batch])
                continue
            for product, text, item in zip(batch, texts, response.data):
                embeddings.append(ProductEmbedding(product.id, item.embedding, text))

        logger.info("Generated embeddings for %d products", len(embeddings))
        # Don't pin an empty result (e.g. DB not seeded yet at startup); retry on next search.
        if generation == _generation and embeddings:
            _cache = embeddings
        return embeddings


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot / (magnitude_a * magnitude_b)


async def find_relevant_products(query: str, top_k: int = 5) -> list[RelevantProduct]:
    """Top-k products by cosine similarity to `query`. Returns [] on any failure."""
    try:
        response = await get_llm_client().embeddings.create(
            model=settings.embedding_model, input=query
        )
        query_embedding = response.data[0].embedding
        product_embeddings = await get_product_embeddings()

        ranked = sorted(
            ((pe.product_id, cosine_similarity(query_embedding, pe.embedding)) for pe in product_embeddings),
            key=lambda item: item[1],
            reverse=True,
        )[:top_k]

        async with SessionLocal() as session:
            products = (
                await session.scalars(
                    select(Product)
                    .where(Product.id.in_([product_id for product_id, _ in ranked]))
                    .options(*PRODUCT_LOAD_OPTIONS)
                )
            ).all()
        by_id = {p.id: p for p in products}

        return [
            RelevantProduct(by_id[product_id], similarity)
            for product_id, similarity in ranked
            if product_id in by_id
        ]
    except Exception:
        logger.exception("Error finding relevant products")
        return []
