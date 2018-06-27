import os

from flask import Flask

from python_db import PostgresStorage, MongoStorage, RedisStorage

# если сначала работало, а потом поломалось - можно удалить контейнеры
# sudo docker rm $(sudo docker ps -a -q)
# sudo docker rmi $(sudo docker images -a -q)
# docker volume prune -f

# загружаем данные в Postgres
postgres_storage = PostgresStorage()
postgres_storage.load_data()
# подключение к Mongo
mongo_storage = MongoStorage()
# подключение к Redis
redis_storage = RedisStorage()

app = Flask(__name__)
bind_port = os.environ['BIND_PORT']


@app.route('/')
def hello():
    redis_storage.storage.incr('hits')
    return 'Hello World! I have been seen {} times.'.format(redis_storage.storage.get('hits'))

if __name__=='__main__':
    print("Прокинули порт {}, Redis {}".format(bind_port, redis_storage.storage))
    app.run(host="0.0.0.0", port=int(bind_port), debug=True)
