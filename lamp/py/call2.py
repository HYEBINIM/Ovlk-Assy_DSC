# DB 관련 모듈 (ver 8.4.0)
import mysql.connector
from mysql.connector import Error

# 지역 시간 모듈
import time

# 데이터를 읽어올 local DB
local_db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset"
}

# 호출 신호를 보낼 kiosk DB
kiosk_db_config = {
    "host": "192.168.150.5",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset"
}

# local DB에서 호출 신호를 읽어와 kiosk DB로 보내는 메소드
def read_call_data():
    try:
        current_time = time.localtime()
        formatted_date_time = time.strftime("%Y.%m.%d %H:%M:%S", current_time)

        local_db = mysql.connector.connect(**local_db_config)
        local_cursor = local_db.cursor(dictionary = True)

        if local_db.is_connected():
            print(f"[{formatted_date_time}] Local DB Connected...")
        
        kiosk_db = mysql.connector.connect(**kiosk_db_config)
        kiosk_cursor = kiosk_db.cursor(dictionary = True)

        if kiosk_db.is_connected():
            print(f"[{formatted_date_time}] Kiosk DB Connected...")
    except Error as e:
        print(f"[{formatted_date_time}] Error during DB Connection: {e}")
        return
    except Exception as e:
        print(f"[{formatted_date_time}] Exception during DB Connection: {e}")
        return
    
    # read data (plc)
    select_query = "SELECT data0 FROM guide1 WHERE id = 13"

    local_cursor.execute(select_query)
    local_record = local_cursor.fetchone()

    if local_record:
        update_query = ""
        if local_record['data0'] == "1":
            update_query = "UPDATE call1 SET data1 = 1 WHERE id = 1"
        else:
            update_query = "UPDATE call1 SET data1 = 0 WHERE id = 1"
        
        if update_query:
            kiosk_cursor.execute(update_query)
            kiosk_db.commit()
    
    current_time = time.localtime()
    formatted_date_time = time.strftime("%Y.%m.%d %H:%M:%S", current_time)

    local_cursor.close()
    local_db.close()
    print(f"[{formatted_date_time}] Local DB Disconnected...")

    kiosk_cursor.close()
    kiosk_db.close()
    print(f"[{formatted_date_time}] Kiosk DB Disconnected...")

polling_interval = 1

while True:
    read_call_data()
    time.sleep(polling_interval)