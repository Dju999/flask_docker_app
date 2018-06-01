# Установка Ubuntu 18.04 в Google Cloud

Как установить - по инструкции отсюда: https://cloud.google.com/compute/docs/quickstart-linux

Внимание! В инструкции установка Debian, а нам нужна Ubuntu 18.04. Эта опция выбирается в меню Boot Disk

![выбор ОС](https://habrastorage.org/webt/vl/dt/3m/vldt3mgct8jq3n6n9oa3pmyug_a.png "boot disk")

После установики ваш инстанс можно будет найти на этой странице https://console.cloud.google.com/compute/instances

![страница с инстансами](https://habrastorage.org/webt/cb/fx/qz/cbfxqzxqcdo0atxs9eg_c-t3jby.png "Google cloud instances")

# Подготовка инстанса к работе

Подготовку нужно выполнить всего один раз.

Далее нужно перейти в инстанс и открыть консоль (прямо в браузере) - то есть выбрать пункт "Open in browser window".

![запуск консоли](https://habrastorage.org/webt/sl/up/h1/sluph1qjdyzjdct31mmsfr0lwbo.png "Instance console")

Когда команда выпонится, вы увидите консоль Вашей удалённой машины с Ubuntu 18 на борту

![ubuntu console](https://habrastorage.org/webt/n5/s1/ll/n5s1llvkezhubqqsv3ulmk_8du0.png "Консоль Ubuntu")

Выполнить в консоли команду:

<pre>
sudo apt-get update && sudo apt-get -y upgrade
</pre>

Эта команда обновит пакетный менеджер apt-get. После этотго установить пакет pip:

<pre>
sudo apt install python-pip; sudo apt-get install unzip
</pre>

pip - это менеджер пакетов python, его помощью можно будет устанавливать python библиотеки. unzip - программа для распаковки архивов.

С помощью pip установим библиотеку requests:
<pre>
pip install requests;
pip install tqdm;
</pre>

Теперь zip-архив с данными, который я заранее залил на Google Drive нужно перенести в виртуалку Google Cloud. Для этого  склонируем полезный репозиторий

<pre>
git clone https://github.com/chentinghao/download_google_drive.git
</pre>

Запускаем скачивание файла - zip архива с данными.
<pre>
python download_google_drive/download_gdrive.py 1D3CcWOSw-MUx6YvJ_4dqOLHZAh-6uTxK data.zip
</pre>

Установим docker и docker-compose

<pre>
sudo apt-get install docker docker-compose
</pre>

Теперь скачиваем репозиторий курса Нетологии

<pre>
dju0204@instance-ubuntu:~$ git clone https://github.com/Dju999/flask_docker_app.git
Cloning into 'flask_docker_app'...
remote: Counting objects: 81, done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 81 (delta 0), reused 0 (delta 0), pack-reused 77
Unpacking objects: 100% (81/81), done.
dju0204@instance-ubuntu:~$ cd flask_docker_app/postgres_interactions
</pre>

Подготовка завершена! Один раз проделав этот пункт, можно к нему больше не возвращаться

# Работа в инстансе

Сначала распаковываем архив с данными.

Примечание: т.к. мы распаковываем в директорию /tmp, то файлы будут удаляться при каждом рестарте инстанса. Нужно будет повторно распаковывать архив с помощью этой команды после каждого рестарта.

<pre>
rm -rf /tmp/data; unzip data.zip -d  /tmp/data
</pre>

Мы увидим процесс извлечения данных

<pre>
Archive:  data.zip
  inflating: /tmp/data/ratings.csv   
  inflating: /tmp/data/ratings_small.csv  
  inflating: /tmp/data/links.csv     
  inflating: /tmp/data/links_small.csv  
  inflating: /tmp/data/keywords.csv  
  inflating: /tmp/data/movies_metadata.csv  
  inflating: /tmp/data/credits.csv  
</pre>

Переходим в директорию занятия
<pre>
cd flask_docker_app/postgres_interactions
</pre>

Запускаем построение контейнера. Внимание! Построение контейнера запускаем только один раз, при самом первом запуске инстанса.

<pre>
sudo docker-compose --project-name postgres-client -f docker-compose.yml up --build -d
</pre>

В консоли побежит информация о сборке контейнера. Для теста запустим контейнер и подключимся к командной строке Alpine-Linux:
<pre>
sudo docker-compose --project-name postgres-client -f docker-compose.yml run --rm postgres-client
Starting postgresclient_postgres_host_1 ... done
/ # echo "Hello, Netology!"
Hello, Netology!
</pre>

Проверим, что директория с данными Kaggle подключилась:
<pre>
/ # ls /data
credits.csv          links.csv            movies_metadata.csv  ratings_small.csv
keywords.csv         links_small.csv      ratings.csv
</pre>

Как видно csv-файлы присутствуют, контейнер запущен! можно начинать работу.

Подключение к Postgres
<pre>
psql --host $APP_POSTGRES_HOST -U postgres
</pre>
