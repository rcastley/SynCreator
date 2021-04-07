FROM python:3-alpine 
COPY . /app
WORKDIR /app
RUN pip3 install -e . 
CMD ["export FLASK_APP=app/flaskr"]
CMD ["waitress-serve", "--call", "flaskr:create_app"]
