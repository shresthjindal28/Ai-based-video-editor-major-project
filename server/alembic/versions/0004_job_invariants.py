"""Database-enforced job states and valid lifecycle transitions."""
from alembic import op

revision = "0004_job_invariants"
down_revision = "0003_file_deletions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint("job_status", "edit_jobs",
        "status IN ('pending','queued','processing','completed','failed','cancelling','cancelled')")
    op.create_check_constraint("job_counters", "edit_jobs",
        "progress >= 0 AND progress <= 100 AND retry_count >= 0 AND fence >= 0")
    op.execute("""
        CREATE FUNCTION autocut_job_transition() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.status = NEW.status THEN RETURN NEW; END IF;
            IF (OLD.status = 'pending' AND NEW.status IN ('queued','processing','cancelled','failed'))
            OR (OLD.status = 'queued' AND NEW.status IN ('pending','processing','cancelled','failed'))
            OR (OLD.status = 'processing' AND NEW.status IN ('completed','failed','cancelling','pending'))
            OR (OLD.status = 'cancelling' AND NEW.status IN ('cancelled','failed'))
            OR (OLD.status = 'failed' AND NEW.status = 'pending') THEN RETURN NEW; END IF;
            RAISE EXCEPTION 'Invalid job lifecycle transition' USING ERRCODE = '23514';
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER job_valid_transition BEFORE UPDATE ON edit_jobs
        FOR EACH ROW EXECUTE FUNCTION autocut_job_transition()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER job_valid_transition ON edit_jobs")
    op.execute("DROP FUNCTION autocut_job_transition()")
    op.drop_constraint("job_status", "edit_jobs", type_="check")
    op.drop_constraint("job_counters", "edit_jobs", type_="check")
