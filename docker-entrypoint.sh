#!/bin/sh

cd /app

# Get the paths for django-admin etc.
source .profile

# Ensure migrations are up to date
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() or \
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')
EOF

# Compile translations
django-admin compilemessages --ignore=.local

# Collect static files
python manage.py collectstatic --noinput

# Generate self signed certificates if necessary
if [ ! -f /app/certs/selfsigned.key ] || [ ! -f /app/certs/selfsigned.crt ] || [ -f /app/certs/selfsigned.cnf ]; then
    if [ -f /app/certs/selfsigned.cnf ] && [ "${HOST_DOMAIN}" == "$(cat /app/certs/selfsigned.cnf)" ]; then
        : # Do nothing, the certificates are already generated and match the current domain
    else
        echo "Generating self signed certificates"
        openssl req -x509 -newkey rsa:4096 -keyout certs/selfsigned.key -out certs/selfsigned.crt -sha256 -days 3650 -nodes -subj "/CN=${HOST_DOMAIN}" > /dev/null 2>&1
        echo "${HOST_DOMAIN}" >certs/selfsigned.cnf
    fi
fi

# Swap out nginx.conf variables with environment variables
envsubst "$(printf '${%s} ' $(env | cut -d'=' -f1))" <templates/nginx.conf >nginx.conf

# Start the proxy
nginx -c nginx.conf -p /app

# Start the server
echo "Starting Daphne server"
exec python manage.py runserver 0.0.0.0:8000
