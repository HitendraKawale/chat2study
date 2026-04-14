"""init core tables

Revision ID: 20260414_01
Revises: None
Create Date: 2026-04-14 12:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260414_01"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "chat2study"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_chat2study_users"),
        sa.UniqueConstraint("email", name="uq_chat2study_users_email"),
        schema=SCHEMA,
    )
    op.create_index("ix_chat2study_users_email", "users", ["email"], unique=False, schema=SCHEMA)

    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_domain", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            [f"{SCHEMA}.users.id"],
            name="fk_chat2study_sources_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_chat2study_sources"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_chat2study_sources_user_id", "sources", ["user_id"], unique=False, schema=SCHEMA
    )
    op.create_index(
        "ix_chat2study_sources_source_domain",
        "sources",
        ["source_domain"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "chats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("complexity_score", sa.Integer(), nullable=True),
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
            ["source_id"],
            [f"{SCHEMA}.sources.id"],
            name="fk_chat2study_chats_source_id_sources",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            [f"{SCHEMA}.users.id"],
            name="fk_chat2study_chats_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_chat2study_chats"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_chat2study_chats_user_id", "chats", ["user_id"], unique=False, schema=SCHEMA
    )
    op.create_index(
        "ix_chat2study_chats_source_id", "chats", ["source_id"], unique=False, schema=SCHEMA
    )
    op.create_index("ix_chat2study_chats_status", "chats", ["status"], unique=False, schema=SCHEMA)

    op.create_table(
        "artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artifact_type", sa.String(length=50), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["chat_id"],
            [f"{SCHEMA}.chats.id"],
            name="fk_chat2study_artifacts_chat_id_chats",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_chat2study_artifacts"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_chat2study_artifacts_chat_id", "artifacts", ["chat_id"], unique=False, schema=SCHEMA
    )
    op.create_index(
        "ix_chat2study_artifacts_artifact_type",
        "artifacts",
        ["artifact_type"],
        unique=False,
        schema=SCHEMA,
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
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
            name="fk_chat2study_jobs_chat_id_chats",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_chat2study_jobs"),
        schema=SCHEMA,
    )
    op.create_index("ix_chat2study_jobs_chat_id", "jobs", ["chat_id"], unique=False, schema=SCHEMA)
    op.create_index(
        "ix_chat2study_jobs_job_type", "jobs", ["job_type"], unique=False, schema=SCHEMA
    )
    op.create_index("ix_chat2study_jobs_status", "jobs", ["status"], unique=False, schema=SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_chat2study_jobs_status", table_name="jobs", schema=SCHEMA)
    op.drop_index("ix_chat2study_jobs_job_type", table_name="jobs", schema=SCHEMA)
    op.drop_index("ix_chat2study_jobs_chat_id", table_name="jobs", schema=SCHEMA)
    op.drop_table("jobs", schema=SCHEMA)

    op.drop_index("ix_chat2study_artifacts_artifact_type", table_name="artifacts", schema=SCHEMA)
    op.drop_index("ix_chat2study_artifacts_chat_id", table_name="artifacts", schema=SCHEMA)
    op.drop_table("artifacts", schema=SCHEMA)

    op.drop_index("ix_chat2study_chats_status", table_name="chats", schema=SCHEMA)
    op.drop_index("ix_chat2study_chats_source_id", table_name="chats", schema=SCHEMA)
    op.drop_index("ix_chat2study_chats_user_id", table_name="chats", schema=SCHEMA)
    op.drop_table("chats", schema=SCHEMA)

    op.drop_index("ix_chat2study_sources_source_domain", table_name="sources", schema=SCHEMA)
    op.drop_index("ix_chat2study_sources_user_id", table_name="sources", schema=SCHEMA)
    op.drop_table("sources", schema=SCHEMA)

    op.drop_index("ix_chat2study_users_email", table_name="users", schema=SCHEMA)
    op.drop_table("users", schema=SCHEMA)
