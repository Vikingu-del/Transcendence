# Use a base image with package management
FROM alpine:latest

# Install NGINX, Netcat, and gettext
RUN apk add --no-cache nginx openrc netcat-openbsd gettext

# Copy NGINX configuration file to the container
COPY config/nginx.template.conf /etc/nginx/nginx.template.conf
COPY config/entrypoint.sh /usr/local/bin/

# Make entrypoint executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the port defined in gateway.env
EXPOSE ${GATEWAY_PORT}

# CMD to start NGINX with environment variables
## Uses envsubst to replace environment variables in nginx.conf at runtime, then starts NGINX.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
