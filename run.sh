#!/usr/bin/env bash

source venv/bin/activate
env DISCORD_SBRD_TOKEN=$1 DISCORD_SBRD_TARGET_CHANNEL='The Lounge' gunicorn -w 1 -k eventlet -b 0.0.0.0:5123 'web_app:create_app()'