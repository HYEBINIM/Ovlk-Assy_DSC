# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 모니터별로 관리할 assy 테이블이 있는 DB
assy_db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset",
    "charset": "utf8"
}

db = mysql.connector.connect(**assy_db_config)
cursor = db.cursor(dictionary = True)

query = "SELECT data0 FROM assy_lh ORDER BY id DESC LIMIT 1"
cursor.execute(query)
record = cursor.fetchone()

data = record['data0']
data_split = data.split(chr(29))

for line in data_split:
    print(line)