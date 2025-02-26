#!/bin/bash

# Ensure the vault binary is in the PATH (if not already)
export PATH=$PATH:/usr/local/bin

# Path to the Vault configuration file
VAULT_CONFIG="/vault/config/vault.hcl"

# Ensure Vault data directory exists
mkdir -p /vault/file vault/token vault/approle
touch /vault/token/root_token

# Start Vault in server mode with the configuration
echo "Starting Vault server..."

# Wait for Vault to start (you can increase this sleep duration if necessary)
sleep 3

mkdir -p /vault/internal_secrets
touch /vault/internal_secrets/init-output.txt

# Start Vault server in the background
vault server -config=${VAULT_CONFIG} &
VAULT_PID=$!

# Wait for Vault to become ready
echo "Waiting for Vault to start..."
sleep 5

# Initialize Vault if not initialized
if ! vault status | grep -q "Initialized.*true"; then
    echo "Vault is not initialized. Initializing..."
    vault operator init -key-shares=5 -key-threshold=3 > /vault/internal_secrets/init-output.txt
    echo "Vault initialized. Keys stored in /vault/internal_secrets/init-output.txt"

    # Unseal Vault
    for i in 1 2 3; do
        vault operator unseal $(grep "Unseal Key $i:" /vault/internal_secrets/init-output.txt | awk '{print $4}')
    done

    # Login with root token
    VAULT_ROOT_TOKEN=$(grep "Initial Root Token:" /vault/internal_secrets/init-output.txt | awk '{print $4}')
    export VAULT_ROOT_TOKEN
    echo -n "$VAULT_ROOT_TOKEN" > /vault/token/root_token
    vault login $VAULT_ROOT_TOKEN
    export VAULT_TOKEN=$VAULT_ROOT_TOKEN
    VAULT_TOKEN=$VAULT_ROOT_TOKEN
    echo -e "Vault unsealed and logged in. Root token stored in /secrets/.env \n and is value now is $VAULT_TOKEN"
else
    # Unseal Vault
    echo "Vault is already initialized. Unsealing..."
    for i in 1 2 3; do
        vault operator unseal $(grep "Unseal Key $i:" /vault/internal_secrets/init-output.txt | awk '{print $4}')
    done
    echo "Vault unsealed."
fi

# Enable KV secrets engine version 2
if ! vault secrets list | grep -q "secret/"; then
    # Enable KV secrets engine version 2
    vault secrets enable -path=secret kv-v2
    echo "KV secrets engine enabled at path=secret."
else
    echo "KV secrets engine is already enabled at path=secret."
fi

# Loop through and create policies if they don't exist
for policy in $(ls /vault/config/vault-policies); do
    if vault policy write $(basename $policy .hcl) /vault/config/vault-policies/$policy; then
        echo "$(basename $policy .hcl) created"
    else
        echo "$(basename $policy .hcl) already exists"
    fi
done

# Wait indefinitely to keep the container running
wait $VAULT_PID