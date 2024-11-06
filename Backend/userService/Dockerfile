# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY config/requirements.txt /app/
COPY config/entrypoint.sh /usr/local/bin/entrypoint.sh
# Make the entrypoint script executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt update && apt install -y netcat-openbsd postgresql-client

# Copy the project files
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]