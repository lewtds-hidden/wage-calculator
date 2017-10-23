PORT ?= 5000

run-dev:
	make run FLASK_DEBUG=True

run-prod:
	make run APPLICATION_SETTINGS_FILE=settings_prod.cfg

run:
	FLASK_APP=server.py flask run -p ${PORT}

.PHONY: run run-dev run-prod