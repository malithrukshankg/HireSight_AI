"""Create cv_schema and migrate cvs from public

Revision ID: a1b2c3d4e5f6
Revises: None
Create Date: 2026-03-09

Moves cvs table from public schema to cv_schema. No cross-schema foreign keys.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _public_cvs_exists(connection) -> bool:
    """Check if public.cvs table exists."""
    result = connection.execute(
        text(
            "SELECT EXISTS("
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'cvs'"
            ") AS exists"
        )
    )
    row = result.fetchone()
    return bool(row[0]) if row else False


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS cv_schema")

    op.create_table(
        "cvs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("candidate_id", sa.UUID(), nullable=False),
        sa.Column("uploaded_by_user_id", sa.UUID(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("file_type", sa.Text(), nullable=False),
        sa.Column("s3_bucket", sa.Text(), nullable=True),
        sa.Column("s3_key", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.Text(), nullable=True),
        sa.Column("content_type", sa.Text(), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column(
            "parsed_profile_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("embedding_version", sa.Text(), nullable=True),
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
        sa.CheckConstraint(
            "file_type IN ('pdf', 'docx')",
            name="ck_cvs_file_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id"),
        schema="cv_schema",
    )

    conn = op.get_bind()
    if _public_cvs_exists(conn):
        conn.execute(
            text("""
                INSERT INTO cv_schema.cvs (
                    id, candidate_id, uploaded_by_user_id, file_name, file_type,
                    s3_bucket, s3_key, original_filename, content_type, size_bytes,
                    uploaded_at, extracted_text, parsed_profile_json, embedding_version,
                    created_at, updated_at
                )
                SELECT
                    id, candidate_id, uploaded_by_user_id, file_name, file_type,
                    s3_bucket, s3_key, original_filename, content_type, size_bytes,
                    uploaded_at, extracted_text, parsed_profile_json, embedding_version,
                    created_at, updated_at
                FROM public.cvs
            """)
        )
        op.drop_table("cvs", schema="public")


def downgrade() -> None:
    op.create_table(
        "cvs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("candidate_id", sa.UUID(), nullable=False),
        sa.Column("uploaded_by_user_id", sa.UUID(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("file_type", sa.Text(), nullable=False),
        sa.Column("s3_bucket", sa.Text(), nullable=True),
        sa.Column("s3_key", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.Text(), nullable=True),
        sa.Column("content_type", sa.Text(), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column(
            "parsed_profile_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("embedding_version", sa.Text(), nullable=True),
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
        sa.CheckConstraint(
            "file_type IN ('pdf', 'docx')",
            name="ck_cvs_file_type",
        ),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id"),
        schema="public",
    )

    conn = op.get_bind()
    conn.execute(
        text("""
            INSERT INTO public.cvs (
                id, candidate_id, uploaded_by_user_id, file_name, file_type,
                s3_bucket, s3_key, original_filename, content_type, size_bytes,
                uploaded_at, extracted_text, parsed_profile_json, embedding_version,
                created_at, updated_at
            )
            SELECT
                id, candidate_id, uploaded_by_user_id, file_name, file_type,
                s3_bucket, s3_key, original_filename, content_type, size_bytes,
                uploaded_at, extracted_text, parsed_profile_json, embedding_version,
                created_at, updated_at
            FROM cv_schema.cvs
        """)
    )

    op.drop_table("cvs", schema="cv_schema")
    op.execute("DROP SCHEMA IF EXISTS cv_schema")
