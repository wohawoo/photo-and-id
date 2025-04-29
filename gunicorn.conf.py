import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.environ.get("PORT", "8080")
backlog = 256

# Worker processes
workers = 1  # Single worker for memory constraints
worker_class = 'sync'
worker_connections = 50
timeout = 120
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'

# Process naming
proc_name = 'face-verification-api'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Process management
preload_app = False
reload = False
reload_engine = 'auto'

# Memory management
max_requests = 5  # Recycle workers frequently
max_requests_jitter = 2

# Timeout configuration
graceful_timeout = 120

# Worker configuration
worker_tmp_dir = '/dev/shm'  # Use RAM-based temporary directory
worker_exit_on_app_exit = True

# Limit request line and headers
limit_request_line = 4096
limit_request_fields = 50
limit_request_field_size = 4096 