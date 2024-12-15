# Start from the base Python image
FROM python:3-alpine

# Set environment variables
ENV VAULT_VERSION=1.9.3

# Install necessary dependencies
RUN apk add --no-cache curl bash unzip openssl

# Download and install Vault directly
RUN curl -L https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && \
    mv vault /usr/local/bin/ && \
    rm vault.zip && \
    chmod +x /usr/local/bin/vault

# Ensure required directories exist
RUN mkdir -p /vault/config /vault/data

# Add Vault configuration files
COPY config/ /vault/config/

RUN chmod +x /vault/config/entrypoint.sh

# Set entrypoint and command
ENTRYPOINT ["/vault/config/entrypoint.sh"]
