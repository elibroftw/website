import multiprocessing
bind = '127.0.0.1:8000'
# bind = ['unix:gunicorn.sock']
workers = multiprocessing.cpu_count() * 2 + 1
preload_app = True
pidfile = 'gunicorn.pid'
wsgi_app = 'app:app'
capture_output = True
# errorlog = 'gunicorn.log'
errorlog = 'STDOUT'
log_level = 'debug'
# umask = 0o664
# daemon = True
# threads = 2
