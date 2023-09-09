import time
from HySQL import HySQL

start_time = time.time()

# query = open('./query/select.hql').read() # you can read SQL from file.
# query = "SELECT id AS ID, type AS TYPE FROM user LIMIT 10 ORDER BY id ASC WHERE id >= 2489677657 AND type != 'PushEvent' AND type = IssuesEvent OR type = DeleteEvent" # Or you can write the query in one line.
query = "SELECT * FROM city WHERE CountryCode != 'AFG' ORDER BY Population, ID DESC LIMIT 10"
sql = HySQL(query).excute()

sql = HySQL()
sql.SELECT('*')
sql.FROM('city')
sql.WHERE("CountryCode != 'AFG'")
sql.ORDER_BY("Population, ID DESC")
sql.LIMIT(10)
# result = sql.excute(view=False)

# Same as

query = "SELECT * FROM city WHERE CountryCode != 'AFG' \
ORDER BY Population, ID DESC LIMIT 10"
# result = HySQL(query).excute(view=False)

print(f'Excution time: {time.time() - start_time} s')
