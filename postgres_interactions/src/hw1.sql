SELECT ('ФИО: Капитан Америка');
-- первый запрос
SELECT * FROM ratings LIMIT 10;

-- второй запрос
SELECT userId, COUNT(*) FROM ratings GROUP BY 1 ORDER BY 2 DESC LIMIT 10;