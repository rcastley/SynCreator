FROM python:3.11-alpine 

WORKDIR /app

COPY . /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN /venv/bin/pip install --upgrade pip --no-cache-dir -e . 

CMD ["export FLASK_APP=app/flaskr"]

CMD ["waitress-serve", "--call", "flaskr:create_app"]
