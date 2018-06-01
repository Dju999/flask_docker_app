# Командная строка PostgreSQL

## Старт интерпретатора

<code>
sudo docker run --name netology-postgres -e POSTGRES_PASSWORD=netology_pass -d postgres
</code>

Если не стартует с ошибкой
<pre>
docker: Error response from daemon: Conflict. The container name "/netology-postgres" is already in use by container "2a99cb6629b78e7b5b6747a9bd453263940127909d91c8517e9ee0b230e60768". You have to remove (or rename) that container to be able to reuse that name.
</pre>

То контейнер уже создан и можно стартовать его
<pre>
sudo docker start 2a99cb6629b78e7b5b6747a9bd453263940127909d91c8517e9ee0b230e60768
</pre>

Если не помогло - надо бы остановить все запущенные докер-образы и удалить их

<pre>
sudo docker stop $(sudo docker ps -a -q)
sudo docker rm $(sudo docker ps -a -q)
</pre>

Параметры docker run, остальные параметры [тут](https://docs.docker.com/v1.11/engine/reference/commandline/run/)

<code>
--name - Assign a name to the container
  
-d, --detach - Run container in background and print container ID

-e - устанавливаем переменную среды
</code>

Получаем доступ к Postgres CLI внутри контейнера

<pre>
sudo docker run -it --rm --link netology-postgres:postgres postgres psql -h postgres -U postgres

ЛИБО

sudo docker exec -it netology-postgres psql -U postgres
</pre>

Разбор опций

<pre>
-it - запустить интеракцивный терминал 
</pre>

Ожидаемый результат: запуск интерпретатора

<pre>
alex@alex-All-Series:~$ sudo docker run -it --rm --link netology-postgres:postgres postgres psql -h postgres -U postgres
Password for user postgres: 
psql (10.4 (Debian 10.4-2.pgdg90+1))
Type "help" for help.

postgres=# 
</pre>

Проверим, что в БД есть какие-то таблицы

<code>
SELECT table_schema,table_name FROM information_schema.tables LIMIT 10;
</code>


## Создание пользователя и схемы данных

Попробуем создать пользователя БД и схему данных

<pre>
postgres=# CREATE USER ololouser WITH PASSWORD 'ololopass';
postgres'# CREATE DATABASE ololodb;
postgres=# GRANT ALL PRIVILEGES ON DATABASE ololodb TO ololouser;
</pre>

# Создание таблиц

Для создания таблицы в Postgres нужно указать типы данных для полей, а также задать ключии таблицы.

Общий шаблон создания таблиц

<pre>
CREATE TABLE table_name (
 column_name TYPE column_constraint,
 table_constraint table_constraint
)
</pre>

Конкретный пример

<pre>
CREATE TABLE account(user_id serial PRIMARY KEY, email VARCHAR (355) UNIQUE NOT NULL, last_login TIMESTAMP);
</pre>

Заполняем табличку данными

<pre>
postgres=# INSERT INTO account VALUES (123, 'ololo@ya.ru', '2003-2-1'::timestamp);
postgres=# SELECT * FROM account;
 user_id |    email    |     last_login      
---------+-------------+---------------------
     123 | ololo@ya.ru | 2003-02-01 00:00:00
(1 row)

postgres=# 
</pre>

Вопрос: почему ошибка?
<pre>
postgres=# INSERT INTO account VALUES (1235, 'ololo@ya.ru', '2023-2-1'::timestamp), (1234, 'ololo123@ya.ru', '2013-2-1'::timestamp);
ERROR:  duplicate key value violates unique constraint "account_email_key"
DETAIL:  Key (email)=(ololo@ya.ru) already exists.
</pre>

Как добавить новую колонку
<pre>
ALTER TABLE account ADD COLUMN phone VARCHAR;
</pre>

Заполнить колонку рандомными значениями
<pre>
UPDATE account SET phone=md5(random()::text);

postgres=# SELECT * FROM account;
 user_id |     email      |     last_login      |              phone               
---------+----------------+---------------------+----------------------------------
     123 | ololo@ya.ru    | 2003-02-01 00:00:00 | 48a38b8b836d5ee6bc01d801c3712e9d
    1235 | ololoww@ya.ru  | 2023-02-01 00:00:00 | 74c41824f87047170e4bd7ea701d09b0
    1234 | ololo123@ya.ru | 2013-02-01 00:00:00 | f2a50425a94d4d6add1036b9b4ba4c67
(3 rows)

</pre>
