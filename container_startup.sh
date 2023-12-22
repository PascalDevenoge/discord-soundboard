#!/usr/bin/env bash

alembic upgrade head
gunicorn -w 1 -k gthread --threads 4 -b '0.0.0.0:5123' 'web_app:create_app()'