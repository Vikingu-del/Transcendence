#!/bin/sh
set -e

# # Check if we should wait for backend services
# if [ "${WAIT_FOR_SERVICES}" == "true" ]; then
#     # Wait for backend services to be available
#     for service in ${BACKEND_SERVICES}; do
#         until nc -z "${service}" 8000; do
#             echo "Waiting for ${service} to be available..."
#             sleep 2
#         done
#     done
# else
#     echo "Skipping wait for backend services."
# fi

# Create a directory for SSL certificates
mkdir -p /etc/nginx/ssl

# Generate a self-signed certificate without prompting for input
openssl req -newkey rsa:2048 -nodes -keyout /etc/nginx/ssl/nginx-selfsigned.key \
  -x509 -days 365 -out /etc/nginx/ssl/nginx-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"

# Start NGINX
nginx -g 'daemon off;'
