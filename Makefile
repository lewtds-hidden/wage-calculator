PORT ?= 5000

run:
	flask run -p ${PORT}

run-dev:
	export FLASK_DEBUG=True
	make run

run-prod:
	export APPLICATION_SETTINGS_FILE=settings_prod.cfg
	make run