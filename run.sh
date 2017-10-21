#!/bin/sh

export FLASK_APP=server.py
export FLASK_DEBUG=1

exec flask run