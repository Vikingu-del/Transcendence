#!/bin/sh

# Wait until PostgreSQL is ready
echo "Waiting for the database to be ready..."

while ! nc -z $DB_HOST $DB_PORT; do
  echo "Database with host $DB_HOST in port $DB_PORT is still unavailable - sleeping"
  sleep 1
done

# echo "${POSTGRES_PASSWORD}"

echo "Database is up - continuing..."

# Run database migrations (optional)
python3 manage.py makemigrations
python3 manage.py migrate

# Start the Django development server
python3 manage.py runserver 0.0.0.0:8000
