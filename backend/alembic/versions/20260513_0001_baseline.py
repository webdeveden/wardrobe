"""Baseline schema (equivalent to the final Prisma migration state).

Databases previously managed by Prisma already have these tables, so this migration
is a no-op for them and only records the revision.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-05-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

role_enum = sa.Enum("USER", "ADMIN", name="Role")


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "createdAt",
            TIMESTAMP(precision=3),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("updatedAt", TIMESTAMP(precision=3), nullable=False),
    ]


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("Product"):
        return

    op.create_table(
        "User",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("passwordHash", sa.Text(), nullable=False),
        sa.Column("role", role_enum, nullable=False, server_default="USER"),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="User_pkey"),
    )
    op.create_index("User_email_key", "User", ["email"], unique=True)

    for table in ("Category", "Era"):
        op.create_table(
            table,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("slug", sa.Text(), nullable=False),
            *_timestamps(),
            sa.PrimaryKeyConstraint("id", name=f"{table}_pkey"),
        )
        op.create_index(f"{table}_name_key", table, ["name"], unique=True)
        op.create_index(f"{table}_slug_key", table, ["slug"], unique=True)

    op.create_table(
        "Product",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("aisle", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("categoryId", sa.Integer(), nullable=False),
        sa.Column("eraId", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="Product_pkey"),
        sa.ForeignKeyConstraint(
            ["categoryId"],
            ["Category.id"],
            name="Product_categoryId_fkey",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["eraId"], ["Era.id"], name="Product_eraId_fkey", ondelete="RESTRICT", onupdate="CASCADE"
        ),
    )
    op.create_index("Product_slug_key", "Product", ["slug"], unique=True)
    op.create_index("Product_categoryId_idx", "Product", ["categoryId"])
    op.create_index("Product_eraId_idx", "Product", ["eraId"])
    op.create_index("Product_createdAt_idx", "Product", ["createdAt"])
    op.create_index("Product_aisle_idx", "Product", ["aisle"])

    op.create_table(
        "ProductImage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("productId", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("alt", sa.Text(), nullable=True),
        sa.Column("sortOrder", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id", name="ProductImage_pkey"),
        sa.ForeignKeyConstraint(
            ["productId"],
            ["Product.id"],
            name="ProductImage_productId_fkey",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
    op.create_index(
        "ProductImage_productId_sortOrder_idx", "ProductImage", ["productId", "sortOrder"]
    )


def downgrade() -> None:
    for table in ("ProductImage", "Product", "Era", "Category", "User"):
        op.drop_table(table)
    role_enum.drop(op.get_bind(), checkfirst=True)
