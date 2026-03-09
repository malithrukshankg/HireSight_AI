"""Drop public.cvs (moved to cv_schema by cv-service)

Revision ID: d4e5f6g7h8i9
Revises: 2d7f7e8fa1a3
Create Date: 2026-03-09

Gateway no longer owns cvs table. CV data lives in cv_schema.cvs (cv-service).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d4e5f6g7h8i9"
down_revision: Union[str, Sequence[str], None] = "2d7f7e8fa1a3"
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
    """Drop public.cvs if it exists (cv-service migration may have already dropped it)."""
    conn = op.get_bind()
    if _public_cvs_exists(conn):
        op.drop_table("cvs", schema="public")


def downgrade() -> None:
    """Recreate public.cvs with original structure for gateway rollback."""
    conn = op.get_bind()
    if _public_cvs_exists(conn):
        return  # cv-service downgrade may have already recreated it

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
