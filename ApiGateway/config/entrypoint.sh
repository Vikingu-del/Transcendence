#!/bin/sh
set -e

# Check if we should wait for backend services
if [ "${WAIT_FOR_SERVICES}" == "true" ]; then
    # Wait for backend services to be available
    for service in ${BACKEND_SERVICES}; do
        until nc -z "${service}" 8000; do
            echo "Waiting for ${service} to be available..."
            sleep 2
        done
    done
else
    echo "Skipping wait for backend services."
fi

# Replace template file with environment variables
envsubst < /etc/nginx/nginx.template.conf > /etc/nginx/nginx.conf

# Start NGINX
nginx -g 'daemon off;'
