#!/bin/bash
set -e

VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/approle/auth_db/role_id"
SECRET_ID_FILE="/vault/approle/auth_db/secret_id"

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
    $VAULT_ADDR/v1/secret/data/auth_db)

# Get application credentials from Vault
APP_USER=$(echo $VAULT_RESPONSE | jq -r .data.data.AUTH_DB_USER)
APP_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.AUTH_DB_PASSWORD)
APP_DB=$(echo $VAULT_RESPONSE | jq -r .data.data.AUTH_DB_NAME)

# Debug output (remove in production)
echo "Debug: APP_USER=$APP_USER APP_DB=$APP_DB"

# Validate credentials
if [ -z "$APP_USER" ] || [ "$APP_USER" = "null" ] || \
   [ -z "$APP_PASSWORD" ] || [ "$APP_PASSWORD" = "null" ] || \
   [ -z "$APP_DB" ] || [ "$APP_DB" = "null" ]; then
    echo "❌ Failed to retrieve valid credentials from Vault"
    exit 1
fi

# Set PostgreSQL environment variables
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="postgres"
export POSTGRES_DB="postgres"

# Create initialization script
cat > /docker-entrypoint-initdb.d/init-user-db.sh << EOF
#!/bin/bash
set -e

# Run as postgres superuser
psql -v ON_ERROR_STOP=1 --username "\$POSTGRES_USER" <<-EOSQL
    -- Create application database
    CREATE DATABASE $APP_DB;

    -- Create application user
    CREATE USER $APP_USER WITH ENCRYPTED PASSWORD '$APP_PASSWORD';

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE $APP_DB TO $APP_USER;

    -- Connect to application database
    \c $APP_DB

    -- Grant schema privileges
    GRANT ALL ON SCHEMA public TO $APP_USER;
EOSQL
EOF

chmod +x /docker-entrypoint-initdb.d/init-user-db.sh
echo "✅ Retrieved database credentials"

exec docker-entrypoint.sh postgres