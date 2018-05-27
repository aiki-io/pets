FROM python:3.6-slim

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5 && \
    echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.6 main" | tee /etc/apt/sources.list.d/mongodb-org-3.6.list && \
    apt-get update && \
    apt-get install -y \
    mongodb-org-shell \
    gcc

RUN mkdir /opt/pets

WORKDIR /opt/pets

ADD . .

RUN pip install -r requirements.txt

EXPOSE  5000

CMD gunicorn -b :5000 --reload --access-logfile - --error-logfile - pets:app




