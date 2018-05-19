FROM python:3.6-slim

RUN apt-get update && \
    apt-get install -y \
    mongodb

RUN mkdir /opt/pets

WORKDIR /opt/pets

ADD . .

RUN pip install -r requirements.txt

EXPOSE  5000

CMD gunicorn -b :5000 --access-logfile - --error-logfile - pets:app




