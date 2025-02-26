ARG ELK_VERSION

# https://github.com/elastic/elasticsearch-docker
FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_VERSION}

COPY setup-certs.sh /bin/setup-certs.sh
RUN chmod +x /bin/setup-certs.sh

ENTRYPOINT [ "setup-certs.sh" ]