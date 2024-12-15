# Use Node.js image to build the Vue app
FROM node:latest

# Set the working directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the app
COPY . .

# Build the Vue app for production
RUN npm run build
# RUN npm run preview

# The `dist/` folder will be available after the build
