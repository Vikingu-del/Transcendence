#!/bin/sh
set -e

# Vault details
VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/secrets/gateway/role_id"
SECRET_ID_FILE="/vault/secrets/gateway/secret_id"

# Check if the role_id and secret_id files exist
if [[ ! -f "$ROLE_ID_FILE" || ! -f "$SECRET_ID_FILE" ]]; then
    echo "❌ Role ID or Secret ID file not found!"
    exit 1
fi

# Read AppRole credentials
ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)

echo "ROLE_ID = $ROLE_ID, SECRET_ID = $SECRET_ID"

# Authenticate with Vault using AppRole
VAULT_TOKEN=$(curl -s --request POST --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)
echo "VAULT_TOKEN = $VAULT_TOKEN"

# Retrieve database secrets
CURRENT_HOST=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/gateway | jq -r .data.data.CURRENT_HOST)
export CURRENT_HOST=$CURRENT_HOST

# Check if we should wait for backend services (Optional)
if [ "${WAIT_FOR_SERVICES}" == "true" ]; then
    # Wait for backend services to be available
    for service in ${BACKEND_SERVICES}; do
        until nc -z "${service}" 8000; do
            echo "Waiting for ${service} to be available..."
            sleep 2
        done
    done
else
    echo "Skipping wait for backend services."
fi

# Create a directory for SSL certificates if not already present
mkdir -p /etc/nginx/ssl

# Generate a self-signed certificate without prompting for input
if [ ! -f /etc/nginx/ssl/nginx-selfsigned.crt ]; then
    echo "Generating self-signed SSL certificate..."
    openssl req -newkey rsa:2048 -nodes -keyout /etc/nginx/ssl/nginx-selfsigned.key \
      -x509 -days 365 -out /etc/nginx/ssl/nginx-selfsigned.crt \
      -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=localhost"
else
    echo "SSL certificate already exists. Skipping certificate generation."
fi

# Start NGINX
nginx -g 'daemon off;'
