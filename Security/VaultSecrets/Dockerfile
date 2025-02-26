# Use a base image with Vault pre-installed
FROM vault:1.9.3

# Install Python and any dependencies for your vault.py script
RUN apk add --no-cache python3 py3-pip bash curl && pip3 install hvac python-dotenv 

# Copy entrypoint script and vault.py into the container
COPY vault.py /vault.py
COPY config/entrypoint.sh /entrypoint.sh
COPY secrets/ /internal/secrets/
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]