FROM docker.elastic.co/kibana/kibana:8.17.0

USER root

RUN mkdir -p /usr/share/kibana/config

COPY config/kibana.yml /usr/share/kibana/config/kibana.yml
COPY config/custom-entrypoint.sh /custom-entrypoint.sh

RUN chmod +x /custom-entrypoint.sh

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get install -y curl bash unzip jq

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

USER kibana

ENTRYPOINT [ "/custom-entrypoint.sh" ]