"""Create the initial AutoCut application schema.

Revision ID: 0001_initial_domain
Revises:
Create Date: 2026-10-20
"""

import app.db.models  # noqa: F401
from alembic import op
from app.db.base import Base

revision = "0001_initial_domain"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=True)
