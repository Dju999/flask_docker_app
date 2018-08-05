import datetime
import logging
import os
from subprocess import call

import numpy as np
import pandas as pd
from sqlalchemy import create_engine


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# загружаем данные в Postgres
call("bash /home/load_data.sh", shell=True)

engine = create_engine('postgresql://postgres:@{}'.format(os.environ['APP_POSTGRES_HOST']))

# загрузка данных из текстового файла
links = pd.read_csv('/data/links.csv', sep=',', header='infer')
links.loc[links.tmdbId.isnull()] = 0
links[['tmdbId']] = links.tmdbId.astype(np.int64)
logger.info("Таблица ссылок")
print(links.head())

# загрузка данных из Postgres
ratings = pd.read_sql('SELECT * FROM ratings', engine)
logger.info("Таблица рейтингов")
print(ratings.head())
logger.info("Загрузили типы данных {}".format(ratings.dtypes))

# пример JOIN
logger.info("Join таблицы ratings на links")
df = links.merge(ratings, how='inner', left_on='movieId', right_on='movieid').head()
print(df.head())

# пример группировки
logger.info("Пример группировки данных")
ratings_counter = ratings[
    ratings.timestamp > datetime.datetime.strptime('2015-01-01', '%Y-%m-%d').timestamp()
].groupby(
    by=['userid']
)['movieid'].count().sort_values(ascending=False)
print(ratings_counter.head())

# считаем несколько метрик
logger.info("Несколько агрегированных метрик")
df = ratings[
    ratings.timestamp > datetime.datetime.strptime('2015-01-01', '%Y-%m-%d').timestamp()
].groupby(
    by=['userid']
)['rating'].agg(
    [np.ma.count, np.mean, np.std]
).head()
print(df.head())

# применяем оконные функции
logger.info("Демонстрация оконных функций")
window_ranked_ratings = ratings.assign(
    rnk=ratings.groupby(['userid'])[['timestamp']]
               .rank(method='first', ascending=True)
).query('rnk<5').sort_values(['userid', 'timestamp'])
print(window_ranked_ratings.head())
