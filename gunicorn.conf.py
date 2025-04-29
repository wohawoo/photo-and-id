import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.environ.get("PORT", "5000")
backlog = 2048

# Worker processes
workers = 1  # Only use 1 worker due to memory constraints
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

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
preload_app = True
reload = False
reload_engine = 'auto'

# Memory management
max_requests = 100
max_requests_jitter = 10 