# Mongo command line interface

Подключение к Mongo-серверу осуществляется с помощью утилиты Mongo

<pre>
/ # /usr/bin/mongo -host $APP_MONGO_HOST -port $APP_MONGO_PORT
MongoDB shell version v4.0.0
connecting to: mongodb://mongo_host:27017/
MongoDB server version: 4.0.0
Welcome to the MongoDB shell.
For interactive help, type "help".
---

>

</pre>

В консоли существует множество команд


stats - статистика MongoDB

<pre>
> db.stats()
{
	"db" : "test",
	"collections" : 0,
	"views" : 0,
	"objects" : 0,
	"avgObjSize" : 0,
	"dataSize" : 0,
	"storageSize" : 0,
	"numExtents" : 0,
	"indexes" : 0,
	"indexSize" : 0,
	"fileSize" : 0,
	"fsUsedSize" : 0,
	"fsTotalSize" : 0,
	"ok" : 1
}
</pre>

Создадим коллекцию документов

<pre>
> use test_db
switched to db test_db
</pre>

Добавим в коллекцию документов один документ

<pre>
> db.test_db.insert({name: 'Pepe', gender: 'm', weight: 40})
WriteResult({ "nInserted" : 1 })
</pre>

Снова посмотрим статистику по БД - мы увидим одну созданную коллеккцию:
<pre>
> db.stats()
{
	"db" : "test_db",
	"collections" : 1,
	"views" : 0,
	"objects" : 1,
	"avgObjSize" : 67,
	"dataSize" : 67,
	"storageSize" : 4096,
	"numExtents" : 0,
	"indexes" : 1,
	"indexSize" : 4096,
	"fsUsedSize" : 42377572352,
	"fsTotalSize" : 244529655808,
	"ok" : 1
}
</pre>

Как видно, у нас в БД появилась новая коллекция и один объект. В любой момент мы можем проверить, какие объекты хранятся в БД:

<pre>
> db.getCollectionNames()
[ "test_db" ]
</pre>

Для фильтрации записей используем find (аналог WHERE из SQL)

<pre>
> db.test_db.find({'name': 'Pepe'})
{ "_id" : ObjectId("5b56a66a64669cd544d5fd73"), "name" : "Pepe", "gender" : "m", "weight" : 40 }
</pre>

JSON, который передётся в функцию find называется "селектор". Селектор формирует набор документов из коллекции, которые отвечают уловиям, перечисленным в селектора.

Добавим новый документ в коллекцию с отличающимся набором полей:

<pre>
> db.test_db.insert({name: 'Lolo', gender: 'f', home: 'Moscow', student: false})
WriteResult({ "nInserted" : 1 })
</pre>

Воспользуемся командой find(), которая является аналогом для SELECT в стандарте SQL.
<pre>
> db.test_db.find()
{ "_id" : ObjectId("5b56a66a64669cd544d5fd73"), "name" : "Pepe", "gender" : "m", "weight" : 40 }
{ "_id" : ObjectId("5b56b32e64669cd544d5fd74"), "name" : "Lolo", "gender" : "f", "home" : "Moscow", "student" : false }
</pre>

Мы добавили в нашу коллекцию новый домумент с другим набором полей. Такое добавление было бы невозможно в реляционной БД, где набор полей фиксируется в момент создания таблицы.

Для удаления записей используется функция .remove(), в которую нужно передать селектор
<pre>
> db.test_db.remove({home: "Moscow"})
WriteResult({ "nRemoved" : 1 })
</pre>

Проверим, какие элементы остались в коллекции

<pre>
> db.test_db.find()
{ "_id" : ObjectId("5b56a66a64669cd544d5fd73"), "name" : "Pepe", "gender" : "m", "weight" : 40 }
</pre>

В селекторы можно передавать специальные операторы, которые эквивалентны условиям в WHERE запросов SQL:

<pre>
> db.test_db.find({gender: 'm', weight: {$gt: 700}})

</pre>

Тут ничего не нашли - это ожидаемо. Поправим условие в селекторе:

