# Оконные функции SQL

Старт контейнера
<pre>
sudo docker-compose --project-name postgres-client -f docker-compose.yml up --build -d; sudo docker-compose --project-name postgres-client -f docker-compose.yml run --rm postgres-client
</pre>

Загрузка данных и старт БД:
<pre>
sh /home/load_data.sh; psql --host $APP_POSTGRES_HOST -U postgres;
</pre>

Оконные функции - полезный инструмент для построения сложных аналитических запросов.

Для их использования нужно задать парметры окна и функцию, которую хотим посчитать на каждом объекте внутри окна.

Простой пример - функция ROW_NUMBER(). Эта функция нумерует строки внутри окна. Пронумеруем контент для каждого пользователя в порядке убывания рейтингов.

<pre>
SELECT
  userId, movieId, rating,
  ROW_NUMBER() OVER (PARTITION BY userId ORDER BY rating DESC) as movie_rank
FROM (SELECT DISTINCT userId, movieId, rating FROM ratings WHERE userId <>1 LIMIT 1000) as sample
ORDER BY userId, rating DESC, movie_rank LIMIT 20;

userid | movieid | rating | movie_rank 
--------+---------+--------+------------
      2 |    1356 |      5 |          1
      2 |     339 |      5 |          2
      2 |     648 |      4 |          3
      2 |     605 |      4 |          4
      2 |    1233 |      4 |          5
      2 |    1210 |      4 |          6
      2 |     377 |      4 |          7
      2 |     260 |      4 |          8
      2 |      79 |      4 |          9
      2 |     628 |      4 |         10
      2 |      64 |      4 |         11
      2 |      58 |      3 |         12
      2 |      25 |      3 |         13
      2 |     762 |      3 |         14
</pre>

Параметры запроса:

* ROW_NUMBER - функция, которую применяем к окну
* OVER - описание окна. Описание окна содержит:
** PARTITION BY - поле (или список полей), которые описывают группу строк для применения оконной функции
** ORDER BY - поле, которое задаёт порядок записей внутри окна. Для полей внутри ORDER BY можно применять стандартные модификаторы DESC, ASC

коннная функция никак не меняет количество строк в выдаче, но к каждой строке добавляется полезная информация - например, про порядковый номер строки внутри окна

Названия функций обычно отражают их ссмысл. НИже будут прриведены примеры использования и результаты запросо

# SUM()

Суммирует значения внутри окна. Посчитаем странную метрику - разделим каждое значение рейтинга на сумму всех рейтингов этого пользователя.

<pre>
SELECT userId, movieId, rating,
    rating / SUM(rating) OVER (PARTITION BY userId) as strange_rating_metric
    FROM (SELECT DISTINCT userId, movieId, rating FROM ratings WHERE userId <>1 LIMIT 1000) as sample
    ORDER BY userId, rating DESC LIMIT 20;
 userid | movieid | rating | strange_rating_metric 
--------+---------+--------+-----------------------
      2 |     339 |      5 |    0.0684931506849315
      2 |    1356 |      5 |    0.0684931506849315
      2 |     648 |      4 |    0.0547945205479452
      2 |      64 |      4 |    0.0547945205479452
      2 |      79 |      4 |    0.0547945205479452
      2 |     260 |      4 |    0.0547945205479452
      2 |    1233 |      4 |    0.0547945205479452
      2 |    1210 |      4 |    0.0547945205479452
      2 |     377 |      4 |    0.0547945205479452
      2 |     605 |      4 |    0.0547945205479452
      2 |     628 |      4 |    0.0547945205479452
      2 |     762 |      3 |    0.0410958904109589
      2 |     141 |      3 |    0.0410958904109589
      2 |     780 |      3 |    0.0410958904109589
      2 |       5 |      3 |    0.0410958904109589
      2 |      58 |      3 |    0.0410958904109589
      2 |      25 |      3 |    0.0410958904109589
      2 |    1475 |      3 |    0.0410958904109589
      2 |      32 |      2 |    0.0273972602739726
      2 |    1552 |      2 |    0.0273972602739726
(20 rows)

</pre>

# COUNT(), AVG()

Счётчик элементов внутри окна, а так же функция Average(). Для наглядности воспользуемся ими одновременно - результаты не должны отличаться.
Вычислим полезную метрику - отклонение рейтинга пользователя от среднего рейтинга, который он склонен выставлять

<pre>
SELECT userId, movieId, rating,
    rating - AVG(rating) OVER (PARTITION BY userId) rating_deviance_simplex,
    rating - SUM(rating) OVER (PARTITION BY userId) /COUNT(rating) OVER (PARTITION BY userId) as rating_deviance_complex
    FROM (SELECT DISTINCT userId, movieId, rating FROM ratings WHERE userId <>1 LIMIT 1000) as sample
    ORDER BY userId, rating DESC LIMIT 20;
 userid | movieid | rating | rating_deviance_simplex | rating_deviance_complex 
--------+---------+--------+-------------------------+-------------------------
      2 |     339 |      5 |        1.68181818181818 |        1.68181818181818
      2 |    1356 |      5 |        1.68181818181818 |        1.68181818181818
      2 |     648 |      4 |       0.681818181818182 |       0.681818181818182
      2 |      64 |      4 |       0.681818181818182 |       0.681818181818182
      2 |      79 |      4 |       0.681818181818182 |       0.681818181818182
      2 |     260 |      4 |       0.681818181818182 |       0.681818181818182
      2 |    1233 |      4 |       0.681818181818182 |       0.681818181818182
      2 |    1210 |      4 |       0.681818181818182 |       0.681818181818182
      2 |     377 |      4 |       0.681818181818182 |       0.681818181818182
      2 |     605 |      4 |       0.681818181818182 |       0.681818181818182
      2 |     628 |      4 |       0.681818181818182 |       0.681818181818182

