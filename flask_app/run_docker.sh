#/bin/bash

# install docker.compose
sudo apt install docker docker-compose

# doenload image
#docker pull alpine

# run docker
#-- docker run -i -t alpine /bin/sh
# docker-compose --project-name app-test -f docker-compose.yml build
docker-compose --project-name app-test -f docker-compose.yml up --build

# docker-compose stop

# docker system prune -a

# список образов  docker images -a
# удалить по image_id docker rmi -f IMAGE_ID
# docker stop $(docker ps -a -q)
# docker rm $(docker ps -a -q)