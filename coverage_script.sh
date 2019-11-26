rm coverage.txt
coverage erase
coverage run --source='.' ./ratonGato/manage.py test ratonGato
coverage report -m -i > coverage.txt
