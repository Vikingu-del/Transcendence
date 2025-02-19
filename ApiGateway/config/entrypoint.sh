#!/bin/bash
set -e

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/gateway/role_id"
SECRET_ID_FILE="/vault/approle/gateway/secret_id"

# Function to generate SSL certificates
generate_ssl_certificates() {
    local SSL_DIR="/tmp/nginx/ssl"
    
    # Create SSL directory if it doesn't exist
    mkdir -p $SSL_DIR
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout $SSL_DIR/nginx-selfsigned.key \
        -out $SSL_DIR/nginx-selfsigned.crt \
        -subj "/C=FR/ST=IDF/L=Paris/O=42/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

    # Set proper permissions
    chmod 644 $SSL_DIR/nginx-selfsigned.crt
    chmod 600 $SSL_DIR/nginx-selfsigned.key
}

# Function to setup ModSecurity
setup_modsecurity() {
    echo "Setting up ModSecurity..."
    
    # Create required directories
    mkdir -p /etc/nginx/modsecurity.d/{data,custom-rules,tmp}
    
    # Check for unicode.mapping
    if [ ! -f "/etc/nginx/modsecurity.d/unicode.mapping" ]; then
        echo "Downloading unicode.mapping..."
        curl --retry 3 --retry-delay 2 -fsSL \
            "https://raw.githubusercontent.com/SpiderLabs/ModSecurity/v3/master/unicode.mapping" \
            -o "/etc/nginx/modsecurity.d/unicode.mapping"
        chmod 644 "/etc/nginx/modsecurity.d/unicode.mapping"
    fi
    
    # Set proper permissions
    chown -R nginx:nginx /etc/nginx/modsecurity.d
    chmod -R 755 /etc/nginx/modsecurity.d
    chmod 644 /etc/nginx/modsecurity.d/unicode.mapping
}

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

# Setup ModSecurity
setup_modsecurity
echo "✅ ModSecurity setup complete"

# Generate SSL certificates
generate_ssl_certificates
echo "✅ SSL certificates generated"

# Export ModSecurity configuration
export MODSEC_RULE_ENGINE=On
export MODSEC_AUDIT_LOG=/var/log/modsec_audit.log
export MODSEC_CONFIG_DIR=/etc/nginx/modsecurity.d

# Let the original entrypoint handle template processing
exec /docker-entrypoint.sh nginx -g "daemon off;"