#!/bin/bash

set -e

set -e

# Create media directories if they don't exist
mkdir -p /app/media/avatars

# Ensure default.png exists
if [ ! -f "/app/media/default.png" ]; then
    echo "Error: Default avatar file missing!"
    exit 1
fi

# Set proper permissions
chmod -R 755 /app/media
chmod 644 /app/media/default.png
chmod 755 /app/media/avatars

# Ensure proper ownership
chown -R root:root /app/media
# Ensure proper ownership
chown -R root:root /app/media

# Rest of the script remains unchanged
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