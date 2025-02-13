# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 지역 시간 모듈
import time

# 업데이트 실행 상태를 지정할 전역변수
running = True

# 데이터를 읽어올 plc DB
main_db_config = {
    "host": "192.168.200.2",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset",
    "charset": "utf8"
}

# 모니터별로 관리할 assy 테이블이 있는 DB
assy_db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset",
    "charset": "utf8"
}

# kiosk DB 서버에서 plc 데이터 읽어오는 메소드
def read_plc_data():
    try:
        main_db = mysql.connector.connect(**main_db_config)
        main_cursor = main_db.cursor(dictionary = True)

        if main_db.is_connected():
            print("Main DB Connected...")
        
        assy_db = mysql.connector.connect(**assy_db_config)
        assy_cursor = assy_db.cursor(dictionary = True)

        if assy_db.is_connected():
            print("Assy DB Connected...")
    except Error as e:
        print(f"Error during DB connection: {e}")
        return
    except Exception as e:
        print(f"Exception during DB connection: {e}")
        return
    
    # read data (lh)
    select_query_lh = "SELECT * FROM assy3read WHERE id = 1"

    main_cursor.execute(select_query_lh)
    record_lh = main_cursor.fetchone()

    # binding assy_lh record
    sub_query = "SELECT id FROM assy_lh ORDER BY date DESC, time DESC LIMIT 1"
    assy_cursor.execute(sub_query)
    sub_record = assy_cursor.fetchone()

    if sub_record:
        max_id = sub_record['id']

        cur = time.localtime()
        cur_date = time.strftime("%Y-%m-%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        # column binding (dict)
        cols = {
            "DATA2": "DATA1",
            "DATA3": "DATA2",
            "DATA4": "DATA3",
            "DATA5": "DATA4",
            "DATA6": "DATA5",
            "DATA9": "DATA6"
        }

        # update data
        set_clause = []
        for key, value in record_lh.items():
            if "DATA" in key and key != "DATA0" and value is not None:
                col_name = cols.get(key, None)
                if col_name:
                    set_clause.append(f"{col_name} = {value}")
                    if col_name == "DATA6" and (value == '1' or value == '2'):
                        # PC완료 업데이트 토글
                        global running
                        running = False
        
        if len(set_clause) > 0:
            update_query = f"UPDATE assy_lh SET date = '{cur_date}', time = '{cur_time}', {', '.join(set_clause)} WHERE id = {max_id}"

            print(update_query)

            assy_cursor.execute(update_query)
            assy_db.commit()

            if not running:
                complete_query = "UPDATE assy3read SET data0 = 1, contents1 = 11 WHERE id = 4"

                print(complete_query)

                main_cursor.execute(complete_query)
                main_db.commit()
    
        main_cursor.close()
        main_db.close()
        print("Main DB Disconnected...")

        assy_cursor.close()
        assy_db.close()
        print("Assy DB Disconnected...")

# 업데이트가 중지된 동안 새로운 scan값이 들어오는지 관찰하는 메소드
def check_new_data():
    # 가장 최근 데이터의 DATA1 - DATA6의 값이 None 타입일 때 새로운 scan값이 들어온 것으로 간주
    db = mysql.connector.connect(**assy_db_config)
    cursor = db.cursor(dictionary = True)

    if db.is_connected():
        print("Assy DB Connected... (For checking new INSERT)")

    query = "SELECT DATA1, DATA2, DATA3, DATA4, DATA5, DATA6 FROM assy_lh ORDER BY date DESC, time DESC LIMIT 1"
    cursor.execute(query)
    record = cursor.fetchone()

    null_check = True
    for key, value in record.items():
        if value is not None:
            null_check = False
    
    global running
    running = null_check

    cursor.close()
    db.close()
    print("Assy DB Disconnected... (For checking new INSERT)")

polling_interval = 1

while True:
    if running:
        time.sleep(polling_interval)
        read_plc_data()
        print(f"Running: {running}")
    else:
        time.sleep(polling_interval)
        check_new_data()
        print(f"Running: {running}")