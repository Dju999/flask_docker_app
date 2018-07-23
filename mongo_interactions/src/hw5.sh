#!/bin/sh

# команда для загрузки файла в MONGO
/usr/bin/mongoimport --host $APP_MONGO_HOST --port $APP_MONGO_PORT --db movies --collection tags --file /data/simple_tags.json

# в файле agg.js три задачи
# - подсчитайте число элементов в созданной коллекции
# - подсчитайте число фильмов с конкретным тегом - `woman`
# - используя группировку данных ($groupby) вывести top-3 самых распространённых тегов
/usr/bin/mongo $APP_MONGO_HOST:$APP_MONGO_PORT/movies /home/agg.js