# coding=utf-8
import os

from lz4.block import compress, decompress
from msgpack import packb, unpackb
from msgpack_numpy import decode, encode
import numpy as np

import psycopg2
import psycopg2.extensions
from pymongo import MongoClient
from redis import Redis


class PostgresStorage:
    def __init__(self):
        # подключение к Postgres
        params = {
            "host": os.environ['APP_POSTGRES_HOST'],
            "port": os.environ['APP_POSTGRES_PORT'],
            "user": 'postgres'
        }
        self.conn = psycopg2.connect(**params)

        # дополнительные настройки
        psycopg2.extensions.register_type(
            psycopg2.extensions.UNICODE,
            self.conn
        )
        self.conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        self.cursor = self.conn.cursor()

    def load_data(self):
        # создаём таблички
        self.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS links (
            movieId bigint,
            imdbId varchar(20),
            tmdbId varchar(20)
        );
        CREATE TABLE IF NOT EXISTS ratings (
            userId bigint,
            movieId bigint,
            rating float(25),
            timestamp bigint
        );"""
        )

        # заливаем данные
        self._load_csv('/data/ratings_small.csv', 'ratings')
        self._load_csv('/data/links.csv', 'links')
        print("Данные залиты в Postgres")

        self.conn.commit()

    def _load_csv(self, csv_path, table_name):
        with open(csv_path, 'r') as f:
            next(f)  # Skip the header row.
            self.cursor.copy_from(f, table_name, sep=',')

    def run_sql_str(self, sql_str):
        """Исполняем SQL и возвращаем PandasDF"""

        self.cursor.execute(sql_str)

        ui_data = [a for a in self.cursor.fetchall()]

        self.conn.commit()

        return ui_data


class MongoStorage:
    def __init__(self):
        # Mongo
        mongo_conf = {
            'host': os.environ['APP_MONGO_HOST'],
            'port': int(os.environ['APP_MONGO_PORT'])
        }
        storage = MongoClient(**mongo_conf)
        self.mongo_recsys_storage = storage.get_database("recsys")

    def load_data(self, prefix, data):
        selector = {'id': {'$in': [user_id for user_id in data.keys()]}}
        collection = self.mongo_recsys_storage.get_collection(prefix)
        collection.delete_many(selector)
        collection.insert_many(
            [
                {
                    'id': int(user_id),
                    'value': compress(packb(data[user_id], default=encode))
                }
                for user_id in data
            ]
        )

    def get_data(self, prefix, doc_id):
        latent_user_factors = np.array([])
        doc = {'id': int(doc_id)}
        collection = self.mongo_recsys_storage.get_collection(prefix)
        mongo_doc = collection.find_one(doc)
        if mongo_doc is None:
            print("Пользователя с id %(id)d не существует" % mongo_doc)
        else:
            latent_user_factors = unpackb(decompress(mongo_doc['value']), object_hook=decode)
        return latent_user_factors


class RedisStorage:
    def __init__(self):
        # Redis
        REDIS_CONF = {
            "host": os.environ['APP_REDIS_HOST'],
            "port": os.environ['APP_REDIS_PORT'],
            "db": 0
        }
        self.storage = Redis(**REDIS_CONF)

    def load_data(self, prefix, data):
        self.storage.set(prefix, compress(packb(data, default=encode)))

    def get_data(self, prefix):
        result = np.array([])
        redis_data = self.storage.get(prefix)
        if redis_data is not None:
            result = unpackb(decompress(redis_data), object_hook=decode)
        return result
