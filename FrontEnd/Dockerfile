FROM node:latest

WORKDIR /app

COPY package*.json ./
RUN npm install
RUN npm install vue-i18n@next --save

COPY . .



EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]