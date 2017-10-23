PORT ?= 5000

run-dev:
	export FLASK_DEBUG=True
	make run

run-prod:
	export APPLICATION_SETTINGS_FILE=settings_prod.cfg
	make run

run:
	pwd
	ls
	export FLASK_APP=server.py
	flask run -p ${PORT}

.PHONY: run run-dev run-prod