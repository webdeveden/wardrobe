"""SQLAlchemy models mapped onto the existing (originally Prisma-created) tables.

Table and column names keep their original camelCase spelling so existing databases
work unchanged; Python attributes use snake_case.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    """Naive UTC timestamp, matching Prisma's TIMESTAMP(3) storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


def _created_at() -> Mapped[datetime]:
    return mapped_column(
        "createdAt",
        TIMESTAMP(precision=3),
        default=utcnow,
        server_default=func.current_timestamp(),
    )


def _updated_at() -> Mapped[datetime]:
    return mapped_column("updatedAt", TIMESTAMP(precision=3), default=utcnow, onupdate=utcnow)


class User(Base):
    __tablename__ = "User"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="User_pkey"),
        Index("User_email_key", "email", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    email: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str] = mapped_column("passwordHash", Text)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="Role"), default=Role.USER, server_default=Role.USER.value
    )
    created_at: Mapped[datetime] = _created_at()
    updated_at: Mapped[datetime] = _updated_at()


class Category(Base):
    __tablename__ = "Category"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="Category_pkey"),
        Index("Category_name_key", "name", unique=True),
        Index("Category_slug_key", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = _created_at()
    updated_at: Mapped[datetime] = _updated_at()

    products: Mapped[list["Product"]] = relationship(back_populates="category", lazy="raise")


class Era(Base):
    __tablename__ = "Era"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="Era_pkey"),
        Index("Era_name_key", "name", unique=True),
        Index("Era_slug_key", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = _created_at()
    updated_at: Mapped[datetime] = _updated_at()

    products: Mapped[list["Product"]] = relationship(back_populates="era", lazy="raise")


class Product(Base):
    __tablename__ = "Product"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="Product_pkey"),
        Index("Product_slug_key", "slug", unique=True),
        Index("Product_categoryId_idx", "categoryId"),
        Index("Product_eraId_idx", "eraId"),
        Index("Product_createdAt_idx", "createdAt"),
        Index("Product_aisle_idx", "aisle"),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    aisle: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    category_id: Mapped[int] = mapped_column(
        "categoryId",
        Integer,
        ForeignKey(
            "Category.id", name="Product_categoryId_fkey", ondelete="RESTRICT", onupdate="CASCADE"
        ),
    )
    era_id: Mapped[int] = mapped_column(
        "eraId",
        Integer,
        ForeignKey("Era.id", name="Product_eraId_fkey", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    created_at: Mapped[datetime] = _created_at()
    updated_at: Mapped[datetime] = _updated_at()

    # lazy="raise" turns accidental N+1 lazy loads into errors; load relations explicitly.
    category: Mapped[Category] = relationship(back_populates="products", lazy="raise")
    era: Mapped[Era] = relationship(back_populates="products", lazy="raise")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        lazy="raise",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="(ProductImage.sort_order, ProductImage.id)",
    )


class ProductImage(Base):
    __tablename__ = "ProductImage"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="ProductImage_pkey"),
        Index("ProductImage_productId_sortOrder_idx", "productId", "sortOrder"),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        "productId",
        Integer,
        ForeignKey(
            "Product.id",
            name="ProductImage_productId_fkey",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
    url: Mapped[str] = mapped_column(Text)
    alt: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0, server_default="0")

    product: Mapped[Product] = relationship(back_populates="images", lazy="raise")
