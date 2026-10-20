"""Enforce edit-version immutability in PostgreSQL.

Revision ID: 0002_immutable_versions
Revises: 0001_initial_domain
"""
from alembic import op

revision = "0002_immutable_versions"
down_revision = "0001_initial_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION autocut_immutable_edit_version() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Edit versions are immutable; create a revision'
                USING ERRCODE = '23514';
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER edit_versions_immutable BEFORE UPDATE ON edit_versions
        FOR EACH ROW EXECUTE FUNCTION autocut_immutable_edit_version()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER edit_versions_immutable ON edit_versions")
    op.execute("DROP FUNCTION autocut_immutable_edit_version()")
