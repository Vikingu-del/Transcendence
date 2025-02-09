#!/bin/bash

set -e

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/user_db/role_id"
SECRET_ID_FILE="/vault/approle/user_db/secret_id"

if [ ! -f "$ROLE_ID_FILE" ] || [ ! -f "$SECRET_ID_FILE" ]; then
    echo "❌ Credentials missing"
    exit 1
fi

ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)
echo "Retrieved AppRole credentials"

VAULT_TOKEN=$(curl -s --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)

if [ -z "$VAULT_TOKEN" ] || [ "$VAULT_TOKEN" = "null" ]; then
    echo "❌ Failed to authenticate with Vault"
    exit 1
fi
echo "✅ Successfully authenticated with Vault"

VAULT_RESPONSE=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/user_db)

export POSTGRES_USER=$(echo $VAULT_RESPONSE | jq -r .data.data.DB_USER)
export POSTGRES_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.DB_PASSWORD)
export POSTGRES_DB=$(echo $VAULT_RESPONSE | jq -r .data.data.DB_NAME)

echo "✅ Retrieved database credentials"
exec docker-entrypoint.sh postgres