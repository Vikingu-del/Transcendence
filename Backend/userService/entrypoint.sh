#!/bin/bash

# Wait for PostgreSQL to be ready
while ! python3 -c "import psycopg2; psycopg2.connect(dbname='mydatabase', user='myuser', password='mypassword', host='postgres-db')" &> /dev/null; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run migrations
echo "Applying migrations..."
python3 manage.py migrate || { echo "Migrations failed"; exit 1; }

# Create a superuser if it doesn't exist (optional)
if ! python3 manage.py shell -c \
    "from django.contrib.auth import get_user_model; \
    User = get_user_model(); \
    print(User.objects.filter(username='admin').exists())"; then
    echo "Creating superuser..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('eseferi', 'rk.seferi@gmail.com', 'yourpassword')" | python3 manage.py shell || { echo "Failed to create superuser"; exit 1; }
fi

# Start the server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:80