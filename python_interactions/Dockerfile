# как запускать
# sudo docker-compose --project-name py-db -f docker-compose.yml up --build -d
# sudo docker-compose --project-name py-db -f docker-compose.yml run --rm python-db

FROM continuumio/miniconda3

ENTRYPOINT ["/bin/bash"]

RUN apt-get update && apt-get install -y  postgresql-client curl nano mongodb mongo-tools

# Добавляем пакеты в анаконду - например, pandas
RUN conda install -c anaconda scipy numpy pandas sqlalchemy pymongo psycopg2 msgpack-numpy lz4 msgpack-python

# Копируем в контейнер скрипт для создания таблиц
COPY ./src/* /home/