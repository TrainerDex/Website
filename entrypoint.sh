pipenv run python manage.py migrate --no-color --noinput -v 3

pipenv run gunicorn --worker-tmp-dir /dev/shm config.wsgi