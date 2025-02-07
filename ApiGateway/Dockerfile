# Start with the base Nginx image
FROM nginx:alpine

# Set environment variables (you can configure more as needed)
ENV WAIT_FOR_SERVICES=false

RUN apk update; apk upgrade; apk add nginx openssl curl bash unzip jq; apk add --no-cache gettext

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

# Copy your custom Nginx configuration
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/entrypoint.sh /entrypoint.sh

# Copy the entrypoint script
RUN chmod +x /entrypoint.sh && \
    mkdir -p /etc/nginx/ssl && \
    chown -R nginx:nginx /etc/nginx/ssl

EXPOSE 80 443

# Make the entrypoint script the container entrypoint
ENTRYPOINT ["/entrypoint.sh"]

