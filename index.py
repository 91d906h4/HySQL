import time
from HySQL import HySQL

start_time = time.time()

# input = open('./query/insert.hql').read() # you can read SQL from file.
input = "SELECT id AS ID, type AS TYPE FROM user TOP 10 ORDER BY id ASC WHERE id >= 2489677657 AND type != 'PushEvent' AND type = IssuesEvent OR type = DeleteEvent" # Or you can write the query in one line.
query = HySQL(input).excute()

print(f'Excution time: {time.time() - start_time} s')