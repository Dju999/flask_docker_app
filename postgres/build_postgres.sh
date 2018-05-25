#/bin/bash

# -d - запустить доке в фоне, напечатет CONTAINER_ID
docker run --name netology-postgres -e POSTGRES_PASSWORD=simplepass -d postgres
# docker stop container_ID - остановить контейнер по id
# docker start  netology-postgres -чтобы запустить повторно

# запускаем сам postgres
docker run -it --rm --link netology-postgres:postgres postgres psql -h postgres -U postgres
