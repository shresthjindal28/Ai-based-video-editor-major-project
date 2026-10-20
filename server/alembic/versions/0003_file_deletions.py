"""Durable file cleanup intents committed with domain deletion."""
import sqlalchemy as sa

from alembic import op

revision = "0003_file_deletions"
down_revision = "0002_immutable_versions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("file_deletions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False, unique=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.String(100)),
    )
    op.create_index("ix_file_deletions_available_at", "file_deletions", ["available_at"])


def downgrade() -> None:
    op.drop_table("file_deletions")
