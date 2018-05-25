#/bin/bash

docker run -it --rm --link netology-postgres:postgres postgres psql -h postgres -U postgres -c '
  CREATE TABLE IF NOT EXISTS links (
    movieId bigint,
    imdbId varchar(20),
    tmdbId varchar(20)
  );'

docker run -it --rm --link netology-postgres:postgres -v `pwd`/data:/data postgres \
  psql -h postgres -U postgres -c \
    "\\copy links FROM '/data/links.csv' DELIMITER ',' CSV HEADER"

docker run -it --rm --link netology-postgres:postgres postgres psql -h postgres -U postgres -c '
  CREATE TABLE IF NOT EXISTS ratings (
    userId bigint,
    movieId bigint,
    rating float(25),
    timestamp bigint
  );'


docker run -it --rm --link netology-postgres:postgres -v `pwd`/data:/data postgres \
  psql -h postgres -U postgres -c \
    "\\copy ratings FROM '/data/ratings.csv' DELIMITER ',' CSV HEADER"