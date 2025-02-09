#!/bin/bash
set -e

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/gateway/role_id"
SECRET_ID_FILE="/vault/approle/gateway/secret_id"

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

CURRENT_HOST=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/gateway | jq -r .data.data.CURRENT_HOST)
export CURRENT_HOST

# Generate SSL if needed
if [ ! -f /etc/nginx/ssl/nginx-selfsigned.crt ]; then
    openssl req -newkey rsa:2048 -nodes \
        -keyout /etc/nginx/ssl/nginx-selfsigned.key \
        -x509 -days 365 -out /etc/nginx/ssl/nginx-selfsigned.crt \
        -subj "/CN=localhost"
fi

exec nginx -g 'daemon off;'