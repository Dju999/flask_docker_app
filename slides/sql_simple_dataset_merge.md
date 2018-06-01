## Объединение датасетов

Ингда требуется достать из двух различных таблиц данные с одинаковым набором полей - напримерЮ когда вы хотите проанализировать информацию об одном и том же процессе из двух независимых источников.

Если нужно объединить две выдачи - используем UNION (можно с модификатором UNION ALL)

<pre>
postgres=# (SELECT userId, to_char(to_timestamp(timestamp), 'YYYY/MM/DD') as dt from public.ratings WHERE to_char(to_timestamp(timestamp), 'YYYY/MM/DD')='2002/09/03' LIMIT 2) UNION ALL  (SELECT userId, to_char(to_timestamp(timestamp), 'YYYY/MM/DD') as dt from public.ratings WHERE to_char(to_timestamp(timestamp), 'YYYY/MM/DD')='2015/09/03' LIMIT 2) LIMIT 5;
 userid |     dt     
--------+------------
  41615 | 2002/09/03
  41615 | 2002/09/03
  43232 | 2015/09/03
  43232 | 2015/09/03
(4 rows)
</pre>

Выборки можно пересекать, используя INTERSECT

<pre>
postgres=# (SELECT userId from public.ratings WHERE to_char(to_timestamp(timestamp), 'YYYY/MM/DD')>='2010/09/03') INTERSECT  (SELECT userId from public.ratings WHERE to_char(to_timestamp(timestamp), 'YYYY/MM/DD')<'2015/09/03') LIMIT 5; userid 
--------
  86036
 212698
 151812
 106095
  63618
(5 rows)
</pre>

А можно строить разность двух выборок с помощью EXCEPT
<pre>
postgres=# (SELECT userId from public.ratings WHERE to_char(to_timestamp(timestamp), 'YYYY/MM/DD')>='2010/09/03') EXCEPT  (SELECT userId from public.ratings WHERE to_char(to_timestamp(timestamp), 'YYYY/MM/DD')<'2015/09/03') LIMIT 5; userid 

 userid 
--------
 183089
 217030
 263381
 223071
 167276
(5 rows)
</pre>

