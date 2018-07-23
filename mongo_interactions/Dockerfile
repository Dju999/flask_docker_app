# как запускать
# sudo docker-compose --project-name mongo-client -f docker-compose.yml up --build -d
# sudo docker-compose --project-name mongo-client -f docker-compose.yml run --rm mongo-client
# /usr/bin/mongo -host $APP_MONGO_HOST -port $APP_MONGO_PORT

FROM alpine:3.6
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk update && apk upgrade && apk --no-cache --update-cache add mongodb=3.4.4-r0 su-exec curl mongodb-tools=3.4.4-r2 nano


COPY ./src/* /home/
