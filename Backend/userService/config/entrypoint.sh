#!/bin/bash

# Function to wait for postgres
postgres_ready() {
    nc -z $DB_HOST $DB_PORT
}

until postgres_ready; do
  echo "Database is still unavailable - sleeping"
  sleep 1
done

echo "Database is up - continuing..."

# Run migrations
echo "Running makemigrations..."
python manage.py makemigrations

echo "Running migrate..."
python manage.py migrate

echo "Starting server..."
exec "$@"