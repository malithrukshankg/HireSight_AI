"""Add match score columns to candidates

Revision ID: d5e6f7g8h9i0
Revises: c1d2e3f4a5b6
Create Date: 2026-05-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d5e6f7g8h9i0"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("candidates", sa.Column("match_score", sa.Float(), nullable=True))
    op.add_column("candidates", sa.Column("scores_json", postgresql.JSONB(), nullable=True))
    op.add_column(
        "candidates",
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("candidates", "matched_at")
    op.drop_column("candidates", "scores_json")
    op.drop_column("candidates", "match_score")
