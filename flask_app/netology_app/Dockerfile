
FROM python:3.5.2-alpine

ENV BIND_PORT 5001
ENV APP_REDIS_HOST redis
ENV APP_REDIS_PORT 6379
#MONGO
ENV APP_MONGO_HOST mongodb
ENV APP_MONGO_PORT 27017
# POSTGRES
ENV APP_POSTGRES_HOST postgresdb
ENV APP_POSTGRES_PORT 5432


EXPOSE $BIND_PORT

RUN apk update \
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev

COPY ./requirements.txt /home/requirements.txt
COPY ./app.py /home/app.py
COPY ./python_db.py /home/python_db.py
RUN pip install -r /home/requirements.txt


CMD [ "python", "/home/app.py" ]
# CMD [ "python", "/home/python_db.py" ]
