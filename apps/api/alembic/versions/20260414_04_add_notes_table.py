"""add notes table

Revision ID: 20260414_04
Revises: 20260414_03
Create Date: 2026-04-14 15:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260414_04"
down_revision = "20260414_03"
branch_labels = None
depends_on = None

SCHEMA = "chat2study"


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note_type", sa.String(length=50), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=True),
        sa.Column("content_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("model_provider", sa.String(length=50), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["chat_id"],
            [f"{SCHEMA}.chats.id"],
            name="fk_notes_chat_id_chats",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_notes"),
        sa.UniqueConstraint("chat_id", "note_type", name="uq_notes_chat_id_note_type"),
        schema=SCHEMA,
    )
    op.create_index("ix_notes_chat_id", "notes", ["chat_id"], unique=False, schema=SCHEMA)
    op.create_index("ix_notes_note_type", "notes", ["note_type"], unique=False, schema=SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_notes_note_type", table_name="notes", schema=SCHEMA)
    op.drop_index("ix_notes_chat_id", table_name="notes", schema=SCHEMA)
    op.drop_table("notes", schema=SCHEMA)
