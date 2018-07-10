import os

from flask import Flask, render_template, request

from db_interactions import PostgresStorage, MongoStorage, RedisStorage
from recsys_model import SVDRecsys

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

recsys = SVDRecsys(postgres_storage, mongo_storage, redis_storage)
print("Модель обучена, данные сохранены")

@app.route('/')
def hello():
    redis_storage.storage.incr('hits')
    return render_template('index.html')


@app.route('/recs')
def recs():
    personal_recs = recsys.get_recommendations(
        request.args.get("user_id", type=int, default=100),
        request.args.get("top", type=int, default=50)
    )
    return render_template('rec_page.html', recs=personal_recs)


if __name__=='__main__':
    print("Прокинули порт {}, Redis {}".format(bind_port, redis_storage.storage))
    app.run(host="0.0.0.0", port=int(bind_port), debug=True)
