FROM test1, test2, test3
SELECT name AS 'Name' ,age AS 'Age'
WHERE name LIKE ^H|^J
ORDER BY name DESC
