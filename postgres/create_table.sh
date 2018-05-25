#/bin/bash

docker run -it --rm --link netology-postgres:postgres postgres psql -h postgres -U postgres -c '
  CREATE TABLE IF NOT EXISTS temp (
    movieId bigint,
    imdbId varchar(20),
    tmdbId varchar(20)
  );'