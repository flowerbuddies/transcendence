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
django-admin compilemessages

# Start the server
exec python manage.py runserver 0.0.0.0:8000
