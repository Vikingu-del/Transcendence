# Use a compatible Python version
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

USER root

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get install -y curl bash unzip jq &> /tmp/my.log

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.14.0/vault_1.14.0_linux_amd64.zip -o vault.zip && \
    unzip vault.zip && mv vault /usr/local/bin/ && rm vault.zip

# Copy the requirements file
COPY ./config/requirements.txt config/requirements.txt
COPY ./config/entrypoint.sh /bin/entrypoint.sh
RUN chmod +x /bin/entrypoint.sh

RUN mkdir -p /app/media

# Install the dependencies
RUN pip install --no-cache-dir -r config/requirements.txt

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y postgresql-client

# Copy the project files
COPY . .

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["/bin/entrypoint.sh"]

# Command to run the Django development server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8005"]