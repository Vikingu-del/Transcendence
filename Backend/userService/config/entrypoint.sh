#!/bin/sh

# Wait until PostgreSQL is ready
echo "Waiting for the database to be ready..."

while ! nc -z $DB_HOST 5432; do
  echo "Database is still unavailable - sleeping"
  sleep 1
done

echo "Database is up - continuing..."

# Run database migrations
echo "Running makemigrations..."
python3 manage.py makemigrations
echo "Running migrate..."
python3 manage.py migrate

# Start the Django development server
echo "Starting Django server..."
exec "$@"