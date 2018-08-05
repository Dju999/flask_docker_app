import logging
import os

from pymongo import MongoClient


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Создадаём подключение к Mongo")
mongo = MongoClient(**{
    'host': os.environ['APP_MONGO_HOST'],
    'port': int(os.environ['APP_MONGO_PORT'])
})
db = mongo["movie"]
collection = db['tags']

# подготовка данных - загружаем текстовый файл
agg_filename = '/data/keywords.tsv'
tag_data = []
if db.tags.count() > 0:
    with open(agg_filename, 'r') as f:
        for line in f.readlines():
            movieId, tags = line.strip().split('\t')
            tags = eval(tags)
            for tag in tags:
                tag.update({'movieId': movieId})
                tag_data.append(
                    tag
                )
    collection.insert_many(tag_data)

logger.info("sample tags: {}".format(tag_data[:3]))
logger.info("Общее количество документов к коллекции: {}".format(db['tags'].count()))

# достаём данные из Mongo и считаем агрегаты
logger.info("Пример аггрегации данных: top-5 самых популярных тегов")
pipline = [
    {"$group":
        {"_id": "$name",
         "tag_count":
            {"$sum": 1}
         }
     },
    {"$sort":
        {"tag_count": -1}
     },
    {"$limit": 5}
]
print([i for i in collection.aggregate(pipline)])
