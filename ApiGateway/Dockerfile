# Start with the base Nginx image
FROM nginx:alpine

# Set environment variables (you can configure more as needed)
ENV WAIT_FOR_SERVICES=false

RUN apk update; apk upgrade; apk add nginx; apk add openssl; apk add --no-cache gettext

# Copy your custom Nginx configuration
COPY config/nginx.conf.template /etc/nginx/nginx.conf.template

# Copy the entrypoint script
COPY config/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Make the entrypoint script the container entrypoint
ENTRYPOINT ["/entrypoint.sh"]

