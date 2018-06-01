# Сборка докера с Anaconda

Для демонстрации взаимодействия между Python и зазличными базами данных мы будем использовать докер-контйенер с дистрибутивом Anaconda.

Мы развернём образ continuumio [miniconda](https://hub.docker.com/r/continuumio/miniconda3/) - дистрибутив основан на Debian/

Установим с помомощью Anaconda в контейнер базовые пакеты Python для обработки данных (sklearn, numpy, pandas) и библиотеки на работы с БД (sqlalchemy, psycorg2, pymongo)

<pre>
sudo docker-compose --project-name py-db -f docker-compose.yml up --build -d
</pre>

Сборка контейнера проходит относительно долго, т.к. приходится устанавливаться большое количество библиотек

После сборки контейнер нужно развернуть
<pre>
sudo docker-compose --project-name py-db -f docker-compose.yml run --rm python-db
</pre>

Когда запустится консоль, выполним команду для загрузки данных из CSV-файлов в базу данных Postgres
<pre>
bash /home/load_data.sh
</pre>

Проверим, что данные загрузились в таблицу ratings успешно:

<pre>
psql -h $APP_POSTGRES_HOST -U postgres -c 'SELECT COUNT(*) FROM ratings;'
 count
--------
 100004
(1 row)
</pre>

Данные загружены, можно работать с ними из Python.