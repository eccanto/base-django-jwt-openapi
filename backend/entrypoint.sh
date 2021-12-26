#!/usr/bin/env bash

set -euo pipefail

python3 manage.py makemigrations ecommerce
python3 manage.py migrate
python3 manage.py createsuperuser --no-input || true

exec "$@"
