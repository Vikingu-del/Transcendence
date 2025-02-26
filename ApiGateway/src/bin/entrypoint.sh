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
    mkdir -p /var/cache/modsecurity/tmp /var/lib/modsecurity/data /var/log/modsecurity /var/log/modsecurity/audit /var/cache/modsecurity/upload
    
    # Move unicode.mapping to the correct location
    if [ -f "/etc/modsecurity.d/unicode.mapping" ]; then
        mv /etc/modsecurity.d/unicode.mapping /etc/nginx/modsecurity.d/unicode.mapping
        chmod 644 /etc/nginx/modsecurity.d/unicode.mapping
    else
        echo "✅ unicode.mapping already exists in the right location"
    fi
    
    # Create log files
    touch /var/log/modsecurity/modsec_audit.log /var/log/modsecurity/debug.log
    
    # Set proper permissions
    chown -R nginx:nginx /etc/nginx/modsecurity.d /var/cache/modsecurity /var/lib/modsecurity /var/log/modsecurity
    chmod -R 755 /etc/nginx/modsecurity.d /var/cache/modsecurity /var/lib/modsecurity /var/log/modsecurity
    chmod 644 /var/log/modsecurity/modsec_audit.log /var/log/modsecurity/debug.log
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

# Retrieve ModSecurity configuration from Vault
MODSEC_CONFIG=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/gateway | jq -r .data.data) 

# Debugging: Print the raw response from Vault
echo "Raw Vault response: $MODSEC_CONFIG"

for key in $(echo $MODSEC_CONFIG | jq -r "keys[]"); do
    value=$(echo $MODSEC_CONFIG | jq -r --arg key "$key" '.[$key]')
    sanitized_key=$(echo "$key" | tr -d '[:space:]')
    export "$sanitized_key"="$value"
done

# Export ModSecurity configuration as environment variables
echo "METRICS_ALLOW_FROM=$METRICS_ALLOW_FROM"

echo "✅ ModSecurity configuration retrieved"

# Setup ModSecurity
setup_modsecurity
echo "✅ ModSecurity setup complete"

# Substitute environment variables in Nginx configuration templates
envsubst < /etc/nginx/templates/includes/proxy_backend.conf.template > /etc/nginx/templates/includes/proxy_backend.conf.template
envsubst < /etc/nginx/templates/includes/proxy_backend_ssl.conf.template > /etc/nginx/templates/includes/proxy_backend_ssl.conf.template
envsubst < /etc/nginx/templates/includes/location_common.conf.template > /etc/nginx/templates/includes/location_common.conf.template
envsubst < /etc/nginx/templates/includes/cors.conf.template > /etc/nginx/templates/includes/cors.conf.template

if ! grep -q "Include /opt/owasp-crs/rules/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf.example" /etc/nginx/modsecurity.d/modsecurity.conf; then
    echo "including exclusion rules in ModSecurity configuration"
    echo "echo \"Include /opt/owasp-crs/rules/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf.example\" >> /etc/nginx/modsecurity.d/modsecurity.conf" >> /docker-entrypoint.d/95-configure-rules.sh
else
    echo "✅ Exclusion rules already included in ModSecurity configuration"
fi

# Generate SSL certificates
generate_ssl_certificates
echo "✅ SSL certificates generated"

# Let the original entrypoint handle template processing
exec /docker-entrypoint.sh nginx -g "daemon off;"