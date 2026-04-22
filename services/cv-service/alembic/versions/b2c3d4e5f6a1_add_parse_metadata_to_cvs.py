"""Add parse metadata columns to cv_schema.cvs

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-04-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("cvs", sa.Column("content_hash", sa.Text(), nullable=True), schema="cv_schema")
    op.add_column("cvs", sa.Column("parse_version", sa.Text(), nullable=True), schema="cv_schema")
    op.add_column("cvs", sa.Column("model_version", sa.Text(), nullable=True), schema="cv_schema")
    op.add_column("cvs", sa.Column("prompt_version", sa.Text(), nullable=True), schema="cv_schema")
    op.add_column("cvs", sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True), schema="cv_schema")


def downgrade() -> None:
    op.drop_column("cvs", "parsed_at", schema="cv_schema")
    op.drop_column("cvs", "prompt_version", schema="cv_schema")
    op.drop_column("cvs", "model_version", schema="cv_schema")
    op.drop_column("cvs", "parse_version", schema="cv_schema")
    op.drop_column("cvs", "content_hash", schema="cv_schema")
