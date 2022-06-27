import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
preload_app = True
pidfile = 'gunicorn.pid'
wsgi_app = 'app:app'
capture_output = True
# errorlog = 'gunicorn.log'
errorlog = 'STDOUT'
# umask = 0o664
# daemon = True
# threads = 2
# bind = ['unix:gunicorn.sock']
