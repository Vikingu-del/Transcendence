# Use a base image with package management
FROM nginx:latest

# Update package list and install required packages
RUN apt update && apt upgrade -y
RUN apt install -y netcat-openbsd gettext-base openssl

# Copy NGINX configuration file to the container
COPY config/nginx.template.conf /etc/nginx/nginx.conf
COPY config/entrypoint.sh /usr/local/bin/

# Make entrypoint executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the ports for HTTP and HTTPS
EXPOSE 80 443

# Use the entrypoint script to start NGINX with environment variables
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
