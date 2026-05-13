"""add hashed_password to users

Revision ID: 20260514_05
Revises: 20260414_04
Create Date: 2026-05-14
"""

import sqlalchemy as sa

from alembic import op

revision = "20260514_05"
down_revision = "20260414_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
