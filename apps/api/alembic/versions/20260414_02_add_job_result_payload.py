"""add job result payload and timing fields

Revision ID: 20260414_02
Revises: 20260414_01
Create Date: 2026-04-14 13:00:00
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260414_02"
down_revision = "20260414_01"
branch_labels = None
depends_on = None

SCHEMA = "chat2study"


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("result_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "jobs",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "jobs",
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("jobs", "finished_at", schema=SCHEMA)
    op.drop_column("jobs", "started_at", schema=SCHEMA)
    op.drop_column("jobs", "result_payload", schema=SCHEMA)
