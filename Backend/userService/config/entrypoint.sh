#!/bin/bash

set -e

# Create media directories with proper structure
mkdir -p /app/media
mkdir -p /app/media/avatars

# Copy default avatar if it doesn't exist
if [ ! -f "/app/media/default.png" ]; then
    cp /app/config/default.png /app/media/default.png
fi

# Set permissions for media directory structure
# First set directory permissions
chmod 755 /app/media
chmod 755 /app/media/avatars

# Then set file permissions only if files exist
find /app/media -type f -name "*.png" -exec chmod 644 {} +
find /app/media/avatars -type f -exec chmod 644 {} + 2>/dev/null || true

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