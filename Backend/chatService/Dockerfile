FROM python:3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project files in specific order
COPY chatService/ chatService/
COPY manage.py .
COPY config/entrypoint.sh /entrypoint.sh

# Set executable permissions
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
# Change CMD to use Django development server instead of Daphne for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]