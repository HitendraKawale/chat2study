"""add chunks table

Revision ID: 20260414_03
Revises: 20260414_02
Create Date: 2026-04-14 14:00:00
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.dialects import postgresql

revision = "20260414_03"
down_revision = "20260414_02"
branch_labels = None
depends_on = None

SCHEMA = "chat2study"
EMBEDDING_DIMENSIONS = 768


def upgrade() -> None:
    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("embedding_provider", sa.String(length=50), nullable=False),
        sa.Column("embedding_model", sa.String(length=255), nullable=False),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=False),
        sa.Column("embedding", VECTOR(EMBEDDING_DIMENSIONS), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["chat_id"],
            [f"{SCHEMA}.chats.id"],
            name="fk_chunks_chat_id_chats",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_chunks"),
        schema=SCHEMA,
    )
    op.create_index("ix_chunks_chat_id", "chunks", ["chat_id"], unique=False, schema=SCHEMA)
    op.create_index("ix_chunks_ordinal", "chunks", ["ordinal"], unique=False, schema=SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_chunks_ordinal", table_name="chunks", schema=SCHEMA)
    op.drop_index("ix_chunks_chat_id", table_name="chunks", schema=SCHEMA)
    op.drop_table("chunks", schema=SCHEMA)
