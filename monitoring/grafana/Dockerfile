FROM grafana/grafana:latest

USER root

# Copy custom config files
RUN mkdir -p /etc/grafana/provisioning/dashboards /etc/grafana/provisioning/datasources
COPY provisioning/dashboard.yaml /etc/grafana/provisioning/dashboards/dashboard.yaml
COPY provisioning/datasources.yml /etc/grafana/provisioning/datasources/datasources.yml
COPY dashboards/ /var/lib/grafana/dashboards/
# Create Kibana user using elasticsearch-users tool
COPY config/custom-entrypoint.sh /custom-entrypoint.sh 

# Install netcat
RUN apk update && apk add --no-cache netcat-openbsd curl bash unzip jq &> /tmp/my.log

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

RUN chmod +x /custom-entrypoint.sh

# Start Elasticsearch
ENTRYPOINT ["/custom-entrypoint.sh"]
