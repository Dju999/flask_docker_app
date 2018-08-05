import logging
import os

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Float, MetaData, String
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from sqlalchemy.sql import label
from sqlalchemy.ext.declarative import declarative_base


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Формируем подключение к Postgres через SQLAlchemy")
# создаём движок для работы с данными
engine = create_engine('postgresql://postgres:@{}:{}'.format(
    os.environ['APP_POSTGRES_HOST'], os.environ['APP_POSTGRES_PORT']))

# создаём пустую таблицу
metadata = MetaData()
ui_table = Table(
    'ui_interactions', metadata,
    Column('user', Integer, primary_key=True),
    Column('item', Integer, primary_key=True),
    Column('rating', Float)
)

# проверка на существование таблицы - уже внутри
metadata.create_all(engine)


class UITriplet(object):
    """
        Интеракция контента с пользователем

        Содержит триплеты пользователь-контент-рейтинг
    """
    def __init__(self, user, item, rating):
        self.user = user
        self.item = item
        self.rating = rating

    def __repr__(self):
        return "<Triplet(user='%s',item='%s', rating='%s')>" % (self.user, self.item, self.rating)


# ассоциируем объект Python с таблицей Postgres
mapper(UITriplet, ui_table)


Base = declarative_base()


class Link(Base):
    """
        Связь с таблицей Links

        Содержит внутренний id и ссылки на imbd и tmdb
    """
    __tablename__ = 'links'

    movieid = Column(Integer, primary_key=True)
    imdbid = Column(String)
    tmdbid = Column(String)

    def __repr__(self):
        return "<Link(movieid='%s',imbdid='%s', rating='%s')>" % (self.movieid, self.imdbid, self.tmdbid)


# создаём вспомогательный объект для работы с таблицей
Session = sessionmaker(bind=engine)
session = Session()

if session.query(UITriplet).count() == 0:
    # читаем построчно файл и формируем из каждой строчки триплет
    agg_filename = '/home/user_agg.tsv'
    ui_data = []
    with open(agg_filename, 'r') as f:
        for line in f.readlines():
            line = line.strip().split('\t')
            ui_data.append(
                UITriplet(line[0], line[1], line[2])
            )

    session.add_all(ui_data)
    session.commit()

logger.info("{} записей загружены в Postgres".format(session.query(UITriplet).count()))

logger.info("Пример выборки с помощью SQLAlchemy{}".format(
    [i for i in session.query(UITriplet).limit(5)]
))

# пример джойна

join_query = session.query(Link).outerjoin(UITriplet, UITriplet.item == Link.movieid).filter(
    UITriplet.item is None
).limit(5)
logger.info("Результат LEFT JOIN {}".format([i for i in join_query]))

# пример GROUP BY:
sqla_grouped_query = session.query(UITriplet.user, label('count', func.count(UITriplet.item))).group_by(UITriplet.user).limit(10)

logger.info("Пример группировки по полю user таблицы ratings {}".format([i for i in sqla_grouped_query]))
