import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.environ.get("PORT", "8080")
backlog = 2048

# Worker processes
workers = 1  # Only use 1 worker due to memory constraints
worker_class = 'sync'
worker_connections = 1000
timeout = 600  # Increased timeout to 10 minutes
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'  # Changed to debug for more detailed logs

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
preload_app = False  # Changed to False to prevent memory issues
reload = False
reload_engine = 'auto'

# Memory management
max_requests = 10  # Reduced to recycle workers more frequently
max_requests_jitter = 3

# Timeout configuration
graceful_timeout = 300
timeout = 600

# Worker configuration
worker_tmp_dir = '/dev/shm'  # Use RAM-based temporary directory
worker_exit_on_app_exit = True 