FROM python:3.8-slim-buster

WORKDIR /app
RUN pip3 install pyyaml flask flask-login requests gunicorn
COPY . .
EXPOSE 7070

CMD [ "gunicorn", "--workers", "2", "--bind", "0.0.0.0:7070", "wsgi:app" ]
