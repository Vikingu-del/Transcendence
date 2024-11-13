#!/bin/bash

# Check if the environment is 'development' or 'production'
if [ "$NODE_ENV" == "development" ]; then
  echo "Running in development mode..."
  # Run Vite's development server for hot-reloading
  npm run dev
else
  echo "Running in production mode..."
  # Start Nginx to serve the built files
  nginx -g 'daemon off;'
fi