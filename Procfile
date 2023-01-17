release: python manage.py migrate
web: gunicorn config.wsgi
worker: celery -A config worker -B --without-gossip --without-mingle --without-heartbeat -l INFO --concurrency 2