# Домашнее задание

## Зайти на Кинопоиск, найти 5 любимых фильмов и сделать по ним табличку с данными.

Табличка filmes:
- title - название (текст)
- id (число) соответствует film_id в табличке persons2content
- country страна (тест)
- box_office сборы в долларах (число)
- release_year год выпуска (timestamp)

Табличка persons
- id (число) - соответствует person_id в табличке persons2content
- fio (текст) фамилия, имя

Табличка persons2content
- person_id (число) - id персоны
- film_id (число) - id контента
- person_type (текст) тип персоны (актёр, режиссёр и т.д.)

Тим образом реализуется схема БД "Звезда" с центром в табличке persons2content

# Создать таблички

Написать SQL для создания табличек со слайдов 15, 17

Решением будут SQL-запросы в формате .sql

Примеры (тут):https://github.com/Dju999/flask_docker_app/blob/master/slides/sql_postgresql_cli.md
