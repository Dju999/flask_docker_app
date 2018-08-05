import os
import psycopg2
import psycopg2.extensions
import logging


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# подключение к Postgres

logger.info("Создаём подключёние к Postgres")
params = {
    "host": os.environ['APP_POSTGRES_HOST'],
    "port": os.environ['APP_POSTGRES_PORT'],
    "user": 'postgres'
}
conn = psycopg2.connect(**params)

# дополнительные настройки
psycopg2.extensions.register_type(
    psycopg2.extensions.UNICODE,
    conn
)
conn.set_isolation_level(
    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
)
cursor = conn.cursor()

# Формируем SQL-запрос
# параметры SQL-запроса
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
        """ % user_item_query_config
)

# выгружаем данные из БД в Python
cursor.execute(sql_str)
ui_data = [a for a in cursor.fetchall()]
conn.commit()
logger.info("Данные по оценкам загружены из Postgres")

agg_filename = '/home/user_agg.tsv'
# создаём текстовый файл с результатами
with open(agg_filename, 'w') as f:
    for row in ui_data:
        f.write("{}\t{}\t{}\n".format(row[0], row[1], row[2]))
logger.info("Данные сохранены в {}".format(agg_filename))
