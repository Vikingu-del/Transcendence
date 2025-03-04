FROM wrouesnel/postgres_exporter

USER root


# Create Kibana user using elasticsearch-users tool
COPY custom-entrypoint.sh /custom-entrypoint.sh

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd curl bash unzip jq

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

RUN chmod +x /custom-entrypoint.sh

# Start Elasticsearch
ENTRYPOINT ["/custom-entrypoint.sh"]
