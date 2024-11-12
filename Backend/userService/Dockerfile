# Use a compatible Python version
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd

# Copy the requirements file
COPY config/requirements.txt /requirements.txt
COPY config/entrypoint.sh /bin/entrypoint.sh
RUN chmod +x /bin/entrypoint.sh

# Install the dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Install Pillow
RUN python -m pip install Pillow

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y postgresql-client

# Copy the project files
COPY . .

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["entrypoint.sh"]

# Command to run the Django development server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]