python manage.py migrate --no-color --noinput -v 3
python manage.py compilemessages -v 3 --no-color
gunicorn --worker-tmp-dir /dev/shm config.asgi -w $WORKER_COUNT -k uvicorn.workers.UvicornWorker --log-level debug --timeout 99
