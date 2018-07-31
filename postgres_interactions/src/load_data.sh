#/bin/sh


psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "DROP TABLE IF EXISTS links"
psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "DROP TABLE IF EXISTS ratings"

echo "Загружаем links.csv..."
psql --host $APP_POSTGRES_HOST -U postgres -c '
  CREATE TABLE IF NOT EXISTS links (
    movieId bigint,
    imdbId varchar(20),
    tmdbId varchar(20)
  );'

psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "\\copy links FROM '/data/links.csv' DELIMITER ',' CSV HEADER"

echo "Загружаем ratings.csv..."
psql --host $APP_POSTGRES_HOST -U postgres -c '
  CREATE TABLE IF NOT EXISTS ratings (
    userId bigint,
    movieId bigint,
    rating float(25),
    timestamp bigint
  );'

psql --host $APP_POSTGRES_HOST -U postgres -c \
    "\\copy ratings FROM '/data/ratings_small.csv' DELIMITER ',' CSV HEADER"
