# 시리얼 통신 모듈
import serial

# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 지역 시간 모듈
import time

# 파일 시스템 관련 모듈
import os

# 랜덤값 생성 모듈
import random

# 스캔 검증, 스캔 로트 코드 등을 업데이트할 plc DB
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

# 인덱스와 지그 번호를 가져올 조립 1차 PC의 DB
jig_db_config = {
    "host": "192.168.200.9",
    "port": 3306,
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset",
    "charset": "utf8"
}

# 에러 로깅 메소드
def log_message(message, log_file="/AutoSet6/public_html/log/main.log"):
    log_dir = os.path.dirname(log_file)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok = True)

    with open(log_file, "a") as f:
        f.write(message)

# 두 개의 바코드 데이터를 비교하는 메소드
def compare_data(pre_data, new_data):
    if pre_data is None:
        return False

    pre_data_split = pre_data.split(chr(29))
    new_data_split = new_data.split(chr(29))

    # 업체 영역(토크) 제거
    del pre_data_split[7]
    del new_data_split[7]

    # 재조합
    pre_data = chr(29).join(pre_data_split)
    new_data = chr(29).join(new_data_split)

    if pre_data == new_data:
        return True
    else:
        return False

# 바코드의 prefix로 LH, RH 구분해주는 메소드
def get_direction(code):
    # 구분자는 prefix의 3번째 문자
    source = int(code[2])

    # 3: RH / 4: LH
    dir = "Undefined"
    if source == 3:
        dir = "LH"
    elif source == 4:
        dir = "RH"
    
    return dir

# 스캔값에서 업체 영역(토크)만 추출하는 메소드
def get_torque(data):
    data_split = data.split(chr(29))

    torque = data_split[7][1:]

    return torque

# 스캔값의 업체 영역(토크)을 변경하는 메소드
def set_torque(data, torque):
    data_split = data.split(chr(29))

    data_split[7] = "C" + torque

    data = chr(29).join(data_split)

    return data

# 스캔값의 날짜를 추출하는 메소드
def get_scan_date(data):
    data_split = data.split(chr(29))

    scan_date = data_split[5]

    return scan_date[1:3]

