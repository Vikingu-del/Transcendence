#!/bin/bash
set -e
echo "[$(date)] Starting healthcheck..." >> /var/log/postgresql/healthcheck.log

# Get credentials from Vault
VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/user_db/role_id"
SECRET_ID_FILE="/vault/approle/user_db/secret_id"

# Check if files exist
if [ ! -f "$ROLE_ID_FILE" ] || [ ! -f "$SECRET_ID_FILE" ]; then
    echo "[$(date)] Missing credential files" >> /var/log/postgresql/healthcheck.log
    ls -la /vault/approle/user_db >> /var/log/postgresql/healthcheck.log
    exit 1
fi

ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)

echo "[$(date)] Got ROLE_ID=$ROLE_ID" >> /var/log/postgresql/healthcheck.log

# Get Vault token
VAULT_TOKEN=$(curl -s --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)

if [ -z "$VAULT_TOKEN" ] || [ "$VAULT_TOKEN" = "null" ]; then
    echo "[$(date)] Failed to get Vault token" >> /var/log/postgresql/healthcheck.log
    exit 1
fi

# Get DB credentials
DB_USER=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/user_db | jq -r .data.data.DB_USER)

if [ -z "$DB_USER" ] || [ "$DB_USER" = "null" ]; then
    echo "[$(date)] Failed to get DB_USER" >> /var/log/postgresql/healthcheck.log
    exit 1
fi

echo "[$(date)] Got DB_USER=$DB_USER" >> /var/log/postgresql/healthcheck.log

# Check PostgreSQL
pg_isready -U "$DB_USER" -h localhost
EXIT_CODE=$?

echo "[$(date)] pg_isready exit code: $EXIT_CODE" >> /var/log/postgresql/healthcheck.log
exit $EXIT_CODE