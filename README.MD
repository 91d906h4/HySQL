# HySQL

## Syntax

### 1. SELECT

The `SELECT` statement is used to select data from a database.

The data will be returned in json.

```sql
FROM <table_name> SELECT <col1, col2, ...>
```

You can also change the order. For example :

```sql
SELECT fun, profit FROM real_world
```

Using `WHERE` to filter to result.

```sql
FROM <table_name> SELECT <col1, col2, ...>
WHERE <cond1, cond2, ...>
```

### 2. UPDATE

The `UPDATE` statement is used to modify the existing records in a table.

```sql
UPDATE <table_name>
SET <col1 = val1, col2 = val2, ...>
WHERE <cond1, cond2, ...>
```

For example :

```sql
UPDATE employee
SET salary = 200000
WHERE name = 'ME'
```

### 3. INSERT

The `INSERT INTO` statement is used to insert new records in a table.
You will need to specify both the column names and the values to be inserted:

```sql
INSERT INTO <table_name> (col1, col2, ...)
VALUE (val1, val2, ...)
```

The numbers of column must be same as the numbers of value. For example :

```sql
INSERT INTO className (id, name)
VALUE (30, 'Joe')
```

### 4. DELETE

The `DELETE` statement is used to delete existing records in a table.

There is a difference between HySQL and MySQL, in HySQL, you can specify the columns you want to delete.

```sql
DELETE <col1, col2, ...>
FROM <table_name>
WHERE <cond1, cond2, ...>
```

For example :

```sql
DELETE id
FROM class
WHERE name = 'Joe'
```

### 5. CREATE

The `CREATE` statement is used to create a new HySQL table.

```sql
CREATE <table_name> (
    <col1> <val1>,
    <col2> <val2>,
    ...
)
```

The columns and values will be the col and val of the first data. For example :

```sql
CREATE TABLE tree (
    Name 'Pinus resinosa',
    Kingdom 'Plantae',
    Clade 'Tracheophytes'
)
```

The database generated :

```json
[
    {
        "Name": "Pinus resinosa,
        "Kingdom": "Plantae",
        "Clade": "Tracheophytes"
    }
]
```

### 6. DROP

The \`DROP\` statement is used to drop an existing HySQL table.

HySQL can drop multiple tables in one time.

```sql
DROP TABLE <table_name1, table_name2, ...>
```

For example :

```sql
DROP TABLE tree, class, employee
```
