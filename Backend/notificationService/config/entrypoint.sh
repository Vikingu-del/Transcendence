#!/bin/bash
set -e

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/notification/role_id"
SECRET_ID_FILE="/vault/approle/notification/secret_id"

# Check credentials exist
if [ ! -f "$ROLE_ID_FILE" ] || [ ! -f "$SECRET_ID_FILE" ]; then
    echo "❌ Credentials missing"
    exit 1
fi

ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)
echo "Retrieved AppRole credentials"

# Fix: Correct login path for AppRole authentication
VAULT_TOKEN=$(curl -s --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login | jq -r '.auth.client_token')

if [ -z "$VAULT_TOKEN" ] || [ "$VAULT_TOKEN" = "null" ]; then
    echo "❌ Failed to authenticate with Vault"
    echo "Role ID: $ROLE_ID"
    echo "Response: $(curl -s --request POST \
        --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
        $VAULT_ADDR/v1/auth/approle/login)"
    exit 1
fi
echo "✅ Successfully authenticated with Vault"

# Get secrets
VAULT_RESPONSE=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/notification) 

# Export variables
export DB_USER=$(echo $VAULT_RESPONSE | jq -r .data.data.NOTIFICATION_DB_USER)
export DB_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.NOTIFICATION_DB_PASSWORD)
export DB_NAME=$(echo $VAULT_RESPONSE | jq -r .data.data.NOTIFICATION_DB_NAME)
export DB_HOST=$(echo $VAULT_RESPONSE | jq -r .data.data.NOTIFICATION_DB_HOST)
export DB_PORT=$(echo $VAULT_RESPONSE | jq -r .data.data.NOTIFICATION_DB_PORT)

# Wait for PostgreSQL
MAX_RETRIES=30
count=0
until PGPASSWORD=$DB_PASSWORD pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
    count=$((count + 1))
    if [ $count -eq $MAX_RETRIES ]; then
        echo "❌ Database connection timeout"
        exit 1
    fi
    echo "⏳ Waiting for database... ($count/$MAX_RETRIES)"
    sleep 2
done

echo "✅ Database ready"
python manage.py migrate
exec python manage.py runserver 0.0.0.0:8002
