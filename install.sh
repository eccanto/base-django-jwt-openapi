#!/usr/bin/env bash

set -euo pipefail

GREEN="32"
BOLDGREEN="\e[1;${GREEN}m"
ENDCOLOR="\e[0m"

DEPLOY_ENV=.env

if [[ ! -f "$DEPLOY_ENV" ]]; then
    echo "generating new .env file..."

    DJANGO_SUPERUSER_USERNAME="admin"
    DJANGO_SUPERUSER_PASSWORD=$(pwgen -Bcny 18 -1)
    DJANGO_SUPERUSER_EMAIL="admin@admin.com"
    DJANGO_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

    cat > $DEPLOY_ENV << EOC
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
EOC

    echo -e "${BOLDGREEN}# username: ${DJANGO_SUPERUSER_USERNAME}${ENDCOLOR}"
    echo -e "${BOLDGREEN}# password: ${DJANGO_SUPERUSER_PASSWORD}${ENDCOLOR}"
    echo -e "${BOLDGREEN}# service key: ${DJANGO_SECRET_KEY}${ENDCOLOR}"
else
    echo "the .env file already exists."
fi

docker-compose up --build -d
docker-compose logs -f
