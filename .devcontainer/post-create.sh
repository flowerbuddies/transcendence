#!/bin/bash

# This script runs in the context of the devcontainer when it is created.
# It is used to install dependencies and perform other setup tasks.
# The first parameter passed to the script is the path to the root of the project.

SCRIPT_NAME=$0
PROJECT_ROOT=$1

function check_if_project_root_exists() {
  if [ -z "$PROJECT_ROOT" ]; then
    echo "$SCRIPT_NAME: PROJECT_ROOT variable is empty. Please provide the path to the root of the project (in devcontainer) as the first argument."
    exit 1
  fi
  if [ ! -d "$PROJECT_ROOT" ]; then
    echo "$SCRIPT_NAME: Project root does not exist. Please provide the correct path to the root of the project (in devcontainer) as the first argument."
    exit 1
  fi
}

function install_python_requirements() {
  pip install --user -r requirements.txt
}

function migrate_database() {
  python manage.py migrate
}

function create_superuser() {
  cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() or \
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')
EOF
}

function compile_translation_files() {
  django-admin compilemessages
}

function reset_database_if_flag_exists() {
  if [ -f .flag_reset_db ]; then
    echo "Resetting the database due to .flag_reset_db file (env variables might have changed)."
    python manage.py flush --no-input
    rm .flag_reset_db
  fi
}

function main() {
  check_if_project_root_exists
  cd $PROJECT_ROOT
  source .env
  install_python_requirements
  reset_database_if_flag_exists
  migrate_database
  create_superuser
  compile_translation_files
}

main
