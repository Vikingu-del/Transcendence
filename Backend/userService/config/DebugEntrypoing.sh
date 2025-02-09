#!/bin/bash

echo "Retrieving database credentials from Vault..."

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/secrets/user/role_id"
SECRET_ID_FILE="/vault/secrets/user/secret_id"

# Add debug for mounted files
echo "=== Checking mounted files ==="
ls -la /vault/secrets/user/
echo "==========================="

ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)

echo "ROLE_ID = $ROLE_ID, SECRET_ID = $SECRET_ID"

# Get Vault token with debug
echo "=== Getting Vault token ==="
AUTH_RESPONSE=$(curl -s --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login)
echo "Auth Response: $AUTH_RESPONSE"

VAULT_TOKEN=$(echo $AUTH_RESPONSE | jq -r .auth.client_token)
echo "VAULT_TOKEN = $VAULT_TOKEN"
echo "==========================="

# Get secrets with debug
echo "=== Getting secrets ==="
VAULT_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}\n" \
    --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/user)
echo "Vault Response: $VAULT_RESPONSE"
echo "==========================="

# Extract with debug
echo "=== Extracting data ==="
DATA=$(echo "$VAULT_RESPONSE" | sed '/HTTP_STATUS/d' | jq -r .data.data)
echo "Extracted data: $DATA"

# Export with verification
export DB_USER=$(echo "$DATA" | jq -r .DB_USER)
export DB_PASSWORD=$(echo "$DATA" | jq -r .DB_PASSWORD)
export DB_NAME=$(echo "$DATA" | jq -r .DB_NAME)
export DB_HOST=$(echo "$DATA" | jq -r .DB_HOST)
export DB_PORT=$(echo "$DATA" | jq -r .DB_PORT)

echo "DB_USER=$DB_USER"
echo "DB_HOST=$DB_HOST"
echo "DB_PORT=$DB_PORT"
echo "DB_NAME=$DB_NAME"
echo "==========================="

# Test PostgreSQL connection directly
echo "=== Testing PostgreSQL connection ==="
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\conninfo"
echo "==========================="

# Existing wait logic
MAX_RETRIES=30
RETRY_COUNT=0

until PGPASSWORD=$DB_PASSWORD pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Failed to connect to PostgreSQL after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "⏳ Waiting for PostgreSQL... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "✅ PostgreSQL is ready!"
python manage.py migrate
exec python manage.py runserver 0.0.0.0:8000