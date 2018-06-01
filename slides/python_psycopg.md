# Взаимодействие Python и Psycorg

Psycorg - быстрая библитека на C, которая позволяет подключаться к БД Postgres.

Это очень тонкий клиент, который по сути позвовляет происзвести три действия: подключиться к БД, выполнить SQL-запрос и получить результат запроса в виду python-объекта.

Подключение к БД выглядит стандартным образом - нужно передать в функцию connect хост, порт и имя пользователя, который инициирует подключение:
<pre>
params = {
    "host": os.environ['APP_POSTGRES_HOST'],
    "port": os.environ['APP_POSTGRES_PORT'],
    "user": 'postgres'
}
conn = psycopg2.connect(**params)
</pre>

Поле этого требуется настроить курсор - объект, который занимается выполнением SQL и выборкой данных

<pre>
psycopg2.extensions.register_type(
    psycopg2.extensions.UNICODE,
    conn
)
conn.set_isolation_level(
    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
)
cursor = conn.cursor()
</pre>

У обекта cursor есть метод execute, который позволяет передать стандартный SQL на выполнение в Postgres:

<pre>
user_item_query_config = {
    "MIN_USERS_FOR_ITEM": 10,
    "MIN_ITEMS_FOR_USER": 3,
    "MAX_ITEMS_FOR_USER": 50,
    "MAX_ROW_NUMBER": 100000
}
sql_str = (
        """
            SELECT
                ratings.userId as user, ratings.movieId as item, AVG(ratings.rating) as rating
            FROM ratings
            -- фильтруем фильмы, которые редко оценивают
            INNER JOIN (
                SELECT
                    movieId, count(*) as users_per_item
                FROM ratings
                GROUP BY movieId
                HAVING COUNT(*) > %(MIN_USERS_FOR_ITEM)d
            ) as movie_agg
                ON movie_agg.movieId = ratings.movieId
            -- фильтруем пользователей, у которых мало рейтингов
            INNER JOIN (
                SELECT
                    userId, count(*) as items_per_user
                FROM ratings
                GROUP BY userId
                HAVING COUNT(*) BETWEEN %(MIN_ITEMS_FOR_USER)d AND %(MAX_ITEMS_FOR_USER)d
            ) as user_agg
                ON user_agg.userId = ratings.userId
            GROUP BY 1,2
            LIMIT %(MAX_ROW_NUMBER)d
        """ % user_item_query_config
)
</pre>

Мы видим, что SQL-запрос представляет собой строковую переменую. В примере так же видно, как с помощью
стандарнтых средств форматирования строк в Python можно передавать в запрос какие-то параметры для более гибкой настройки результатов.

Оталось выполнить запрос на стороне Postgres и выгрузить результат обратно в Python
<pre>
cursor.execute(sql_str)
ui_data = [a for a in cursor.fetchall()]
conn.commit()
</pre>

Метод commit() в явном виде завершает транзакцию. Это особенно важно для конструкций типа INSERT.

Для наглядности сохраним данные в текстовый TSV-файл
<pre>
agg_filename = '/home/user_agg.tsv'
# создаём текстовый файл с результатами
with open(agg_filename, 'w') as f:
    for row in ui_data:
        f.write("{}\t{}\t{}\n".format(row[0], row[1], row[2]))
</pre>

Проверим, что данные в файл записаны корректно
<pre>
# head /home/user_agg.tsv
180	2145	3.0
300	593	4.5
80	32	5.0
541	3175	3.0
343	1042	5.0
644	2174	4.0
347	2571	3.0
40	4993	4.5
375	110	3.0
28	1094	4.0
</pre>

Всё ок! Мы выполнили запрос в Postgres с помощью Psycopg2 и сохранили результаты в текстовый файл, который можно использовать для следующих этапов обработки.