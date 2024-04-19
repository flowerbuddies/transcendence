#!/bin/sh

cd /app

python3 manage.py makemigrations
python3 manage.py migrate

cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() or \
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')
EOF

django-admin compilemessages

exec python3 manage.py runserver 0.0.0.0:8000
