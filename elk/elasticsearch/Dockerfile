FROM docker.elastic.co/elasticsearch/elasticsearch:8.17.0

# Copy custom config files
COPY config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
COPY config/log4j2.properties /usr/share/elasticsearch/config/log4j2.properties

# Create Kibana user using elasticsearch-users tool
COPY config/custom-entrypoint.sh /custom-entrypoint.sh

USER root

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get install -y curl bash unzip jq

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

RUN chmod +x /custom-entrypoint.sh

USER elasticsearch

ENTRYPOINT ["/custom-entrypoint.sh"]
# Start Elasticsearch
# ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]