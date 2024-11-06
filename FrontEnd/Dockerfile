FROM node:latest

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .

CMD ["npm", "run", "serve"]  # Command to start the Vue app
