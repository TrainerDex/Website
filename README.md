Django Cities upgrade notes

Step 0: `git stash`
Step 1: `git reset --hard 860ca9b47aec2ba40cd8867fc20c5c8dcb8d884d`
Step 2: `python manage.py migrate website 0006_auto_20171213_1441`
Step 3: `python manage.py migrate website zero --fake`
Step 4: `git reset --hard aa6d4f3df43392ba5dcfa2feaf9fa6d4278ba26b`
Step 5: `pip install -r requirements.txt`
Step 6: `python manage.py migrate website 0001_squashed_0006_auto_20171213_1441 --fake`
Step 7: `python manage.py migrate cities_light zero`
Step 8: `git reset --hard fabfcf4d1faf34c4e8d41998eed0c65a2f80ce9b`
Setp 9: `python manage.py migrate website 0002_auto_20171213_1500`
Step 10: `python manage.py migrate cities`
Step 11: `python manage.py cities --import=all`
Step 12: Step 11 takes a while, make a cup of tea!
Step 13: `git reset --hard master`
Step 14: `git stash --apply`
