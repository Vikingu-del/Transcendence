#!bin/bash

echo "Starting Vault server..."
echo "vault root token: ${VAULT_ROOT_TOKEN}"
export VAULT_TOKEN="${VAULT_ROOT_TOKEN}"
python3 "/vault.py"

sleep 1000