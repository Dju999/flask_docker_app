
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

# Зависимости для numpy
# ---------------------


RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev\
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# ----------------------

COPY ./* /home/
COPY ./templates/* /home/templates/
RUN pip install --no-cache -r /home/requirements.txt


CMD [ "python", "/home/app.py" ]
