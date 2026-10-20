import ssl

from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("autocut-main", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_default_queue=settings.celery_queue,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=settings.max_concurrent_renders,
    task_track_started=True,
    broker_transport_options={"visibility_timeout": settings.process_timeout_seconds + 300,
                              "socket_connect_timeout": 5, "socket_timeout": 5},
    broker_connection_timeout=5,
    task_publish_retry=False,
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
if settings.redis_url.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
    celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
celery_app.autodiscover_tasks(["app.workers"])
