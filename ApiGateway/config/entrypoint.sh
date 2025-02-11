#!/bin/bash
set -e

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/gateway/role_id"
SECRET_ID_FILE="/vault/approle/gateway/secret_id"

# Vault Authentication
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

# Export ModSecurity configuration
export MODSEC_RULE_ENGINE=On
export MODSEC_AUDIT_LOG=/var/log/modsec_audit.log
export MODSEC_CONFIG_DIR=/etc/nginx/modsecurity.d

# Create writable directories for dynamic content
mkdir -p /tmp/nginx/conf
mkdir -p /tmp/nginx/ssl
mkdir -p /tmp/modsecurity/data
mkdir -p /tmp/modsecurity/tmp

# Let the original entrypoint handle template processing
exec /docker-entrypoint.sh nginx -g "daemon off;"