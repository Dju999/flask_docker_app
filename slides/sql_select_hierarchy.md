## Обобщённые табличные выражения

Если запрос слишком сложные - логику выборки можно разделить на части.

Обобщённое табличное выражение (Common Table Expression) - возможность вынести часть логики в отдельное выражение

<pre>
postgres=# WITH tmp_table as (SELECT * from public.ratings WHERE to_char(to_timestamp(timestamp), 'YYYY/MM/DD')<'2010/09/03')  SELECT DISTINCT userId, COUNT(to_char(to_timestamp(timestamp), 'YYYY/MM/DD')) as dt_num FROM tmp_table GROUP BY userId LIMIT 10;
 userid | dt_num 
--------+--------
      2 |     22
      3 |     10
      4 |     62
      5 |     26
      6 |      4
      8 |    113
      9 |     84
     10 |     13
     11 |    227
     12 |    248
(10 rows)

</pre>

## Подзапросы

Другой способ разделения логики формирования выборки - подзапросы. Подзапрос - это SELECT, результаты которого используются в другом SELECT/

<pre>
postgres=# SELECT DISTINCT userId FROM public.ratings WHERE rating < (SELECT AVG(rating) from public.ratings) LIMIT 5;
 userid 
--------
 233338
 174416
 196916
 164125
 157514
(5 rows)
</pre>
