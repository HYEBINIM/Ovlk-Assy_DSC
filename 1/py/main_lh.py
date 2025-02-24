# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 지역 시간 모듈
import time

# 사운드 관련 모듈
import pygame

# 업데이트 실행 상태를 지정할 전역변수
running = True

# 데이터를 읽어올 plc DB
# main_db_config = {
#     "host": "192.168.200.2",
#     "port": 3306,
#     "user": "server",
#     "password": "dltmxm1234",
#     "database": "dataset"
# }

main_db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "autoset",
    "database": "dataset"
}

# 모니터별로 관리할 assy 테이블이 있는 DB
# assy_db_config = {
#     "host": "localhost",
#     "port": 3306,
#     "user": "server",
#     "password": "dltmxm1234",
#     "database": "dataset",
#     "charset": "utf8"
# }

assy_db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "autoset",
    "database": "dataset",
    "charset": "utf8"
}

# Pygame 초기화
pygame.mixer.init()

# 사운드 파일 정의
ok_sound = "../sound/DINGDONG.wav"
ng_sound = "../sound/NG.wav"

# 사운드 재생 메소드
def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

# 시작 시점에 running의 값을 정하는 메소드
def init_running():
    try:
        assy_db = mysql.connector.connect(**assy_db_config)
        assy_cursor = assy_db.cursor(dictionary = True)
    except Error as e:
        print(f"Error during initialize status")
    except Exception as e:
        print(f"Exception during initialize status")
    
    init_query = "SELECT data6 FROM assy_lh ORDER BY date DESC, time DESC LIMIT 1"
    assy_cursor.execute(init_query)
    init_record = assy_cursor.fetchone()
    init_value = init_record['data6']

    global running
    if(init_value == '1' or init_value == '2'):
        running = False
    else:
        running = True
    
    print(f"Running Status: {running}")

    return

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
    select_query_lh = "SELECT * FROM assy1read WHERE id = 1"

    main_cursor.execute(select_query_lh)
    record_lh = main_cursor.fetchone()

    # binding assy_lh record
    sub_query = "SELECT id, data1, data2, data3, data4, data5, data6 FROM assy_lh ORDER BY date DESC, time DESC LIMIT 1"
    assy_cursor.execute(sub_query)
    sub_record = assy_cursor.fetchone()

    if sub_record:
        max_id = sub_record['id']

        cur = time.localtime()
        cur_date = time.strftime("%Y-%m-%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        # column binding (dict)
        cols = {
            "data3": "data1",
            "data4": "data2",
            "data5": "data3",
            "data6": "data4",
            "data7": "data5",
            "data8": "data6"
        }

        # update data
        last_col = ""
        last_val = ""
        set_clause = []
        for key, value in record_lh.items():
            if "data" in key and key != "data0" and value is not None:
                col_name = cols.get(key, None)
                if col_name and sub_record[col_name] != value:
                    set_clause.append(f"{col_name} = {value}")
                    last_col = col_name
                    last_val = value
                    if col_name == "data6" and (value == '1' or value == '2'):
                        # PC완료 업데이트 토글
                        global running
                        running = False

                        last_col = col_name
                        last_val = value
        
        if len(set_clause) > 0:
            if last_col == "data3":
                get_torque_query = "SELECT data2 FROM input1 WHERE id = 1"
                main_cursor.execute(get_torque_query)
                torque_record = main_cursor.fetchone()
                torque = torque_record['data2']

                set_clause.append(f"data7 = {torque}")
            elif last_col == "data4":
                get_torque_query = "SELECT data2 FROM input1 WHERE id = 1"
                main_cursor.execute(get_torque_query)
                torque_record = main_cursor.fetchone()
                torque = torque_record['data2']

                set_clause.append(f"data8 = {torque}")
            
            update_query = f"UPDATE assy_lh SET date = '{cur_date}', time = '{cur_time}', {', '.join(set_clause)} WHERE id = {max_id}"

            print(update_query)

            assy_cursor.execute(update_query)
            assy_db.commit()

            if last_val == '1':
                play_sound(ok_sound)
            elif last_val == '2':
                play_sound(ng_sound)

            if not running:
                complete_query = "UPDATE assy1read SET data9 = 1, contents1 = 20 WHERE id = 2"

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

    query = "SELECT data1, data2, data3, data4, data5, data6 FROM assy_lh ORDER BY date DESC, time DESC LIMIT 1"
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

init_running()

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