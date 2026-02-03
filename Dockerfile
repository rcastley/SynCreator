FROM python:3.11-alpine

RUN apk add --no-cache curl

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/syncreator/health || exit 1

CMD ["waitress-serve", "--port=8080", "--threads=8", "--connection-limit=500", "--channel-timeout=120", "--url-prefix=/syncreator", "--url-scheme=https", "--call", "flaskr:create_app"]
