# Типы данных

Ппример создания массива

<pre>
-- создаем таблицу, у которой значения являются массивами
CREATE TABLE holiday_picnic (
     holiday varchar(50) -- строковое значение
     sandwich text[], -- массив
     side text[] [], -- многомерный массив
     dessert text ARRAY, -- массив
     beverage text ARRAY[4] -- массив из 4-х элементов
);

 -- вставляем значения массивов в таблицу
INSERT INTO holiday_picnic VALUES
     ('Labor Day',
     '{"roast beef","veggie","turkey"}',
     '{
        {"potato salad","green salad"},
        {"chips","crackers"}
     }',
     '{"fruit cocktail","berry pie","ice cream"}',
     '{"soda","juice","beer","water"}'
     );
</pre>


# Геометрические типы данных

Есть много встроенных типов данных


 Name   |   Storage Size   |   Representation   |   Description
 ------ | ---------------- | ------------------ | -------------
 point | 16 bytes | Point on a plane | (x,y) 
 line	| 32 bytes | Infinite line (not fully implemented) | 	((x1,y1),(x2,y2)) 
 lseg | 32 bytes | Finite line segment | 	((x1,y1),(x2,y2)) 
 box | 32 bytes	| Rectangular box | ((x1,y1),(x2,y2)) 
 path | 	16+16n bytes	| Closed path (similar to polygon) | ((x1,y1),...) 
 path | 	16+16n bytes	| Open path | [(x1,y1),...] 
 polygon | 40+16n	| Polygon (similar to closed path)  | ((x1,y1),...) 
 circle | 24 bytes	| Circle	 |  <(x,y),r> (center point and radius) 


Пример, зачем это нужно: https://habr.com/post/245015/

# Перечислимый тип

Хранить более эффективно, чем в виде строк

<pre>
CREATE TYPE week AS ENUM ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun');
</pre>


# Полезные команды

## Размер БД

Кооманда pg_database_size вычисляет размер БД в байтах

<pre>
SELECT pg_size_pretty(pg_database_size(current_database()));
 pg_size_pretty
----------------
 3000 MB
(1 row)

</pre>

## Пользовательские таблицы

Команда формирует список таблиц, которые были созданы пользователем

<pre>
SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','pg_catalog');
 table_name
------------
 links
 ratings
(2 rows)
</pre>

Описание таблицы можно получить при помощи команды \d

<pre>
\d ratings
                    Table "public.ratings"
  Column   |       Type       | Collation | Nullable | Default
-----------+------------------+-----------+----------+---------
 userid    | bigint           |           |          |
 movieid   | bigint           |           |          |
 rating    | double precision |           |          |
 timestamp | bigint           |           |          |

</pre>

Можно узнать размер таблицы

<pre>
SELECT pg_size_pretty(pg_relation_size('ratings'));
 pg_size_pretty
----------------
 2990 MB
(1 row)
</pre>

Или полный размер данных (вместе с инднксами и т.д.)

<pre>
SELECT pg_size_pretty(pg_total_relation_size('ratings'));
 pg_size_pretty
----------------
 2991 MB
(1 row)
</pre>

Размер данных в конкретном столбце

<pre>
SELECT pg_size_pretty(SUM(pg_column_size(userId))) FROM ratings;
 pg_size_pretty
----------------
 397 MB
(1 row)
</pre>

# Администрирование и мониторинг

Запрос, который выводит информацию об активных запросах.

<pre>
postgres=# SELECT pid, age(query_start, clock_timestamp()), usename, query, backend_type FROM pg_stat_activity WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%';
 pid | age | usename  | query |    backend_type
-----+-----+----------+-------+---------------------
  66 |     |          |       | autovacuum launcher
  68 |     | postgres |       | background worker
  64 |     |          |       | background writer
  63 |     |          |       | checkpointer
  65 |     |          |       | walwriter
(5 rows)
</pre>


Если запрос висит слишком долго, его стоит прибить командой

<pre>
SELECT pg_terminate_backend(procpid);
</pre>

С помощью команды \timing можно определить время выполнения запроса

<pre>
\timing
Timing is on.
SELECT movieId, COUNT(*) num_rating FROM public.ratings WHERE ratings.movieID > 100000 GROUP BY 1 LIMIT 10;
 movieid | num_rating
---------+------------
  100001 |          2
  100003 |          6
  100006 |          6
  100008 |         28
  100010 |         88
  100013 |         18
  100015 |          4
  100017 |         50
  100032 |         30
  100034 |         64
(10 rows)

Time: 1494.318 ms (00:01.494)
</pre>

Ускорить запрос можно с помощью создания индексов. Индексы можно создавать на лету

<pre>
CREATE INDEX ON ratings(movieId);

CREATE INDEX
Time: 37427.672 ms (00:37.428)
</pre>

После того, как индекс создан - запросы начинают выполнятся бодрее, время сокращается в сотни раз
<pre>
CREATE INDEX ON ratings(movieId);

CREATE INDEX
Time: 38493.878 ms (00:38.494)

SELECT movieId, COUNT(*) num_rating FROM public.ratings WHERE ratings.movieID > 100000 GROUP BY 1 LIMIT 10;
 movieid | num_rating
---------+------------
  100001 |          2
  100003 |          6
  100006 |          6
  100008 |         28
  100010 |         88
  100013 |         18
  100015 |          4
  100017 |         50
  100032 |         30
  100034 |         64
(10 rows)

Time: 5.289 ms
</pre>

# Хранимые процедуры

Хранимые процедуры - это функции, которые определяются пользователем. Их можно создавать  для более гибкого препроцессинга данных.

<pre>
CREATE OR REPLACE FUNCTION imdb_url(imdb_id VARCHAR) RETURNS VARCHAR AS $$ BEGIN RETURN CONCAT(CAST('http://www.imdb.com/' as VARCHAR) , CAST(imdb_id as VARCHAR)) ; END; $$ LANGUAGE plpgsql;

CREATE FUNCTION
Time: 3.637 ms

SELECT imdb_url(links.imdbId) FROM public.links LIMIT 10;
          imdb_url
-----------------------------
 http://www.imdb.com/0114709
 http://www.imdb.com/0113497
 http://www.imdb.com/0113228
 http://www.imdb.com/0114885
 http://www.imdb.com/0113041
 http://www.imdb.com/0113277
 http://www.imdb.com/0114319
 http://www.imdb.com/0112302
 http://www.imdb.com/0114576
 http://www.imdb.com/0113189
(10 rows)

Time: 1.478 ms
</pre>

Мы создали хранимую процедуру, в которой приклеиваем к id оставшуюся часть URL. Хранимые процедуры можно делать и более сложными и использовать их  для препроцессинга данных, или внутри триггеров.

## Схема запроса

Оператор EXPLAIN демострирует этапы выполнения запроса и может быть использован для оптимизации.

<pre>
EXPLAIN SELECT userId, COUNT(*) num_rating FROM public.links LEFT JOIN public.ratings ON links.movieid=ratings.movieid GROUP BY 1 LIMIT 10;
                                      QUERY PLAN
--------------------------------------------------------------------------------------
 Limit  (cost=1880431.03..1880431.13 rows=10 width=16)
   ->  HashAggregate  (cost=1880431.03..1880749.83 rows=31880 width=16)
         Group Key: ratings.userid
         ->  Hash Right Join  (cost=1323.47..1620188.15 rows=52048576 width=8)
               Hash Cond: (ratings.movieid = links.movieid)
               ->  Seq Scan on ratings  (cost=0.00..903196.76 rows=52048576 width=16)
               ->  Hash  (cost=750.43..750.43 rows=45843 width=8)

</pre>
