SELECT ('ФИО: капитан Америка');

-- спользуя функцию определения размера таблицы, вывести top-5 самых больших таблиц базы

SELECT table_name FROM information_schema.tables LIMIT 1;

-- array_agg: собрать в массив все фильмы, просмотренные пользователем (без повторов)
SELECT userID, array_agg(movieId) as user_views FROM ratings WHERE userID=1;

-- таблица user_movies_agg, в которую сохраните результат предыдущего запроса
DROP TABLE IF EXISTS user_movies_agg;
SELECT userID, user_views INTO public.user_movies_agg FROM (SELECT userID, array_agg(movieId) as user_views FROM ratings WHERE userID=1) WHERE userID=1;

SELECT * FROM user_movies_agg LIMIT 3;

-- Используя следующий синтаксис, создайте функцию cross_arr оторая принимает на вход два массива arr1 и arr2.
-- Функциия возвращает массив, который представляет собой пересечение контента из обоих списков.
-- Примечание - по именам к аргументам обращаться не получится, придётся делать через $1 и $2.

CREATE OR REPLACE FUNCTION cross_arr (int[], int[]) RETURNS int[] language sql as $FUNCTION$ тело_функции ; $FUNCTION$;

-- Сформируйте запрос следующего вида: достать из таблицы всевозможные наборы u1, r1, u2, r2.
-- u1 и u2 - это id пользователей, r1 и r2 - соответствующие массивы рейтингов
-- ПОДСКАЗКА: используйте CROSS JOIN
SELECT agg.userId as u1, agg.userId as u2, agg.array_agg as ar1, agg.array_agg as ar2 from user_movies_agg as agg

-- Оберните запрос в CTE и примените к парам <ar1, ar2> функцию CROSS_ARR, которую вы создали
-- вы получите триплеты u1, u2, crossed_arr
-- созхраните результат в таблицу common_user_views
DROP TABLE IF EXISTS common_user_views;
WITH user_pairs as (
  SELECT 1 as u1, 2 as u2, 1 as ar1, 2 as ar2
) SELECT u1, u2, cross_arr(ar1, ar2) INTO public.common_user_views FROM user_pairs;

-- Оставить как есть - это просто SELECT из таблички common_user_views для контроля результата
SELECT * FROM common_user_views LIMIT 3;

-- Создайте по аналогии с cross_arr функцию diff_arr, которая вычитает один массив из другого.
-- Подсказка: используйте оператор SQL EXCEPT.
CREATE OR REPLACE FUNCTION diff_arr (int[], int[]) RETURNS int[] language sql as $FUNCTION$ тело_функции ; $FUNCTION$;

-- Сформируйте рекомендации - для каждой пары посоветуйте для u1 контент, который видел u2, но не видел u1 (в виде массива).
-- Подсказка: нужно заджойнить user_movies_agg и common_user_views и применить вашу функцию diff_arr к соответствующим полям.
-- с векторами фильмов
SELECT * FROM common_user_views CROSS JOIN user_movies_agg LIMIT 10;


------------------------------------------------------------------------------------------------------------------
