#!/bin/sh

echo "Retrieving database credentials from Vault..."

# Vault details
VAULT_ADDR="http://vault:8200"
ROLE_ID_FILE="/vault/secrets/user/role_id"
SECRET_ID_FILE="/vault/secrets/user/secret_id"

# # Check if the role_id and secret_id files exist
# if [[ ! -f "$ROLE_ID_FILE" || ! -f "$SECRET_ID_FILE" ]]; then
#     echo "❌ Role ID or Secret ID file not found!"
#     exit 1
# fi

# Read AppRole credentials
ROLE_ID=$(cat $ROLE_ID_FILE)
SECRET_ID=$(cat $SECRET_ID_FILE)

echo "ROLE_ID = $ROLE_ID, SECRET_ID = $SECRET_ID"

# Authenticate with Vault using AppRole
VAULT_TOKEN=$(curl -s --request POST --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)

echo "VAULT_TOKEN = $VAULT_TOKEN"

if [[ -z "$VAULT_TOKEN" || "$VAULT_TOKEN" == "null" ]]; then
    echo "❌ Failed to authenticate with Vault"
    exit 1
fi
echo "✅ Successfully authenticated with Vault"

# Retrieve database secrets
DB_USER=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user | jq -r .data.data.DB_USER)
DB_PASSWORD=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user | jq -r .data.data.DB_PASSWORD)
DB_NAME=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user | jq -r .data.data.DB_NAME)
DB_HOST=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user | jq -r .data.data.DB_HOST)
DB_PORT=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/data/user | jq -r .data.data.DB_PORT)

if [[ -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_NAME" ]]; then
    echo "❌ Failed to retrieve database credentials from Vault"
    exit 1
fi

if [[ -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_NAME" ]]; then
    echo "❌ Failed to retrieve database credentials from Vault"
    exit 1
fi
echo "✅ Successfully retrieved database credentials from Vault"

echo "DB_USER: $DB_USER, DB_NAME: $DB_NAME, DB_PASSWORD: $DB_PASSWORD, DB_HOST: $DB_HOST"

mkdir -p /app/userService/secrets
touch /app/userService/secrets/.env

echo "DB_USER=$DB_USER" > /app/userService/secrets/.env
echo "DB_PASSWORD=$DB_PASSWORD" >> /app/userService/secrets/.env
echo "DB_NAME=$DB_NAME" >> /app/userService/secrets/.env
echo "DB_HOST=$DB_HOST" >> /app/userService/secrets/.env
echo "DB_PORT=$DB_PORT" >> /app/userService/secrets/.env

# export DB_USER=$DB_USER
# export DB_PASSWORD=$DB_PASSWORD
# export DB_NAME=$DB_NAME
# export DB_HOST=$DB_HOST
# export DB_PORT=$DB_PORT

# Wait until PostgreSQL is ready
echo "Waiting for the database to be ready..."

while ! nc -z $DB_HOST $DB_PORT; do
  echo "Database is still unavailable - sleeping"
  sleep 1
done

echo "Database is up - continuing..."

# Run database migrations
echo "Running makemigrations..."
python3 manage.py makemigrations
echo "Running migrate..."
python3 manage.py migrate

# Start the Django development server
python3 manage.py runserver 0.0.0.0:8000