#!/usr/bin/env bash

source venv/bin/activate
env DISCORD_SBRD_TOKEN=$1 python main.py data/config.toml