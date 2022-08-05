pipenv run python manage.py migrate --no-color --noinput -v 3

pipenv run python manage.py compilemessages -v 3 --no-color

pipenv run gunicorn --worker-tmp-dir /dev/shm config.wsgi -w $WORKER_COUNT