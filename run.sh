#!/usr/bin/env bash

source venv/bin/activate
env DISCORD_SBRD_TOKEN=$1 DISCORD_SBRD_TARGET_CHANNEL='The Lounge' gunicorn -w 1 --threads 4 -k gthread -b 127.0.0.1:5123 'web_app:create_app()'