# Из Python в Mongodb

Для выгрузки данных из MongoDB (или их загрузки) Существует библиотека PyMongo. Бибилиотека представляет собой python-обёртку над API MongoDB.

Создадим класс клиента для доступа к БД и инициируем подключение
<pre>
import os

from pymongo import MongoClient
mongo = MongoClient(**{
    'host': os.environ['APP_MONGO_HOST'],
    'port': int(os.environ['APP_MONGO_PORT'])
})
db = mongo.get_database(name="movie")

collection = db['tags']
</pre>

Функция get_database() возвращает доступ к БД, с которой мы будем работать. Collection - это доступ к соответствующей коллекции
Заметим, что самой БД не существует - она будет создана в момент первого запроса

Для примера загрузки данных мы будем работать с файлом keyword.tsv, который выглядит следующим образом:
<pre>
# head -n3 '/data/keywords.tsv'
862	[{'id': 931, 'name': 'jealousy'}, {'id': 4290, 'name': 'toy'}, {'id': 5202, 'name': 'boy'}, {'id': 6054, 'name': 'friendship'}, {'id': 9713, 'name': 'friends'}, {'id': 9823, 'name': 'rivalry'}, {'id': 165503, 'name': 'boy next door'}, {'id': 170722, 'name': 'new toy'}, {'id': 187065, 'name': 'toy comes to life'}]
8844	[{'id': 10090, 'name': 'board game'}, {'id': 10941, 'name': 'disappearance'}, {'id': 15101, 'name': "based on children's book"}, {'id': 33467, 'name': 'new home'}, {'id': 158086, 'name': 'recluse'}, {'id': 158091, 'name': 'giant insect'}]
15602	[{'id': 1495, 'name': 'fishing'}, {'id': 12392, 'name': 'best friend'}, {'id': 179431, 'name': 'duringcreditsstinger'}, {'id': 208510, 'name': 'old men'}]
</pre>

То есть это пары <movieID, movieTags>, разделённые символом '\t'. В монго можно записать объекты типа dict из python, то есть файл нужно приобразовать.

Разобъем каждую строку на пачку dict вида {'id': 931, 'name': 'jealousy', 'movieId': '862'}, где id - идентификатор тега а movieId - идентификатор фильма, котором принадлежит тег.
Для преобразования будем использовать python:
<pre>
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
</pre>

Таким образом мы сформировали массив tag_data, который состоит из сформированных по тегам триплетов.
Запись в MongoDB была произведена с помощью функции  *insert_many*. Всё просто и не нужно к

Запускаем заливку данных (скрипт python /home/pymongo_example.py)
<pre>
# python /home/pymongo_example.py
2018-08-06 04:06:20,529 : INFO : Создадаём подключение к Mongo
2018-08-06 04:06:23,207 : INFO : sample tags: [
    {'id': 931, 'name': 'jealousy', 'movieId': '862', '_id': ObjectId('5b67c93dde1440000bf352b3')},
    {'id': 4290, 'name': 'toy', 'movieId': '862', '_id': ObjectId('5b67c93dde1440000bf352b4')},
    {'id': 5202, 'name': 'boy', 'movieId': '862', '_id': ObjectId('5b67c93dde1440000bf352b5')}
 ]
2018-08-06 04:06:23,208 : INFO : Общее количество документов к коллекции: 317361
</pre>

Давайте подключимся к Mongo и проверим, что число данных совпадает
<pre>
mongo $APP_MONGO_HOST:$APP_MONGO_PORT/movie
> db.tags.count()
317361
</pre>

Количество тегов совпадает. Посмотрим на конкретные документы:

<pre>
> db.tags.find().limit(5)
{ "_id" : ObjectId("5b67c14dce5c4300130cfc85"), "1" : 2 }
{ "_id" : ObjectId("5b67c1b596e8a6000b7f71cf"), "id" : 931, "name" : "jealousy", "movieId" : "862" }
{ "_id" : ObjectId("5b67c1b596e8a6000b7f71d0"), "id" : 4290, "name" : "toy", "movieId" : "862" }
{ "_id" : ObjectId("5b67c1b596e8a6000b7f71d1"), "id" : 5202, "name" : "boy", "movieId" : "862" }
{ "_id" : ObjectId("5b67c1b596e8a6000b7f71d2"), "id" : 6054, "name" : "friendship", "movieId" : "862" }
</pre>

Для выгрузки данных из Mongo у объекта MongoClient тоже существует много разных ручек.
Для демонстрации напишем код, который подсчитывает самые популярные теги

Сформируем пайплан для агрегации
<pre>
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
</pre>

Выполним пайплан - получим курсор, по результатам которого можно итерироваться:
<pre>
print([i for i in collection.aggregate(pipline)])
</pre>

Результат выдачи:
<pre>
2018-08-06 09:00:00,941 : INFO : Пример аггрегации данных: top-5 самых популярных тегов
[{'_id': 'woman director', 'tag_count': 9345}, {'_id': 'independent film', 'tag_count': 5790}, {'_id': 'murder', 'tag_count': 3924}, {'_id': 'based on novel', 'tag_count': 2505}, {'_id': 'musical', 'tag_count': 2202}]
</pre>

Готово! теперь мы умеем загружать данные в Mongo и строить сложные запросы к данным.