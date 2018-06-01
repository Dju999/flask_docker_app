# Получаем фичи с помощью SQL

## Базовые статистики

Будем работать в обычном докере, в который уже залиты предыдущие таблицы

<pre>
docker run -it --rm --link netology-postgres:postgres postgres psql -h postgres -U postgres
</pre>

### SUM

Простое суммирование, в качестве аргемента принимает имя колонки

Примечание: признак должен быть числовой, иначе результаты могут быть странные

<pre>
postgres=# select SUM(rating) from public.ratings;
   sum    
----------
 91816043
(1 row)
</pre>

### COUNT

Простой счётчик записей. ЕСли передать модификатор DISTINCT - получим только уникальные записи

<pre>
select COUNT(userId) as count, COUNT(DISTINCT userId) as count_distinct, COUNT(DISTINCT userId)/CAST(COUNT(userId) as float) unique_fraction from public.ratings;
</pre>

Несколько особенностей запроса

* несколько аггрегатов в одной строке
* использовали alias - дали имя колонке
* применили арифметическую операцию к результатам запроса (деление) - посчитали отношение уникальных userId к общему числу записей.

### AVG

AVG (AVERAGE) - вычисление среднего значения

<pre>
postgres=# select AVG(rating) from public.ratings;
       avg        
------------------
 3.52809035436088
(1 row)
</pre>

## Базовые статистики по группам: GROUP BY

Кроме расчёта статистик по всей таблице можно считать значения статистик внутри групп, с помощью аггрегирующего оператора GROUP BY:

Например, можем найти самых активных пользователей - тех, кто поставил больше всего оценок

<pre>
postgres=# SELECT userId, COUNT(rating) as activity from public.ratings GROUP BY userId ORDER BY activity DESC LIMIT 5;
 userid | activity 
--------+----------
  45811 |    18276
   8659 |     9279
 270123 |     7638
 179792 |     7515
 228291 |     7410
(5 rows)
</pre>

Группировать можно по нескольким полям

<pre>
postgres=# SELECT userId, to_char(to_timestamp(timestamp), 'YYYY/MM/DD') as dt, COUNT(rating) as activity from public.ratings GROUP BY 1,2 ORDER BY activity DESC LIMIT 5;
 userid |     dt     | activity 
--------+------------+----------
 270123 | 2015/07/05 |     6663
  45811 | 2015/12/15 |     5085
  24025 | 2016/03/27 |     4946
 101276 | 2016/05/09 |     4834
 258253 | 2017/02/10 |     4227
(5 rows)
</pre>

## Фильтрация: HAVING

Аналогично WHERE оператор HAVING позволяет проводить фильтрацию. Разница том, что фильтруются поля с агрегирующими функциями

<pre>
postgres=# SELECT DISTINCT userId, AVG(rating) as avg_rating FROM public.ratings GROUP BY userId HAVING AVG(rating) < 5 LIMIT 5;
 userid |    avg_rating    
--------+------------------
      1 | 4.27777777777778
      2 | 3.31818181818182
      3 |              3.1
      4 |              3.5
      5 | 4.26923076923077
(5 rows)

</pre>
