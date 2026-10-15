"""Pydantic request/response schemas. JSON uses camelCase to match the frontend contract."""

from datetime import datetime, timezone
from typing import Annotated, Literal
from urllib.parse import urlparse

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, PlainSerializer
from pydantic.alias_generators import to_camel

from app.models import Role

def _check_url(value: str) -> str:
    parsed = urlparse(value)
    if not parsed.scheme or not (parsed.netloc or parsed.path):
        raise ValueError("Invalid URL")
    return value


def _serialize_datetime(value: datetime) -> str:
    """ISO 8601 in UTC with millisecond precision and a `Z` suffix (what Prisma emitted)."""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(timespec="milliseconds") + "Z"


Url = Annotated[str, AfterValidator(_check_url)]
UtcDatetime = Annotated[datetime, PlainSerializer(_serialize_datetime, return_type=str)]


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# --- Inputs -----------------------------------------------------------------


class ImageIn(CamelModel):
    url: Url
    alt: Annotated[str, Field(min_length=1)] | None = None
    sort_order: Annotated[int, Field(ge=0)] | None = None


class ProductIn(CamelModel):
    name: Annotated[str, Field(min_length=2)]
    description: Annotated[str, Field(min_length=10)]
    aisle: Annotated[str, Field(min_length=1)]
    quantity: Annotated[int, Field(ge=0)]
    category_slug: Annotated[str, Field(min_length=2)]
    era_slug: Annotated[str, Field(min_length=2)]
    images: Annotated[list[ImageIn], Field(min_length=1)]


SortOption = Literal["newest", "aisle_asc", "aisle_desc", "name_asc", "name_desc"]


class ProductQuery(CamelModel):
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=48)] = 12
    search: str | None = None
    category: str | None = None
    era: str | None = None
    sort: SortOption = "newest"


class AuthIn(CamelModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class ChatIn(CamelModel):
    message: Annotated[str, Field(min_length=1, max_length=1000)]


# --- Outputs ----------------------------------------------------------------


class CategoryOut(CamelModel):
    id: int
    name: str
    slug: str
    created_at: UtcDatetime
    updated_at: UtcDatetime


class EraOut(CategoryOut):
    pass


class ProductImageOut(CamelModel):
    id: int
    product_id: int
    url: str
    alt: str | None
    sort_order: int


class ProductOut(CamelModel):
    id: int
    name: str
    slug: str
    description: str
    aisle: str
    quantity: int
    category_id: int
    era_id: int
    created_at: UtcDatetime
    updated_at: UtcDatetime
    category: CategoryOut
    era: EraOut
    images: list[ProductImageOut]


class ProductListOut(CamelModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class MetaOut(CamelModel):
    categories: list[CategoryOut]
    eras: list[EraOut]


class UserOut(CamelModel):
    id: int
    email: str
    role: Role


class AuthOut(CamelModel):
    token: str
    user: UserOut


class UploadedFileOut(CamelModel):
    url: str
    original_name: str


class UploadOut(CamelModel):
    files: list[UploadedFileOut]


class RecommendedProduct(CamelModel):
    id: int
    name: str
    slug: str


class ChatOut(CamelModel):
    reply: str
    recommended_products: list[RecommendedProduct]
