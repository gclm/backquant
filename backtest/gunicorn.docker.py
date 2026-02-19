import os

bind = "0.0.0.0:54321"
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
worker_class = "sync"
worker_connections = int(os.environ.get("GUNICORN_WORKER_CONNECTIONS", "10"))
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
