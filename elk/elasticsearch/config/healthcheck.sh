#!/bin/bash
set -e
echo "[$(date)] Starting Elasticsearch healthcheck..." >> /var/log/elasticsearch/healthcheck.log

# Get credentials from Vault
VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/elasticsearch/role_id"
SECRET_ID_FILE="/vault/approle/elasticsearch/secret_id"

# Check if files exist
if [ ! -f "$ROLE_ID_FILE" ] || [ ! -f "$SECRET_ID_FILE" ]; then
    echo "[$(date)] Missing credential files" >> /var/log/elasticsearch/healthcheck.log
    ls -la /vault/approle/elasticsearch >> /var/log/elasticsearch/healthcheck.log
    exit 1
fi

ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)

mkdir -p /var/log/elasticsearch

echo "[$(date)] Got ROLE_ID=$ROLE_ID" >> /var/log/elasticsearch/healthcheck.log

# Get Vault token
VAULT_TOKEN=$(curl -s --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)

if [ -z "$VAULT_TOKEN" ] || [ "$VAULT_TOKEN" = "null" ]; then
    echo "[$(date)] Failed to get Vault token" >> /var/log/elasticsearch/healthcheck.log
    exit 1
fi

# Get Elasticsearch credentials
ELASTIC_USERNAME=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/elasticsearch | jq -r .data.data.ELASTIC_USERNAME)

ELASTIC_PASSWORD=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/elasticsearch | jq -r .data.data.ELASTIC_PASSWORD)

if [ -z "$ELASTIC_USERNAME" ] || [ "$ELASTIC_USERNAME" = "null" ] || [ -z "$ELASTIC_PASSWORD" ] || [ "$ELASTIC_PASSWORD" = "null" ]; then
    echo "[$(date)] Failed to get Elasticsearch credentials" >> /var/log/elasticsearch/healthcheck.log
    exit 1
fi

echo "[$(date)] Got credentials for user: $ELASTIC_USERNAME" >> /var/log/elasticsearch/healthcheck.log

# Check Elasticsearch health
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" -u "$ELASTIC_USERNAME:$ELASTIC_PASSWORD" http://localhost:9200/_cluster/health?pretty)
EXIT_CODE=$?

if [ "$HEALTH_CHECK" != "200" ]; then
    echo "[$(date)] Elasticsearch health check failed with code: $HEALTH_CHECK" >> /var/log/elasticsearch/healthcheck.log
    exit 1
fi

echo "[$(date)] Elasticsearch health check successful" >> /var/log/elasticsearch/healthcheck.log
exit $EXIT_CODE