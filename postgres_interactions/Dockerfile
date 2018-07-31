# как запускать
# sudo docker-compose --project-name postgres-client -f docker-compose.yml up --build -d
# sudo docker-compose --project-name postgres-client -f docker-compose.yml run --rm postgres-client
# psql --host $APP_POSTGRES_HOST -U postgres

FROM alpine:edge

RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

RUN apk update && apk upgrade && apk --no-cache --update-cache add postgresql-client su-exec curl nano

COPY ./src/* /home/
