import multiprocessing

# ✅ Bind to all available network interfaces (IPv4 & IPv6)
bind = "0.0.0.0:5000"

# ✅ Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# ✅ Enable threaded workers for handling multiple requests
threads = 2

# ✅ Use an async worker class for better concurrency
worker_class = "gthread"

# ✅ Set request timeout to prevent long-running requests
timeout = 120

# ✅ Preload the application for faster startup
preload_app = True

# ✅ Enable access logging
accesslog = "-"

# ✅ Enable error logging
errorlog = "-"

# ✅ Set log level (options: debug, info, warning, error, critical)
loglevel = "info"

# ✅ Optional: Customize access log format
access_log_format = '%(h)s %(l)s %(u)s [%(t)s] "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
