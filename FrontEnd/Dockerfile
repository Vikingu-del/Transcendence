FROM node:latest

WORKDIR /app

COPY package*.json ./
RUN npm install
RUN npm install vue-i18n@next
RUN npm install vue-i18n@9 @intlify/unplugin-vue-i18n

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]