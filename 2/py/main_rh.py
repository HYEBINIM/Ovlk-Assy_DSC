# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 지역 시간 모듈
import time

# 사운드 관련 모듈
import pygame

# 파일 시스템 관련 모듈
import os

# 에러 발생 traceback 모듈
import traceback

# 업데이트 실행 상태를 지정할 전역변수
running = True

# 데이터를 읽어올 plc DB
main_db_config = {
    "host": "192.168.200.2",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset"
}

# 모니터별로 관리할 assy 테이블이 있는 DB
assy_db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset"
}

# Pygame 초기화
pygame.mixer.init()

# 사운드 파일 정의
ok_sound_file = "../sound/DINGDONG.wav"
ng_sound_file = "../sound/NG.wav"

# 사운드 파일 로드
ok_sound = pygame.mixer.Sound(ok_sound_file)
ng_sound = pygame.mixer.Sound(ng_sound_file)

# 에러 로깅 메소드
def log_message(message, log_file = "/AutoSet6/public_html/log/main.log"):
    log_dir = os.path.dirname(log_file)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok = True)
    
    with open(log_file, "a") as f:
        f.write(message)

# 시작 시점에 running의 값을 정하는 메소드
def init_running():
    try:
        assy_db = mysql.connector.connect(**assy_db_config)
        assy_cursor = assy_db.cursor(dictionary = True)
    except Error as e:
        cur = time.localtime()
        cur_date = time.strftime("%Y.%m.%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        error_msg = f"[RH][{cur_date} {cur_time}]Error during initialize status: {e}\n"
        log_message(error_msg)
        print(error_msg)
    except Exception as e:
        cur = time.localtime()
        cur_date = time.strftime("%Y.%m.%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        error_msg = f"[RH][{cur_date} {cur_time}]Exception during initialize status: {e}\n"
        log_message(error_msg)
        print(error_msg)
    
    init_query = "SELECT data5 FROM assy_rh ORDER BY id DESC LIMIT 1"
    assy_cursor.execute(init_query)
    init_record = assy_cursor.fetchone()
    if init_record:
        init_value = init_record['data5']
    else:
        init_value = "1"

    global running
    if init_value == "1" or init_value == "2":
        running = False
    else:
        running = True
    
    print(f"Running: {running}")

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
        cur = time.localtime()
        cur_date = time.strftime("%Y.%m.%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        error_msg = f"[RH][{cur_date} {cur_time}]Error during DB connection: {e}\n"
        log_message(error_msg)
        print(error_msg)

        return
    except Exception as e:
        cur = time.localtime()
        cur_date = time.strftime("%Y.%m.%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        error_msg = f"[RH][{cur_date} {cur_time}]Exception during DB connection: {e}\n"
        log_message(error_msg)
        print(error_msg)

        return
    
    # read data (rh)
    select_query_rh = "SELECT * FROM assy2read WHERE id = 5"

    main_cursor.execute(select_query_rh)
    record_rh = main_cursor.fetchone()

    # binding assy_rh record
    sub_query = "SELECT id, data1, data2, data3, data4, data5 FROM assy_rh ORDER BY date DESC, time DESC LIMIT 1"
    assy_cursor.execute(sub_query)
    sub_record = assy_cursor.fetchone()

    if sub_record:
        max_id = sub_record['id']

        cur = time.localtime()
        cur_date = time.strftime("%Y-%m-%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        # column binding (dict)
        cols = {
            "data2": "data1",
            "data5": "data4",
            "data6": "data5"
        }

        # update data
        last_val = ""
        set_clause = []
        for key, value in record_rh.items():
            if "data" in key and key != "data0" and value is not None:
                col_name = cols.get(key, None)
                if col_name and sub_record[col_name] != value:
                    set_clause.append(f"{col_name} = {value}")
                    last_val = value
                    if col_name == "data5" and (value == '1' or value == '2'):
                        # PC완료 업데이트 토글
                        global running
                        running = False
        
        if len(set_clause) > 0:
            update_query = f"UPDATE assy_rh SET date = '{cur_date}', time = '{cur_time}', {', '.join(set_clause)} WHERE id = {max_id}"

            print(update_query)

            assy_cursor.execute(update_query)
            assy_db.commit()

            if last_val == '1':
                ok_sound.play()
            elif last_val == '2':
                ng_sound.play()           

            if not running:
                cur = time.localtime()
                cur_date = time.strftime("%Y.%m.%d", cur)
                cur_time = time.strftime("%H:%M:%S", cur)

                complete_query = "UPDATE assy2read SET data7 = 1, contents1 = 18 WHERE id = 6"

                main_cursor.execute(complete_query)
                main_db.commit()

                log_msg = f"[RH][{cur_date} {cur_time}]PC complete signal\n"
                log_message(log_msg)
    
        main_cursor.close()
        main_db.close()
        print("Main DB Disconnected...")

        assy_cursor.close()
        assy_db.close()
        print("Assy DB Disconnected...")

# 업데이트가 중지된 동안 새로운 scan값이 들어오는지 관찰하는 메소드
def check_new_data():
    # 가장 최근 데이터의 DATA1 - DATA5의 값이 None 타입일 때 새로운 scan값이 들어온 것으로 간주
    db = mysql.connector.connect(**assy_db_config)
    cursor = db.cursor(dictionary = True)

    if db.is_connected():
        print("Assy DB Connected... (For checking new INSERT)")

    query = "SELECT data1, data2, data3, data4, data5 FROM assy_rh ORDER BY date DESC, time DESC LIMIT 1"
    cursor.execute(query)
    record = cursor.fetchone()

    if record:
        null_check = True
        for key, value in record.items():
            if value is not None:
                null_check = False
    
        global running
        running = null_check

    cursor.close()
    db.close()
    print("Assy DB Disconnected... (For checking new INSERT)")

polling_interval = 0.5

init_running()

while True:
    try:
        if running:
            time.sleep(polling_interval)
            read_plc_data()
            print(f"Running: {running}")
        else:
            time.sleep(polling_interval)
            check_new_data()
            print(f"Running: {running}")
    except Exception as e:
        cur = time.localtime()
        cur_date = time.strftime("%Y.%m.%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        error_msg = f"[RH][{cur_date} {cur_time}]{traceback.format_exc()}"
        log_message(error_msg)
        print(error_msg)

        continue