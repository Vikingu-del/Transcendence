#!/bin/bash

echo "Starting Vault server..."

# Wait for root token to be available
while [ ! -f /vault/token/root_token ]; do
    echo "Waiting for root token..."
    sleep 1
done

# Read token from shared volume
VAULT_TOKEN=$(cat /vault/token/root_token)
echo "Root token retrieved from shared volume"

# Export for vault.py
export VAULT_TOKEN
python3 "/vault.py"

echo "Vault server started successfully!"