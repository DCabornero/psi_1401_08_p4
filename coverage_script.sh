rm coverage.txt
coverage erase
coverage run --source='.' ./ratonGato/manage.py test logic.tests_additional_P4 logic.tests_function logic.tests_services_P4 datamodel.tests_models
coverage report -m -i > coverage.txt
