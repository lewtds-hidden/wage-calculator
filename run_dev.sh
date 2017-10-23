#!/bin/sh

export FLASK_DEBUG=True
exec flask run "$@"