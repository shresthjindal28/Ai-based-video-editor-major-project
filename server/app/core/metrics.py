from prometheus_client import Counter, Gauge, Histogram

CACHE = Counter("autocut_cache_total", "Cache outcomes", ["outcome"])
REQUESTS = Histogram("autocut_request_seconds", "HTTP duration", ["method", "status"])
PROCESSES = Counter("autocut_process_total", "Media process outcomes", ["tool", "outcome"])
JOBS = Counter("autocut_job_total", "Job outcomes", ["kind", "outcome"])
DB_TIME = Histogram("autocut_database_seconds", "Database query duration")
JOB_TIME = Histogram("autocut_job_seconds", "Worker attempt duration", ["kind"])
RETRIES = Counter("autocut_job_retries_total", "Worker retries", ["kind"])
QUEUE_DEPTH = Gauge("autocut_queue_depth", "Pending or queued durable jobs")
