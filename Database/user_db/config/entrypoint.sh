#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h user_db -p 5432 -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Run the SQL initialization script
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \i /docker-entrypoint-initdb.d/init.sql
EOSQL

# Run the default entrypoint (to start PostgreSQL)
exec docker-entrypoint.sh postgres