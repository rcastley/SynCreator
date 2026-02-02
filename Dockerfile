FROM python:3.11-alpine

WORKDIR /app

COPY . /app
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN /venv/bin/pip install --upgrade pip --no-cache-dir -e .

ADD . /app

ENV FLASK_APP=app/flaskr
EXPOSE 8080

# Only initialize DB if it doesn't exist (preserves existing data)
CMD ["sh", "-c", "if [ ! -f /app/instance/scc.sqlite ]; then flask init-db; fi; waitress-serve --url-prefix '/syncreator' --url-scheme 'https' --call flaskr:create_app"]