<pre>
> db.test_db.find({gender: 'm', weight: {$lt: 700}})
{ "_id" : ObjectId("5b56a66a64669cd544d5fd73"), "name" : "Pepe", "gender" : "m", "weight" : 40 }
</pre>

Так, например, оператор $exists проверяет наличие у объекта того или иного поля. Внутри селектора условия можно объединять с помощью оператора $or
<pre>
> db.test_db.find({$or: [{gender: 'm'}, {home: 'Moscow'}]})
{ "_id" : ObjectId("5b56a66a64669cd544d5fd73"), "name" : "Pepe", "gender" : "m", "weight" : 40 }
{ "_id" : ObjectId("5b56b78664669cd544d5fd75"), "name" : "Lolo", "gender" : "f", "home" : "Moscow", "student" : false }
</pre>

## Обновление записей

Обновление производится функцией update, попробуем её применить

<pre>
db.test_db.update({home: 'Moscow'},{student: true})
WriteResult({ "nMatched" : 1, "nUpserted" : 0, "nModified" : 1 })
</pre>

Проверим, что новый доумент появился в коллекции
<pre>
> db.test_db.find({home: 'Moscow'})

</pre>

Ничего не нашли, что случилось? Выведем все документы коллекции
<pre>
> db.test_db.find()
{ "_id" : ObjectId("5b56a66a64669cd544d5fd73"), "name" : "Pepe", "gender" : "m", "weight" : 40 }
{ "_id" : ObjectId("5b56b78664669cd544d5fd75"), "student" : true }
</pre>

Фунция update не просто изменила это поля, а переписала весь документ. Чтобы такого не произошло, нужно использовать модификатор $set

Вернём нашу запись на место
<pre>
> db.test_db.insert({name: 'Lolo', gender: 'f', home: 'Moscow', student: false})
WriteResult({ "nInserted" : 1 })
</pre>

Проведём правильный update
<pre>
> db.test_db.update({home: 'Moscow'}, {$set: {student: true}})
WriteResult({ "nMatched" : 1, "nUpserted" : 0, "nModified" : 1 })
</pre>


Проверим, что всё успешно
<pre>
> db.test_db.find()
{ "_id" : ObjectId("5b571bf081d67789509607f1"), "name" : "Lolo", "gender" : "f", "home" : "Moscow", "student" : true }
</pre>


Третий параметр в методе update позволяет создать запись, если она отсутствует - т.н. upsert (UPDATE + INSERT)


Попробуем выполнить update записи, которой нет
<pre>
> db.test_db.update({home: 'Perm'}, {$set: {student: false}})
WriteResult({ "nMatched" : 0, "nUpserted" : 0, "nModified" : 0 })
</pre>

Как изменилась коллекция? Никак =[
<pre>
> db.test_db.find()
{ "_id" : ObjectId("5b571bf081d67789509607f1"), "name" : "Lolo", "gender" : "f", "home" : "Moscow", "student" : true }
</pre>

Попробуем функционал UPSERT:
<pre>
> db.test_db.update({home: 'Perm'}, {$set: {student: false}}, true)
WriteResult({
	"nMatched" : 0,
	"nUpserted" : 1,
	"nModified" : 0,
	"_id" : ObjectId("5b57207bbff183a0a45dcfb3")
})
</pre>

Проверим, как изменилась коллекция
<pre>
> db.test_db.find()
{ "_id" : ObjectId("5b571bf081d67789509607f1"), "name" : "Lolo", "gender" : "f", "home" : "Moscow", "student" : true }
{ "_id" : ObjectId("5b57207bbff183a0a45dcfb3"), "home" : "Perm", "student" : false }
</pre>

По умоллчанию будет обновлён один из документов, попадающих под условия селектора. Чётвёртый параметр команды позволяет осуществлять массовую вставку (обновление) документов.

Есть другие модификаторы, например $inc (увеличивает скаляр) или $push (добавляет в массив) - о них можно почитать в документации по [Mongo](https://docs.mongodb.com/manual/reference/operator/update/)
