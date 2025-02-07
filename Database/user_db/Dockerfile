# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest

RUN apt-get update && apt-get install -y curl bash unzip jq

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

# Copy the custom entrypoint script
COPY config/entrypoint.sh /usr/bin/entrypoint.sh

# Make sure the entrypoint script is executable
RUN chmod +x /usr/bin/entrypoint.sh

# Expose the PostgreSQL default port
EXPOSE 5432

# Start the entrypoint script (this will also trigger Vault Agent and PostgreSQL)
ENTRYPOINT ["/usr/bin/entrypoint.sh"]