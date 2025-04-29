import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8080"
backlog = 256

# Worker processes
workers = 1  # Keep single worker for Railway's free tier memory constraints
worker_class = "sync"
threads = 1
worker_connections = 50

# Timeouts
timeout = 120
graceful_timeout = 120
keepalive = 2

# Memory optimization
max_requests = 5
max_requests_jitter = 2

# Security
limit_request_line = 4096
limit_request_fields = 50
limit_request_field_size = 4096

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "debug"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
capture_output = False

# Process naming
proc_name = "face-verification-api"
default_proc_name = "app:app"

# Directory paths
chdir = "/app"
worker_tmp_dir = "/dev/shm"

# SSL/TLS
forwarded_allow_ips = ["127.0.0.1"]
secure_scheme_headers = {
    "X-FORWARDED-PROTOCOL": "ssl",
    "X-FORWARDED-PROTO": "https",
    "X-FORWARDED-SSL": "on"
}

# Reload
reload = False
reload_engine = "auto"
reload_extra_files = []

# Process management
daemon = False
raw_env = []
pidfile = None
umask = 0
initgroups = False
tmp_upload_dir = None

# User/Group
user = 0
group = 0

# Logging configuration
logger_class = "gunicorn.glogging.Logger"
logconfig = None
logconfig_dict = {}
logconfig_json = None

# Syslog
syslog = False
syslog_addr = "udp://localhost:514"
syslog_prefix = None
syslog_facility = "user"
disable_redirect_access_to_syslog = False

# Misc
spew = False
check_config = False
print_config = False
preload_app = False
sendfile = None
reuse_port = False
enable_stdio_inheritance = False
statsd_host = None
dogstatsd_tags = ""
statsd_prefix = ""

def on_starting(server):
    """
    Hook function called when the server starts.
    Use this to configure any additional settings or perform startup tasks.
    """
    # Ensure upload directory exists
    os.makedirs("/dev/shm/face_verification", mode=0o755, exist_ok=True)

def worker_int(worker):
    """
    Hook function called when a worker is interrupted.
    Use this to perform cleanup tasks.
    """
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """
    Hook function called when a worker is aborted.
    Use this to perform emergency cleanup tasks.
    """
    worker.log.info("worker received SIGABRT signal") 