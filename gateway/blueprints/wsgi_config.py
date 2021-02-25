import multiprocessing
loglevel = 'debug'
bind = '0.0.0.0:3333'
worker_class = 'gevent'
workers = 1
# workers = multiprocessing.cpu_count() * 2 + 1
threads = multiprocessing.cpu_count() * 2 + 1
preload_app = True # online
worker_connections = 10000
# keepalive = 5
timeout = 120
# reload = True # develop
capture_output = True