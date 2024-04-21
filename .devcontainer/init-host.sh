#!/bin/bash

# This script runs in the context of the host machine when the container is created.
# It is used to perform tasks that are not possible from within the container, or are requirements for the container to run.
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
    echo ".env file does not exist, copying .env.example file to .env."
    cp .env.example .env
  else
    # Check if .env has the required variables, if not, copy the example file
    required_variables=("POSTGRES_HOST" \
                        "POSTGRES_USER" \
                        "POSTGRES_DB" \
                        "POSTGRES_PASSWORD" \
                        "DJANGO_SUPERUSER_EMAIL" \
                        "DJANGO_SUPERUSER_USERNAME" \
                        "DJANGO_SUPERUSER_PASSWORD" \
                        "DJANGO_SECRET_KEY")
    for variable in "${required_variables[@]}"; do
      if ! grep -q "$variable" .env; then
        echo "$variable variable (or more) is missing in .env file, copying .env.example file to .env."
        rm .env
        cp .env.example .env
        break
      fi
    done
  fi
}

main() {
  check_if_project_root_exists
  copy_env_file_if_not_exists
}

main
