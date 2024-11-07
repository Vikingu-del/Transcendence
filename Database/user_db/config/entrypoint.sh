#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for the PostgreSQL database to be ready..."
until pg_isready -h localhost -p 5432; do
  echo "PostgreSQL is not ready - sleeping..."
  sleep 1
done

echo "PostgreSQL is up - continuing..."

# Create the database user and database if they do not exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
    END IF;
  END
  \$\$;

  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}') THEN
      CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
    END IF;
  END
  \$\$;
EOSQL

# Run the default entrypoint (to start PostgreSQL)
exec docker-entrypoint.sh postgres