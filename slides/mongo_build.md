# Mongodb

MongoDB - это нереляционное хранилище данных, schema-less.

Мы установим Mongo внутрь контейнера на ALpine Linux

## Шаг 1 - сборка образа.

Нам нужен образ с дистрибутивом Alpine Linux и Mongo - необходимая конфигурация содержится в файле docker-compose.yml.

<pre>
sudo docker-compose --project-name mongo-client -f docker-compose.yml up --build -d

Starting mongoclient_mongodb_1 ...
Starting mongoclient_mongodb_1 ... done
Starting mongoclient_alpine-mongo-client_1 ...
Starting mongoclient_alpine-mongo-client_1 ... done
</pre>

Если проблемы с сетью

Может возникнуть непонятная сетевая ошибка
<pre>
Creating network "postgresclient_default" with the default driver
ERROR: could not find an available, non-overlapping IPv4 address pool among the defaults to assign to the network
</pre>

попробуйте
<pre>
ifconfig

выбрать подозриттельный сетевой интерфейс tun0 и удалить его

sudo ip link delete tun0
</pre>

Если не поднимается - нужно проверить, возможно остались следы от старых образов:

<pre>
$ sudo docker-compose --project-name mongo-client -f docker-compose.yml ps
                                  Name                                               Command              State       Ports
-----------------------------------------------------------------------------------------------------------------------------
a93c0a29e67e_a93c0a29e67e_a93c0a29e67e_mongoclient_alpine-mongo-client_1   /bin/sh                       Exit 137
mongoclient_mongodb_1                                                      docker-entrypoint.sh mongod   Up         27017/tcp

$  sudo docker-compose --project-name mongo-client -f docker-compose.yml rm --all;

</pre>

Или перезапустить compose
<pre>
    docker-compose -f docker-compose.yml down

    docker-compose -f docker-composeyml up
</pre>


Проверим, что поднялся контейнер и все сетевые интерфейсы
<pre>
$ sudo docker-compose --project-name mongo-client -f docker-compose.yml ps
              Name                            Command             State     Ports
-----------------------------------------------------------------------------------
mongoclient_alpine-mongo-client_1   /bin/sh                       Up
mongoclient_mongodb_1               docker-entrypoint.sh mongod   Up      27017/tcp
</pre>

Если build выполнился и сетевые интерфейсы подняты - пробуем подключиться к собранному контейнер
<pre>
$ sudo docker-compose --project-name mongo-client -f docker-compose.yml run --rm alpine-client
</pre>

Попробуем подключиться к Mongo
<pre>
    # /usr/bin/mongo -host $APP_MONGO_HOST -port $APP_MONGO_PORT
</pre>

ЕСли что-то пошло не так, можно посмотреть в логи
<pre>
adzhumurat@adzhumurat-HP-G5:~$ sudo docker ps
CONTAINER ID        IMAGE                             COMMAND                  CREATED             STATUS              PORTS               NAMES
4fb59e3c1685        mongoclient_alpine-mongo-client   "/bin/sh"                4 minutes ago       Up 4 minutes                            sleepy_heyrovsky
699ad0a36bfc        mongoclient_alpine-mongo-client   "/bin/sh"                8 minutes ago       Up 4 minutes                            mongoclient_alpine-mongo-client_1
fb743b409812        mongo:latest                      "docker-entrypoint.s…"   20 minutes ago      Up 4 minutes        27017/tcp           mongoclient_mongodb_1
1cb26b58e8c8        postgres                          "docker-entrypoint.s…"   3 days ago          Up 3 days           5432/tcp            netology-postgres
adzhumurat@adzhumurat-HP-G5:~$ sudo docker logs fb743b409812 | tail
2018-07-23T08:30:09.608+0000 I FTDC     [initandlisten] Initializing full-time diagnostic data capture with directory '/data/db/diagnostic.data'
2018-07-23T08:30:09.609+0000 I NETWORK  [initandlisten] waiting for connections on port 27017
adzhumurat@adzhumurat-HP-G5:~$
</pre>

Рекомендую так же поудалять все контейнеры, которые завершились

<pre>
    sudo docker ps -a | grep Exit | cut -d ' ' -f 1 | xargs sudo docker rm
</pre>


Если всё прошло удачно - нужно проверить, что внутри контейнера доступны данные с родительской машины
<pre>
/ # ls /data
credits.csv          keywords.csv         keywords1.csv        links.csv            links_small.csv      movies_metadata.csv  ratings.csv          ratings_small.csv    test.csv             test.json
</pre>