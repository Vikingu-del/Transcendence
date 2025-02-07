#!/bin/bash

echo "Retrieving database credentials from Vault..."

# Vault details
VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/secrets/user_db/role_id"
SECRET_ID_FILE="/vault/secrets/user_db/secret_id"

if [[ ! -f "$ROLE_ID_FILE" || ! -f "$SECRET_ID_FILE" ]]; then
    echo "❌ Role ID or Secret ID file not found!"
    exit 1
fi

ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)

echo "ROLE_ID = $ROLE_ID, SECRET_ID = $SECRET_ID"

VAULT_TOKEN=$(curl -s --request POST --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)
echo "VAULT_TOKEN = $VAULT_TOKEN"

if [[ -z "$VAULT_TOKEN" || "$VAULT_TOKEN" == "null" ]]; then
    echo "❌ Failed to authenticate with Vault"
    exit 1
fi
echo "✅ Successfully authenticated with Vault"

DB_USER=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user_db | jq -r .data.data.DB_USER)
DB_PASSWORD=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user_db | jq -r .data.data.DB_PASSWORD)
DB_NAME=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user_db | jq -r .data.data.DB_NAME)
DB_HOST=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user_db | jq -r .data.data.DB_HOST)
DB_PORT=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user_db | jq -r .data.data.DB_PORT)

if [[ -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_NAME" ]]; then
    echo "❌ Failed to retrieve database credentials from Vault"
    exit 1
fi
echo "✅ Successfully retrieved database credentials from Vault"
echo "DB_USER: $DB_USER, DB_NAME: $DB_NAME, DB_PASSWORD: $DB_PASSWORD, DB_HOST: $DB_HOST, DB_PORT: $DB_PORT"

# Export credentials so Postgres can use them
export POSTGRES_USER="$DB_USER"
export POSTGRES_PASSWORD="$DB_PASSWORD"
export POSTGRES_DB="$DB_NAME"

# Finally, run the default PostgreSQL entrypoint (from the official image) to start the DB
exec /usr/local/bin/docker-entrypoint.sh postgres