from prometheus_client import Counter, Histogram

CACHE = Counter("autocut_cache_total", "Cache outcomes", ["outcome"])
REQUESTS = Histogram("autocut_request_seconds", "HTTP duration", ["method", "status"])
PROCESSES = Counter("autocut_process_total", "Media process outcomes", ["tool", "outcome"])
JOBS = Counter("autocut_job_total", "Job outcomes", ["kind", "outcome"])
DB_TIME = Histogram("autocut_database_seconds", "Database query duration")
