"""Fix data models: users.organization_id UUID+FK, rename recruiter_organization columns

Revision ID: a1b2c3d4e5f6
Revises: e5629043858d
Create Date: 2026-02-17

- Alter users.organization_id from VARCHAR to UUID and add FK to organizations.id
- Rename recruiter_organization.userid -> user_id, organizationif -> organization_id
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e5629043858d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) users.organization_id: change type String -> UUID, then add FK
    # Requires existing values to be valid UUIDs (e.g. from organizations.id)
    op.execute(
        "ALTER TABLE users ALTER COLUMN organization_id TYPE UUID USING organization_id::uuid"
    )
    op.create_foreign_key(
        "fk_users_organization_id",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 2) recruiter_organization: rename columns for consistent naming
    op.alter_column(
        "recruiter_organization",
        "userid",
        new_column_name="user_id",
    )
    op.alter_column(
        "recruiter_organization",
        "organizationif",
        new_column_name="organization_id",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_users_organization_id",
        "users",
        type_="foreignkey",
    )
    op.execute(
        "ALTER TABLE users ALTER COLUMN organization_id TYPE VARCHAR USING organization_id::text"
    )

    op.alter_column(
        "recruiter_organization",
        "user_id",
        new_column_name="userid",
    )
    op.alter_column(
        "recruiter_organization",
        "organization_id",
        new_column_name="organizationif",
    )
