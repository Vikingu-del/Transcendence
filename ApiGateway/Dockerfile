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
    gettext

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && \
    mv vault /usr/local/bin/ && \
    rm vault.zip

# Set up writable directories
RUN mkdir -p /tmp/nginx/ssl && \
    chown -R nginx:nginx /tmp/nginx && \
    chmod -R 755 /tmp/nginx

# Set up ModSecurity and template directories
RUN mkdir -p /etc/nginx/templates/conf.d && \
    mkdir -p /etc/nginx/templates/modsecurity.d && \
    mkdir -p /etc/nginx/templates/includes && \
    mkdir -p /etc/nginx/conf && \
    mkdir -p /etc/nginx/ssl && \
    mkdir -p /etc/nginx/modsecurity.d/custom-rules && \
    mkdir -p /etc/nginx/modsecurity.d/data && \
    chmod 755 /etc/nginx/ssl && \
    chmod 755 /etc/nginx/modsecurity.d/custom-rules && \
    chmod 755 /etc/nginx/modsecurity.d/data && \
    chown -R nginx:nginx /etc/nginx/ssl

# Copy configuration templates
COPY config/nginx.conf.template /etc/nginx/templates/
COPY config/entrypoint.sh /usr/local/bin/custom-entrypoint.sh
COPY config/modsecurity/modsecurity.conf /etc/nginx/modsecurity.d/modsecurity.conf
COPY config/modsecurity/rules/*.conf /etc/nginx/modsecurity.d/custom-rules/
COPY config/modsecurity/data/*.dat /etc/nginx/modsecurity.d/data/

# Set permissions
RUN chmod +x /usr/local/bin/custom-entrypoint.sh && \
    chmod -R 755 /etc/nginx/templates && \
    chmod 644 /etc/nginx/modsecurity.d/data/*.dat && \
    chmod 644 /etc/nginx/modsecurity.d/custom-rules/*.conf && \
    chown -R nginx:nginx /etc/nginx/modsecurity.d/

EXPOSE 80 443

ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]