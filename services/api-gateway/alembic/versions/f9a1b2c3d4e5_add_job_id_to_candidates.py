"""Add job_id to candidates for job applications

Revision ID: f9a1b2c3d4e5
Revises: d4e5f6g7h8i9
Create Date: 2026-04-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f9a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "d4e5f6g7h8i9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("candidates", sa.Column("job_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_candidates_job_id",
        "candidates",
        "jobs",
        ["job_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_candidates_user_org_job",
        "candidates",
        ["user_id", "organization_id", "job_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_candidates_user_org_job", "candidates", type_="unique")
    op.drop_constraint("fk_candidates_job_id", "candidates", type_="foreignkey")
    op.drop_column("candidates", "job_id")
