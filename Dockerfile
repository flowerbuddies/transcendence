FROM alpine:3.18

WORKDIR /app

COPY . .

RUN \
apk add --no-cache python3 python3-dev py3-pip gettext tini build-base libffi-dev nginx; \
pip install --no-cache-dir --upgrade --break-system-packages pip setuptools-scm; \
addgroup -g 1000 appuser; \
adduser -u 1000 -G appuser -D -h /app appuser; \
chmod +x /app/docker-entrypoint.sh; \
mkdir -p /var/lib/nginx/tmp /var/log/nginx /app/logs; \
chown -R appuser:appuser /var/lib/nginx /var/log/nginx /app; \
chmod -R 755 /var/lib/nginx /var/log/nginx;

USER appuser

RUN pip install --user --no-cache-dir -r requirements.txt; \
echo "export PATH=/app/.local/bin:$PATH" >> /app/.profile; \
sed 's/DEBUG = True/DEBUG = False/g' /app/transcendence/settings.py > /app/transcendence/settings.py.new; \
mv /app/transcendence/settings.py.new /app/transcendence/settings.py;

EXPOSE 8000

ENTRYPOINT [ "tini", "--" ]
CMD [ "/app/docker-entrypoint.sh" ]
