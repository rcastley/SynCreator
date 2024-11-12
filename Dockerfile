FROM python:3.11-alpine 

WORKDIR /app

COPY . /app
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN /venv/bin/pip install --upgrade pip --no-cache-dir -e . 

ADD . /app

ENV FLASK_APP=app/flaskr
EXPOSE 8080
CMD ["sh", "-c", "flask init-db; waitress-serve --call flaskr:create_app"]
