# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest

COPY config/entrypoint.sh /usr/bin/entrypoint.sh

RUN chmod +x /usr/bin/entrypoint.sh

# Copy any custom initialization scripts into the Docker image
# (optional, depending on whether you want to include SQL scripts or other files)
COPY config/init.sql /docker-entrypoint-initdb.d/

# Expose the PostgreSQL default port
EXPOSE 5432

ENTRYPOINT ["entrypoint.sh"]
