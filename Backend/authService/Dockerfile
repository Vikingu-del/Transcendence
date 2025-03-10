# Use a compatible Python version
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

USER root

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get install -y curl bash unzip jq &> /tmp/my.log

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

# Copy the requirements file
COPY config/requirements.txt /requirements.txt
COPY config/entrypoint.sh /bin/entrypoint.sh
RUN chmod +x /bin/entrypoint.sh

# Install the dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Install Pillow
RUN python -m pip install Pillow

# Install corsheaders
RUN pip install django-cors-headers

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y postgresql-client

# Copy the project files
COPY . .

# Create a non-root user and change ownership
RUN useradd -m appuser && chown -R appuser:appuser /app /bin/entrypoint.sh
USER appuser

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["entrypoint.sh"]

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "authService.wsgi:application"]