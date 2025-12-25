"""Gunicorn configuration for production."""
import multiprocessing

# Bind to localhost (Cloudflare Tunnel will connect here)
bind = "127.0.0.1:8000"

# Workers: 2 * CPU cores + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout (increase for AI processing)
timeout = 180

# Logging
accesslog = "/home/astre/command-center/testhome/testhome-visualizer/logs/gunicorn-access.log"
errorlog = "/home/astre/command-center/testhome/testhome-visualizer/logs/gunicorn-error.log"
loglevel = "info"

# Process naming
proc_name = "visualizer"

# Reload on code changes (disable in production)
reload = False

# Preload app for faster worker spawning
preload_app = True
