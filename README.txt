試著做了一個結構化查詢語言（SQL）

繼上次做的超微型語言（就姑且稱 ＭｙＬａｎｇ（仮）），這次以同樣概念做了一個 SQL。

一、簡介

名稱：HySQL
概說：HySQL 是 NoSQL 和 SQL 的合體，提供 SQL like 查詢方法和 NoSQL 的處存方法（JSON）。
查詢速度：慢

二、架構

所有資料處存於 ./database 目錄下的 *.table 檔。檔名就是 table 的名稱（FROM <檔名>）。

三、語法

HySQL 的語法和 MySQL 大致相同，只要會用 MySQL 基本上就會用 HySQL。只不過 HySQL 的功能少了一些。
那就讓我們來看看 HySQL 的語法吧～

1. 查詢

SELECT <col1, col2, ...>
FROM <table_name>

可以搭配其他功能使用：

SELECT <col1, col2, ...>
FROM <table_name>
WHERE <cond1, cond2, ...>

SELECT <col1, col2, ...>
FROM <table_name>
WHERE <cond1, cond2, ...>
ORDER BY <col1>

SELECT <col1, col2, ...>
FROM <table_name>
WHERE <cond1, cond2, ...>
ORDER BY <col1>
TOP <number>

Query 可以寫成一行沒問題：
1.png

也可以用 LIKE 來 match regex：
3.png

2. 更新

UPDATE <table>
SET <col1 = val1, col2 = val2, ...>
WHERE <cond1, cond2, ...>

2.png

3. 新增

INSERT INTO <table> (<col1, col2, ...>)
VALUE (<val1, val2, ...>)

4.png

4. 刪除

DELETE <col1, col2, ...>
FROM <table>
WHERE <cond1, cond2, ...>

5.png

5. 建立資料表

CREATE <table> (
    <col1> <val1>,
    <col2> <val2>,
    ...
)

6.png

6. 刪除資料表

DROP TABLE <table1, table2, ...>

7.png

四、使用 HySQL

載入 HySQL 模組，先將其實例化後再執行 .excute() function。

8.png

https://raw.githubusercontent.com/json-iterator/test-data/master/large-file.json