"""Create the User table on databases that predate Prisma's `add_users` migration.

0001_baseline skips entirely when "Product" exists, which assumed a fully migrated
Prisma database. Databases stopped after `replace_price_with_aisle` have products but
no users; this fills that gap and is a no-op everywhere else.

Revision ID: 0002_ensure_user_table
Revises: 0001_baseline
Create Date: 2026-10-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_ensure_user_table"
down_revision: str | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if sa.inspect(bind).has_table("User"):
        return

    role_enum = postgresql.ENUM("USER", "ADMIN", name="Role")
    role_enum.create(bind, checkfirst=True)

    op.create_table(
        "User",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("passwordHash", sa.Text(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("USER", "ADMIN", name="Role", create_type=False),
            nullable=False,
            server_default="USER",
        ),
        sa.Column(
            "createdAt",
            postgresql.TIMESTAMP(precision=3),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("updatedAt", postgresql.TIMESTAMP(precision=3), nullable=False),
        sa.PrimaryKeyConstraint("id", name="User_pkey"),
    )
    op.create_index("User_email_key", "User", ["email"], unique=True)


def downgrade() -> None:
    # The table may have been created by 0001 or by Prisma; dropping it here would lose users.
    pass
