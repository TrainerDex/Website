docker-compose -f ./docker/docker-compose.yml up -d 
pipenv install
pipenv run python ./zapdos/manage.py compilemessages
pipenv run python ./zapdos/manage.py migrate
pipenv run python ./zapdos/manage.py loaddata factions.yaml