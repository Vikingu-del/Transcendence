#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h user_db -p 5432 -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Start the Django server
echo "Starting server..."
exec "$@"