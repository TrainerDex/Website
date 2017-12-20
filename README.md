# Django Cities upgrade notes

* `python manage.py migrate enrollments zero`
* `git stash`
* `git reset --hard 860ca9b47aec2ba40cd8867fc20c5c8dcb8d884d`
* `python manage.py migrate website 0006_auto_20171213_1441`
* `python manage.py migrate website zero --fake`
* `git reset --hard aa6d4f3df43392ba5dcfa2feaf9fa6d4278ba26b`
* `pip install -r requirements.txt`
* `python manage.py migrate website 0001_squashed_0006_auto_20171213_1441 --fake`
* Temporarilly add cities_light to settings.py
* `python manage.py migrate cities_light zero`
* `git reset --hard fabfcf4d1faf34c4e8d41998eed0c65a2f80ce9b`
* `python manage.py migrate website 0002_auto_20171213_1500`
* `python manage.py migrate cities`
* `sudo nano ekpogo/settings.py`

```
CITIES_LOCALES = ['en']
CITIES_POSTAL_CODES = []
```

* `python manage.py cities --import=all`
  * This takes a while, make a cup of tea!
* `git reset --hard master`
* `git stash --apply`
* `python manage.py migrate`
* `sudo rm -r static`
* `python manage.py collectstatic`
