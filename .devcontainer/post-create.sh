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

function copy_env_file_if_not_exists() {
  if [ ! -f .env ]; then
    cp .env.example .env
  fi
}

function install_python_requirements() {
  pip install --user -r requirements.txt
}

function migrate_database() {
  python manage.py migrate
}

function create_superuser() {
  python manage.py createsuperuser --no-input
}

function main() {
  check_if_project_root_exists
  cd $PROJECT_ROOT
  copy_env_file_if_not_exists
  install_python_requirements
  migrate_database
  create_superuser
}

main