</pre>

# MIN(), MAX()

<pre>
SELECT userId, movieId, rating,
    (rating - MIN(rating) OVER (PARTITION BY userId))/(MAX(rating) OVER (PARTITION BY userId)) rating_deviance_simplex
    from (SELECT DISTINCT userId, movieId, rating FROM ratings WHERE userId <>1 LIMIT 1000) as sample
    ORDER BY userId, rating DESC LIMIT 20;
 userid | movieid | rating | rating_deviance_simplex 
--------+---------+--------+-------------------------
      2 |     339 |      5 |                       1
      2 |    1356 |      5 |                       1
      2 |     648 |      4 |                    0.75
      2 |      64 |      4 |                    0.75
      2 |      79 |      4 |                    0.75
      2 |     260 |      4 |                    0.75
      2 |    1233 |      4 |                    0.75
      2 |    1210 |      4 |                    0.75
      2 |     377 |      4 |                    0.75
      2 |     605 |      4 |                    0.75
      2 |     628 |      4 |                    0.75
      2 |     762 |      3 |                     0.5
      2 |     141 |      3 |                     0.5
      2 |     780 |      3 |                     0.5

</pre>

# Rank(), Dense_Rank(), Percent_Rank()

Ранжирующие функции - это RowNumber() "на стероидах". Различия возникают на одинаковых строках: Rank строит индекс таких строк с разрывами (gap),
а Dense_Rank без разрывов (плотный). Percent_rank конвертирует нормера строк в значение перцентилей

<pre>
SELECT userId, movieId, rating,
    RANK() OVER (PARTITION BY userId ORDER BY RATING) r_rank,
    DENSE_RANK() OVER (PARTITION BY userId ORDER BY RATING) r_rank_dense,
    PERCENT_RANK() OVER (PARTITION BY userId ORDER BY RATING)
    FROM (SELECT DISTINCT userId, movieId, rating FROM ratings WHERE userId <>1 LIMIT 1000) as sample
    ORDER BY userId, rating ASC LIMIT 15;
 userid | movieid | rating | r_rank | r_rank_dense |    percent_rank    
--------+---------+--------+--------+--------------+--------------------
      2 |     786 |      1 |      1 |            1 |                  0
      2 |     788 |      1 |      1 |            1 |                  0
      2 |    1552 |      2 |      3 |            2 | 0.0952380952380952
      2 |      32 |      2 |      3 |            2 | 0.0952380952380952
      2 |       5 |      3 |      5 |            3 |   0.19047619047619
      2 |      58 |      3 |      5 |            3 |   0.19047619047619
      2 |     762 |      3 |      5 |            3 |   0.19047619047619
      2 |    1475 |      3 |      5 |            3 |   0.19047619047619
      2 |      25 |      3 |      5 |            3 |   0.19047619047619
      2 |     141 |      3 |      5 |            3 |   0.19047619047619
      2 |     780 |      3 |      5 |            3 |   0.19047619047619
      2 |    1210 |      4 |     12 |            4 |  0.523809523809524
      2 |      64 |      4 |     12 |            4 |  0.523809523809524
      2 |     605 |      4 |     12 |            4 |  0.523809523809524

</pre>

# first_value(), last_value(), nth_value, lag()

Функции, которые находят значение из другой строки внутри окна.

* first_value - первое значение в окне
* last_value - крайнее значение в окне
* nth_value - элемент окна под номером n
* lag - вычисляет для каждой строки смещение

<pre>
SELECT userId, movieId, rating,
    FIRST_VALUE(movieId) OVER (PARTITION BY userId ORDER BY RATING) top_content,
    last_value(movieId) OVER (PARTITION BY userId ORDER BY RATING) bottom_content,
    nth_value(movieId, 5) OVER (PARTITION BY userId ORDER BY RATING) r_nth,
    lag(movieId, 5) OVER (PARTITION BY userId ORDER BY RATING) r_lag
 FROM (SELECT DISTINCT userId, movieId, rating FROM ratings WHERE userId <>1 LIMIT 1000) as sample
 ORDER BY userId, rating ASC LIMIT 15;
 userid | movieid | rating | top_content | bottom_content | r_nth | r_lag 
--------+---------+--------+-------------+----------------+-------+-------
      2 |     786 |      1 |         786 |            788 |       |      
      2 |     788 |      1 |         786 |            788 |       |      
      2 |    1552 |      2 |         786 |             32 |       |      
      2 |      32 |      2 |         786 |             32 |       |      
      2 |       5 |      3 |         786 |            780 |     5 |      
      2 |      58 |      3 |         786 |            780 |     5 |   786
      2 |     762 |      3 |         786 |            780 |     5 |   788
      2 |    1475 |      3 |         786 |            780 |     5 |  1552
      2 |      25 |      3 |         786 |            780 |     5 |    32
      2 |     141 |      3 |         786 |            780 |     5 |     5
      2 |     780 |      3 |         786 |            780 |     5 |    58
      2 |    1210 |      4 |         786 |            377 |     5 |   762
      2 |      64 |      4 |         786 |            377 |     5 |  1475
      2 |     605 |      4 |         786 |            377 |     5 |    25
      2 |     648 |      4 |         786 |            377 |     5 |   141
(15 rows)
</pre>

Аналитические функции - супер-мощная штука. С помощью НИх можно делать крутой препроцессинг данных и эффективно готовить данные для моделей более высогого уровня.
