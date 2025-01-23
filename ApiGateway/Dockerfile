FROM nginx:alpine

RUN apk add --no-cache openssl

WORKDIR /etc/nginx

COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh && \
    mkdir -p /etc/nginx/ssl && \
    chown -R nginx:nginx /etc/nginx/ssl

EXPOSE 80 443

ENTRYPOINT ["/docker-entrypoint.sh"]