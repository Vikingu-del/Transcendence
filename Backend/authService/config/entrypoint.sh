#!/bin/bash

# Wait for postgres
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
    echo "Postgres is unavailable - sleeping"
    sleep 1
done

echo "Postgres is up - executing command"

# Apply database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser --noinput || true

# Start server
exec "$@"