# 스캐너 연동 메소드
def scan():
    port = "COM1"
    baud_rate = 9600

    try:
        ser = serial.Serial(port, baud_rate, timeout = 1)
        
        cur = time.localtime()
        cur_date = time.strftime("%Y.%m.%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        log_msg = f"[scan3_1][{cur_date} {cur_time}]{port} Connected...\n"
        log_message(log_msg)
        print(log_msg)

        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode("utf-8").strip()
                    
                    cur = time.localtime()
                    cur_date = time.strftime("%Y.%m.%d", cur)
                    cur_time = time.strftime("%H:%M:%S", cur)

                    log_msg = f"[scan3_1][{cur_date} {cur_time}]{port} Connected...\n"
                    log_message(log_msg)
                    print(log_msg)

                    # 여러 데이터가 한번에 들어온 경우 반복문 돌리도록 지시 (EOT 기준으로 구분)
                    inputs = data.split(chr(4))

                    for elem in inputs:
                        if elem == '':
                            continue

                        data = elem + chr(4)

                        split_data = data.split(chr(29))
                        try:
                            # 제품 코드 앞에 붙은 'P' 제거
                            part_code = split_data[2][1:]
                            dir = get_direction(part_code)
                        except Exception as e:
                            # 잘못된 QR코드를 스캔한 경우 다시 스캔하도록 지시
                            cur = time.localtime()
                            cur_date = time.strftime("%Y.%m.%d", cur)
                            cur_time = time.strftime("%H:%M:%S", cur)

                            error_msg = f"[scan3_1][{cur_date} {cur_time}]Invalide data: Re-scan\n"
                            log_message(error_msg)
                            print(error_msg)

                            continue
                        
                        if dir == "LH":
                            table = "assy_lh"
                            row_write_id = 2
                            index_col = "lh_code"
                        elif dir == "RH":
                            table = "assy_rh"
                            row_write_id = 6
                            index_col = "rh_code"
                        else:
                            cur = time.localtime()
                            cur_date = time.strftime("%Y.%m.%d", cur)
                            cur_time = time.strftime("%H:%M:%S", cur)

                            error_msg = f"[scan3_1][{cur_date} {cur_time}]Invalide data: Re-scan\n"
                            log_message(error_msg)
                            print(error_msg)

                            continue
                        
                        try:
                            main_db = mysql.connector.connect(**main_db_config)
                            main_cursor = main_db.cursor(dictionary = True)

                            if main_db.is_connected():
                                print("Main DB Connected...")
                            
                            assy_db = mysql.connector.connect(**assy_db_config)
                            assy_cursor = assy_db.cursor(dictionary = True)

                            if assy_db.is_connected():
                                print("Assy DB Connected...")
                            
                            jig_db = mysql.connector.connect(**jig_db_config)
                            jig_cursor = jig_db.cursor(dictionary = True)

                            if jig_db.is_connected():
                                print("Jig(Assy1) DB Connected...")
                        except Error as e:
                            cur = time.localtime()
                            cur_date = time.strftime("%Y.%m.%d", cur)
                            cur_time = time.strftime("%H:%M:%S", cur)

                            error_msg = f"[scan3_1][{cur_date} {cur_time}]Error during DB connection: {e}\n"
                            log_message(error_msg)
                            print(error_msg)

                            continue
                        except Exception as e:
                            cur = time.localtime()
                            cur_date = time.strftime("%Y.%m.%d", cur)
                            cur_time = time.strftime("%H:%M:%S", cur)

                            error_msg = f"[scan3_1][{cur_date} {cur_time}]Exception during DB connection: {e}\n"
                            log_message(error_msg)
                            print(error_msg)

                            continue
                        
                        # 직전 스캔 데이터 읽어오기
                        query_pre = f"SELECT id, data0, data9 FROM {table} ORDER BY id DESC LIMIT 1"
                        assy_cursor.execute(query_pre)
                        pre_record = assy_cursor.fetchone()

                        # 직전 스캔 데이터 읽어오기
                        query_pre = f"SELECT id, data0, data9, data10 FROM {table} ORDER BY id DESC LIMIT 1"
                        assy_cursor.execute(query_pre)
                        pre_record = assy_cursor.fetchone()

                        # 직전 스캔 데이터가 없는 경우
                        if pre_record is None:
                            pre_record = {
                                "data0": None
                            }

                        if get_scan_date(data) == "00":
                            # 초기화 데이터의 경우

                            cur = time.localtime()
                            cur_date = time.strftime("%Y-%m-%d", cur)
                            cur_time = time.strftime("%H:%M:%S", cur)

                            query_init = f"INSERT INTO {table} (date, time, data0) VALUES ('{cur_date}', '{cur_time}', '{data}')"
                            assy_cursor.execute(query_init)
                            assy_db.commit()

                            log_msg = f"[scan3_1][{cur_date} {cur_time}]Initialize monitor.\n"
                            log_message(log_msg)
                            print(log_msg)
                        elif compare_data(pre_record['data0'], data):
                            # 이전 데이터와 중복인 경우

                            # 해당 레코드에서 인덱스 추출
                            index = pre_record['data10']

                            cur = time.localtime()
                            cur_date = time.strftime("%Y-%m-%d", cur)
                            cur_time = time.strftime("%H:%M:%S", cur)

                            if pre_record['data9'] is None:
                                # 단순 중복 스캔인 경우
                                query_duple = f"UPDATE {table} set time = '{cur_time}' WHERE id = {pre_record['id']}"
                                assy_cursor.execute(query_duple)
                                assy_db.commit()

                                query_update = f"UPDATE assy3read SET data0 = 1, data1 = {index}, contents1 = 2 WHERE id = {row_write_id}"
                            else:
                                # 출하 바코드인 경우 (등급값이 있는 경우)
                                if pre_record['data9'] == "A" or pre_record['data9'] == "B":
                                    query_update = f"UPDATE assy3read SET data0 = 1, data1 = {index}, contents1 = 2 WHERE id = {row_write_id}"
                                else:
                                    query_update = f"UPDATE assy3read SET data0 = 2, data1 = {index}, contents1 = 2 WHERE id = {row_write_id}"
                            
                            main_cursor.execute(query_update)
                            main_db.commit()

                            log_msg = f"[scan3_1][{cur_date} {cur_time}]Send scan signal and index({index}).\n"
                            log_message(log_msg)
                            print(log_msg)
                        else:
                            # 이전 데이터와 중복이 아닌 경우 (즉, 관리 바코드인 경우)

                            # 조립 1차 DB에서 같은 바코드의 데이터 추출
                            query_jig = f"SELECT data7, data8, data9, data10 FROM {table} WHERE data0 = '{data}' ORDER BY id DESC LIMIT 1"
                            jig_cursor.execute(query_jig)
                            jig_record = jig_cursor.fetchone()

                            cur = time.localtime()
                            cur_date = time.strftime("%Y-%m-%d", cur)
                            cur_time = time.strftime("%H:%M:%S", cur)

                            if jig_record is None:
                                # 1차에 해당 바코드가 없는 경우 (1차 공정을 건너뛴 경우)
                                log_msg = f"[scan3_1][{cur_date} {cur_time}]No assy1 data. Insert random data.\n"
                                log_message(log_msg)
                                print(log_msg)
                                
                                # 제품에 해당하는 인덱스 추출
                                query_index = f"SELECT id FROM index_code WHERE {index_col} = '{part_code}' LIMIT 1"
                                main_cursor.execute(query_index)
                                index_record = main_cursor.fetchone()

                                # 토크값 추출 (실제 검사값이 아니며, 임의로 부여한 양품값)
                                torque = get_torque(data)
                                torque_1 = int(float(torque[:4]) * 100)
                                torque_2 = int(float(torque[4:]) * 100)

                                # 랜덤 지그 번호 부여 (지그와 인덱스가 맞지 않을 수 있음)
                                jig = random.randint(1, 4)
                                index = index_record['id']
                            else:
                                # 1차에 해당 바코드가 있는 경우 (정상적으로 공정을 진행한 경우)
                                torque_1 = int(jig_record['data7'])
                                torque_2 = int(jig_record['data8'])
                                jig = jig_record['data9']
                                index = jig_record['data10']

                                # 바코드에 사용할 업체 영역 생성
                                mod_torque_1 = torque_1 // 10
                                mod_torque_2 = torque_2 // 10

                                float_torque_1 = mod_torque_1 / 10
                                float_torque_2 = mod_torque_2 / 10

                                str_torque_1 = f"{float_torque_1:04.1f}"
                                str_torque_2 = f"{float_torque_2:04.1f}"

                                torque  = str_torque_1 + str_torque_2

                                # 바코드의 업체 영역을 실제 검사값으로 변경
                                data = set_torque(data, torque)

                            query_insert = f"INSERT INTO {table} (date, time, data0, data7, data10, data17, data18) VALUES ('{cur_date}', '{cur_time}', '{data}', '{jig}', '{index}', '{torque_1}', '{torque_2}')"
                            assy_cursor.execute(query_insert)
                            assy_db.commit()

                            query_update = f"UPDATE assy3read SET data0 = 1, data1 = {index}, contents1 = 2 WHERE id = {row_write_id}"
                            main_cursor.execute(query_update)
                            main_db.commit()

                            log_msg = f"[scan3_1][{cur_date} {cur_time}]Insert new data. Send scan signal and index({index}).\n"
                            log_message(log_msg)
                            print(log_msg)

                        main_cursor.close()
                        main_db.close()
                        print("Main DB Disconnected...")

                        assy_cursor.close()
                        assy_db.close()
                        print("Assy DB Disconnected...")

                        jig_cursor.close()
                        jig_db.close()
                        print("Jig(Assy1) DB Disconnected...")
            except Exception as e:
                cur = time.localtime()
                cur_date = time.strftime("%Y.%m.%d", cur)
                cur_time = time.strftime("%H:%M:%S", cur)

                error_msg = f"[scan3_1][{cur_date} {cur_time}]Exception during recieving data: {e}\n"
                log_message(error_msg)
                print(error_msg)
                continue
    except Exception as e:
        cur = time.localtime()
        cur_date = time.strftime("%Y.%m.%d", cur)
        cur_time = time.strftime("%H:%M:%S", cur)

        error_msg = f"[scan3_1][{cur_date} {cur_time}]Exception during serial connection: {e}\n"
        log_message(error_msg)
        print(error_msg)
    
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()

            cur = time.localtime()
            cur_date = time.strftime("%Y.%m.%d", cur)
            cur_time = time.strftime("%H:%M:%S", cur)

            log_msg = f"[scan3_1][{cur_date} {cur_time}]{port} Disconnected...\n"
            log_message(log_msg)
            print(log_msg)

if __name__ == "__main__":
    scan()