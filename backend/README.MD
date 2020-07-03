## Environment setup
```
source env/bin/activate
```

### Hot-reloads for development
```
python manage.py runserver
```

### Compiles for production
```
python manage.py makemessages --no-wrap --ignore=env/* -l de -l es -l fr -l it -l ja -l ko -l pt-br -l zh-hant
```

### Local Production
```
python manage.py collectstatic --clear
python manage.py migrate
python manage.py compilemessages
```
