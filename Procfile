release: python manage.py migrate

web: gunicorn SungemBackend.wsgi --log-file -

worker: python manage.py rqworker default