from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("autocut-main", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=settings.max_concurrent_renders,
    task_track_started=True,
    broker_transport_options={"visibility_timeout": 3600},
    result_expires=3600,
    task_soft_time_limit=settings.process_timeout_seconds,
    task_time_limit=settings.process_timeout_seconds + 60,
    task_default_retry_delay=5,
    task_max_retries=settings.max_job_retries,
    beat_schedule={
        "dispatch-outbox": {"task": "app.workers.tasks.dispatch_outbox", "schedule": 3.0},
        "recover-stale-jobs": {"task": "app.workers.tasks.recover_stale_jobs", "schedule": 60.0},
    },
)
celery_app.autodiscover_tasks(["app.workers"])
