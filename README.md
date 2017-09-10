This project makes use of [django-colorful 1.2](https://github.com/charettes/django-colorful) and django-rest-framework. 
All API endpoints require an API Token.

# Setup
Install [django-colorful 1.2](https://github.com/charettes/django-colorful) via `pip install django-colorful=1.2`
Run `python manage.py migrate` to generate your database
Run `python manage.py loaddata teams.xml`