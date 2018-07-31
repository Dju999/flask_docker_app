SELECT ('ФИО: капитан Америка');

-- ЗАПРОС 1 - самые популярные фильмы
SELECT movieId, AVG(rating) FROM ratings GROUP BY 1 LIMIT 10;

--  ЗАПРОС 2 - надо заджойнить на keywords
WITH top_rated as ( ЗАПРОС1 ) ЗАПРОС2;

-- ЗАПРОС 3 - модифицируем ЗАПРОС 2 чтобы сохранить данные в таблицу
WITH top_rated as ( ЗАПРОС1 )  SELECT movieId, top_rated_tags INTO top_keywords FROM top_rated ...;

\copy (SELECT * FROM top_keywords) TO '/data/tags.tsv' DELIMITER E'\t';

