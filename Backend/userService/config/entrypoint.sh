#!/bin/sh

# Database connection parameters
DB_HOST=${DB_HOST:-db}   # Default is 'db' (your db service name in Docker Compose)
DB_PORT=${DB_PORT:-5432} # Default PostgreSQL port
DB_NAME=${DB_NAME:-your_database_name}
DB_USER=${DB_USER:-your_database_user}
DB_PASSWORD=${DB_PASSWORD:-your_database_password}
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres_password}

# Wait for the database to be ready
echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
until nc -z -v -w30 $DB_HOST $DB_PORT; do
  echo "Waiting for database to be available..."
  sleep 1
done

echo "Database is up and running, proceeding..."

# Create the database user and database if they do not exist
echo "Creating database user and database if they do not exist..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -U $POSTGRES_USER -d postgres -c "DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$\$;"

PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -U $POSTGRES_USER -d postgres -c "DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}') THEN
      CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
   END IF;
END
\$\$;"

# Run database migrations and start the Django application
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000