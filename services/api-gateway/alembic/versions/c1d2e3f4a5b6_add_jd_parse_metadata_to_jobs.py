"""Add JD parse metadata columns to jobs

Revision ID: c1d2e3f4a5b6
Revises: b7c8d9e0f1a2
Create Date: 2026-04-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("jd_content_hash", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("jd_parse_version", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("jd_model_version", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("jd_prompt_version", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("jd_parsed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "jd_parsed_at")
    op.drop_column("jobs", "jd_prompt_version")
    op.drop_column("jobs", "jd_model_version")
    op.drop_column("jobs", "jd_parse_version")
    op.drop_column("jobs", "jd_content_hash")
