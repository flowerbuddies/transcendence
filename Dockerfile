FROM alpine

WORKDIR /app

COPY . .

RUN \
apk add --no-cache python3 py3-pip tini; \
pip install --upgrade --break-system-packages pip setuptools-scm; \
pip install --break-system-packages -r requirements.txt; \
addgroup -g 1000 appuser; \
adduser -u 1000 -G appuser -D -h /app appuser; \
chown -R appuser:appuser /app; \
chmod +x /app/docker-entrypoint.sh;

USER appuser

EXPOSE 8000

ENTRYPOINT [ "tini", "--" ]
CMD [ "/app/docker-entrypoint.sh" ]
