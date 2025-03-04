#!/bin/bash
set -e

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/elasticsearch/role_id"
SECRET_ID_FILE="/vault/approle/elasticsearch/secret_id"

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
    exit 1
fi
echo "✅ Successfully authenticated with Vault"

# Get secrets
VAULT_RESPONSE=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/elasticsearch)
# RESPONSE_JSON=$(echo $VAULT_RESPONSE | jq -r .data.data)
# echo "VAULT_RESPONSE: $RESPONSE_JSON"

# Export variables
export ELASTIC_USERNAME=$(echo $VAULT_RESPONSE | jq -r .data.data.ELASTIC_USERNAME)
export ELASTIC_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.ELASTIC_PASSWORD)
export ELASTICSEARCH_USERNAME=$(echo $VAULT_RESPONSE | jq -r .data.data.ELASTICSEARCH_USERNAME)
export ELASTICSEARCH_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.ELASTICSEARCH_PASSWORD)
/usr/share/elasticsearch/bin/elasticsearch-users useradd $ELASTICSEARCH_USERNAME -p $ELASTICSEARCH_PASSWORD -r kibana_system

exec "/usr/local/bin/docker-entrypoint.sh"