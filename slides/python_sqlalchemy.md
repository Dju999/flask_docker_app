# ORM в Python:  SQLAclchemy

SQLAclchemy - фреймворк более высокого уровня, написанный на Python, который использует примитивы из других фреймворков - например, Psycopg2.

Эта библиотека реализует ORM-модель (object-relation mappping) - то есть все действия с БД происходят в виде взаимодействий между python-объектами.

При таком подходе SQL-код генерирует сама библиотека, а разработчик оперирует только созданными классами.

Создадим кодключение с помощью SQLAlchemy к Postgres:

<pre>
import os

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Float, MetaData
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:@{}'.format(os.environ['APP_POSTGRES_HOST']))
</pre

Теперь можно описать таблицу в виде класса python и создать её средствами SQLAlchemy

<pre>
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
</pre>

Весь SQL-код вида *CREATE TABLE*  генерируется внутри функции create_all (включая базовую обработку ошибок). Обратите внимание, что первичный ключ состовит из двух столбцов.

Каждая запись в таблице - это объекст соответствующего класса. В нашей таблице хранится информация о взаимодействии пользователя с контентом - создадим соответствующий класс
<pre>
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
        return "<User('%s','%s', '%s')>" % (self.user, self.item, self.rating)
</pre>

 Класс UITriplet и табличку Postgres свяжет объект mapper

<pre>
# ассоциируем объект Python с таблицей Postgres
mapper(UITriplet, ui_table)
</pre>

Если не применить mapper, получим ошибку
<pre>
sqlalchemy.exc.InvalidRequestError: Class <class 'sqlalchemy_example.Link'> does not have a __table__ or __tablename__ specified and does not inherit from an existing table-mapped class.
</pre>

Наконец можно что-то сделать с таблице! Для этого нужно сосздать сессию пользователя (это плата за ACID)
<pre>
# создаём вспомогательный объект для работы с таблицей
Session = sessionmaker(bind=engine)
session = Session()
</pre>

Подготовим данные для добавления в таблицу

<pre>
if session.query(UITriplet).count() == 0:
    agg_filename = '/home/user_agg.tsv'
    ui_data = []
    with open(agg_filename, 'r') as f:
        for line in f.readlines():
            line = line.strip().split('\t')
            ui_data.append(
                UITriplet(line[0], line[1], line[2])
            )
</pre>

У нас получился массив объектов *ui_data* класса *UITriplet* . При помощи SQLAlchemy мы можем добавить эти записи в таблицу
<pre>
if session.query(UITriplet).count() == 0:
    session.add_all(ui_data)
    session.commit()
</pre>

Комит нужно выполнить обязательно - иначе данные не добавится, то есть фнукция *connection.commit()* должна выполнятся после каждого измения данных - например, UPDATE или INSERT.
Результат работы скрипта psycopg_example.py:

<pre>
python /home/psycopg_example.py; python /home/sqlalchemy_example.py

2018-08-05 20:06:35,051 : INFO : Создаём подключёние к Postgres
2018-08-05 20:06:35,118 : INFO : Данные по оценкам загружены из Postgres
2018-08-05 20:06:35,124 : INFO : Данные сохранены в /home/user_agg.tsv

2018-08-05 20:06:45,377 : INFO : Формируем подключение к Postgres через SQLAlchemy
2018-08-05 20:06:46,208 : INFO : 7261 записей загружены в Postgres
</pre>

Проверяем, что таблица существует и туда попали всё нужные данные
<pre>
psql --host $APP_POSTGRES_HOST -U postgres

psql (9.6.9, server 10.4)\

SELECT table_schema,table_name FROM information_schema.tables WHERE table_name='ui_interactions';

 table_schema |   table_name
--------------+-----------------
 public       | ui_interactions
(1 row)

SELECT COUNT(*) FROM public.ui_interactions;

 count
-------
  7261
(1 row)
</pre>

Готово! SQLAlchemy очень полезная штука в веб-приложениях, которая позволяет по классам Python генерировать таблицы в БД.

Можно выполнять запросы к таблицам с помощую полезной [функции query](http://docs.sqlalchemy.org/en/latest/orm/query.html)

query позволяет обращаться к таблице через свойства класса Python, с которым эта таблица ассоциирована.

<pre>
sqla_query = session.query(UITriplet).filter(UITriplet.rating>3.5).order_by(UITriplet.rating.desc()).limit(10)

print([i for i in sqla_query])
</pre>

SQLAlchemy обладает стандартными для SQL возможностями - напиример, можно делать группировки
<pre>
sqla_grouped_query = session.query(UITriplet.user, label('count', func.count(UITriplet.item))).group_by(UITriplet.user).limit(10)

logger.info("Пример группировки по полю user таблицы ratings {}".format([i for i in sqla_grouped_query]))
</pre>

Можно джойнить таблички с помощью соответствующей функции - join либо outerjoin. Например, отфильтруем контент из таблички Links, у которого нет оценок:

<pre>
join_query = session.query(Link.imdbid).outerjoin(UITriplet, UITriplet.item == Link.movieid).filter(UITriplet.item is None).limit(5)
logger.info("Результат LEFT JOIN: id контента, которому не ставили оценки {}".format([i[0] for i in join_query]))
</pre>

Мы познакомились с основным функционалом SQLAlchemy: выборки и фильтрация данных, джойны и группировки.