## Простые выборки  из БД

Для работы нужно развернуть докер-образ с postgresql и данными

Ссылка на данные: https://drive.google.com/file/d/1YiclJxLxWZcHX8ObNiQaS0ZOVyyD7TX4/view?usp=sharing

Данные нужно скопировать к себе на GoogleDrive и скачать

Или скачать прямо из соревнования: https://www.kaggle.com/rounakbanik/the-movies-dataset

Можно воспользоваться инструкциями отсюда: https://github.com/Dju999/flask_docker_app/edit/master/slides/google_cloud_instance.md , пункт "Подготовка инстанса к работе"

# Сборка docker контейнера (выполняется один раз!)

Переходим в директорию *postgres_interactions* и запускаем процесс сборки контейнера

Внимание! Сборку запускаем только один раз, потом бы будем использовать готовый контейнер

<pre>
sudo docker-compose --project-name postgres-client -f docker-compose.yml up --build -d
</pre>

Если возникнет непонятная ошибка про сеть
<pre>
sudo docker-compose --project-name postgres-client -f docker-compose.yml up --build -d
Creating network "postgresclient_default" with the default driver
ERROR: could not find an available, non-overlapping IPv4 address pool among the defaults to assign to the network
</pre>

Нужно выполнить
<pre>
ifconfig

Потом найти непонятный интерфейс tun0 

tun0: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1500
        inet 10.12.181.121  netmask 255.255.255.255  destination 10.12.181.122
        inet6 fe80::d72d:a59d:abbb:6781  prefixlen 64  scopeid 0x20<link>
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 100  (UNSPEC)
        RX packets 22093  bytes 20743248 (20.7 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 24501  bytes 4015886 (4.0 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 


и удалить его

sudo ip link delete tun0
</pre>

После этого перезапустить команду - всё должно заработать.

На этом сборка контейнера завершена, можно приступать к эксплуатации

# Запуск docker контейнера 

Когда контейнер собран, нужно получить доступ к командной строке Alpine Linux.

Внимание! Данные с kaggle в директорию /tmp/data

<pre>
sudo docker-compose --project-name postgres-client -f docker-compose.yml run --rm postgres-client
Starting postgresclient_postgres_host_1 ... done
/ # 
</pre>

Ура, стартовала командная строка - это достутуп в операционную систему внутри контейнера

Подключаемся к БД и создаём табличку
<pre>
psql --host $APP_POSTGRES_HOST -U postgres -c 'CREATE TABLE IF NOT EXISTS temp (movieId bigint, imdbId varchar(20), tmdbId varchar(20));'
</pre>

Теперь посмотри на созданную табличку
<pre>
psql --host $APP_POSTGRES_HOST -U postgres
psql (10.4)
Type "help" for help.

postgres=# SELECT table_schema,table_name FROM information_schema.tables WHERE table_name='temp' LIMIT 10;

 table_schema | table_name 
--------------+------------
 public       | temp
(1 row)

</pre>

SELECT - тип запроса, выборка данных
FROM - таблица, откуда достаём данные. Имя таблицы содержит схему
WHERE - различные условия
LIMIT - сколько записей ожидаем в выдаче

Можно делать нечёткий поиск с помощью оператора LIKE

<pre>
postgres=# SELECT table_schema,table_name FROM information_schema.tables WHERE table_name like '%temp%' LIMIT 10;
 table_schema |   table_name   
--------------+----------------
 public       | temp
 pg_catalog   | pg_pltemplate
 pg_catalog   | pg_ts_template
(3 rows)

</pre>
