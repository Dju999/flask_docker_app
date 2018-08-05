#/bin/sh


psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "DROP TABLE IF EXISTS links"
psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "DROP TABLE IF EXISTS ratings"
psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "DROP TABLE IF EXISTS ui_interactions"

echo "Загружаем links.csv..."
psql --host $APP_POSTGRES_HOST -U postgres -c '
  CREATE TABLE links (
    movieId bigint,
    imdbId varchar(20),
    tmdbId varchar(20)
  );'

psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "\\copy links FROM '/data/links.csv' DELIMITER ',' CSV HEADER"

echo "Загружаем ratings.csv..."
psql --host $APP_POSTGRES_HOST -U postgres -c '
  CREATE TABLE ratings (
    userId bigint,
    movieId bigint,
    rating float(25),
    timestamp bigint
  );'

psql --host $APP_POSTGRES_HOST -U postgres -c \
    "\\copy ratings FROM '/data/ratings_small.csv' DELIMITER ',' CSV HEADER"

# используем Postgres для препроцессинга
psql --host $APP_POSTGRES_HOST  -U postgres -c \
    "DROP TABLE IF EXISTS keywords"

echo "Загружаем keywords.csv..."
psql --host $APP_POSTGRES_HOST -U postgres -c '
  CREATE TABLE keywords (
    movieId bigint,
    tags text
  );'

psql --host $APP_POSTGRES_HOST -U postgres -c \
    "\\copy keywords FROM '/data/keywords.csv' DELIMITER ',' CSV HEADER"
# выгружаем данные с другим сепаратором
psql --host $APP_POSTGRES_HOST -U postgres -c \
    "\\copy (select * from keywords) to '/data/keywords.tsv' with delimiter as E'\t'"