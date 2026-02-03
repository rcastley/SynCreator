FROM python:3.11-alpine

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["waitress-serve", "--port=8080", "--threads=8", "--connection-limit=500", "--channel-timeout=120", "--url-prefix=/syncreator", "--url-scheme=https", "--call", "flaskr:create_app"]
