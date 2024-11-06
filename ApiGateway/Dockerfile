# Start with the base Nginx image
FROM nginx:alpine

# Set environment variables (you can configure more as needed)
ENV WAIT_FOR_SERVICES=true

RUN apk add openssl

# Copy your custom Nginx configuration
COPY config/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint script
COPY config/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the necessary ports
EXPOSE 80 443

# Make the entrypoint script the container entrypoint
ENTRYPOINT ["/entrypoint.sh"]

