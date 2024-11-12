# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest

# Copy the entrypoint script
COPY config/entrypoint.sh /usr/local/bin/entrypoint.sh

# Ensure the entrypoint script is executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the PostgreSQL default port
EXPOSE 5432

# Use the custom entrypoint script
ENTRYPOINT ["entrypoint.sh"]