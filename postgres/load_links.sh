#/bin/bash

docker run -it --rm --link netology-postgres:postgres -v `pwd`/data:/data postgres \
  psql -h postgres -U postgres -c \
    "\\copy temp FROM '/data/links.csv' DELIMITER ',' CSV HEADER"