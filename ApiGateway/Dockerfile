FROM owasp/modsecurity-crs:nginx-alpine

USER root

ENV WAIT_FOR_SERVICES=false

# Install required packages
RUN apk update && \
    apk add --no-cache \
    openssl \
    curl \
    bash \
    unzip \
    jq \
    gettext &> /tmp/my.log

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && \
    mv vault /usr/local/bin/ && \
    rm vault.zip

# Copy the files from the bin folder to the container's /usr/bin/ directory
COPY src/bin/check-low-port /usr/bin/check-low-port
COPY src/bin/entrypoint.sh /usr/bin/custom-entrypoint.sh
COPY src/bin/generate-certificate /usr/bin/generate-certificate
COPY src/bin/healthcheck /usr/bin/healthcheck

# Copy the modsecurity configuration files to /etc/nginx/modsecurity.d/
COPY config/modsecurity/rules/RESPONSE-999-EXECLUSION-RULES-AFTER-CRS.conf /opt/owasp-crs/rules/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf.example

# Copy the nginx configuration template to /etc/nginx/templates/
COPY config/nginx/nginx.conf.template /etc/nginx/templates/nginx.conf.template

# Copy the error pages to the appropriate location
COPY src/error_pages /usr/share/nginx/html/error_pages


RUN chmod +x /usr/bin/check-low-port\
    /usr/bin/custom-entrypoint.sh\
    /usr/bin/generate-certificate\
    /usr/bin/healthcheck

EXPOSE 80 443

ENTRYPOINT ["/usr/bin/custom-entrypoint.sh"]