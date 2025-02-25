# 시리얼 통신 모듈
import serial

# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 지역 시간 모듈
import time

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
    "database": "dataset",
    "charset": "utf8"
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

# 스캔 데이터에서 업체 코드 부분 기준으로 앞, 뒤로 나누어 주는 메소드
# 조립 1차 DB에서 인덱스 및 지그값 추출을 위해 SELECT 할 때 WHERE절에 사용
def devide_code(data):
    split_data = data.split(chr(29))

    prefix = split_data[0]
    suffix = chr(29).join(split_data[2:])

    fix = {
        "prefix": prefix,
        "suffix": suffix
    }

    return fix

# 새로 들어온 스캔값이 직전 스캔값과 동일한지 비교하는 메소드
# 동일할 경우 별도 INSERT 없이 스캔 검증과 로트 번호만 UPDATE
def compare_data(pre_data, new_data):
    pre_data_split = pre_data.split(chr(29))
    new_data_split = new_data.split(chr(29))

    # 업체 코드 제거
    del pre_data_split[1]
    del new_data_split[1]

    # 재조합
    pre_data = chr(29).join(pre_data_split)
    new_data = chr(29).join(new_data_split)

    if pre_data == new_data:
        return True
    else:
        return False

# 바코드의 prefix로 LH, RH 구분해주는 메소드
# parameter: code([String] 바코드의 부품 코드 부분에서 prefix 추출하여 전달)
def get_direction(code):
    # 구분자는 prefix의 3번째 문자임
    source = int(code[2])
    
    # 3: LH / 4: RH
    dir = "Undefined"
    if source == 3:
        dir = "LH"
    elif source == 4:
        dir = "RH"

    return dir
    
# 스캐너 연동 메소드
def scan():
    port = "COM1"
    baud_rate = 9600

    try:
        ser = serial.Serial(port, baud_rate, timeout = 1)
        print(f"{port} Connected...")

        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode("utf-8").strip()
                    print(f"Recieved Data: {data.encode()}")

                    split_data = data.split(chr(29))
                    try:
                        # 제품 코드 앞에 붙은 'P' 제거
                        part_code = split_data[2][1:]
                        dir = get_direction(part_code)
                    except Exception as e:
                        # 잘못된 QR코드를 스캔한 경우 다시 스캔하도록 지시
                        print(f"Invalid data: Re-scan")
                        continue
                    
                    if dir == "LH":
                        table = "assy_lh"
                        row_write_id = 2
                    elif dir == "RH":
                        table = "assy_rh"
                        row_write_id = 6
                    else:
                        # LH, RH 구분이 되지 않는 경우 다시 스캔하도록 지시
                        print("Invalid data: Re-scan")
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
                        print(f"Error during DB Connection: {e}")
                        return
                    except Exception as e:
                        print(f"Exception during DB Connection: {e}")
                        return
                    
                    # 직전 스캔 데이터 읽어오기
                    query_pre = f"SELECT data0 FROM {table} ORDER BY id DESC LIMIT 1"
                    assy_cursor.execute(query_pre)
                    pre_record = assy_cursor.fetchone()

                    # 스캔 데이터에서 업체 코드 기준으로 prefix와 suffix 구분
                    fix = devide_code(data)
                    
                    # 조립 1차 DB에서 업체 코드 제외 모든 부분이 같은 데이터의 인덱스 및 지그값 추출
                    query_jig = f"SELECT data9, data10 FROM {table} WHERE data0 LIKE '{fix['prefix']}%' AND data0 LIKE '%{fix['suffix']}' ORDER BY date DESC, time DESC LIMIT 1"
                    jig_cursor.execute(query_jig)
                    jig_record = jig_cursor.fetchone()
                    print(jig_record)
                    jig = jig_record['data9']
                    index = jig_record['data10']

                    query_update = f"UPDATE assy2read SET data0 = 1, data1 = {index}, contents1 = 2 WHERE id = {row_write_id}"
                    main_cursor.execute(query_update)
                    main_db.commit()

                    # 새로운 스캔 데이터인 경우 INSERT
                    if not compare_data(pre_record['data0'], data):
                        cur = time.localtime()
                        cur_date = time.strftime("%Y-%m-%d", cur)
                        cur_time = time.strftime("%H:%M:%S", cur)

                        query_insert = f"INSERT INTO {table} (date, time, data0, data6, data7) VALUES ('{cur_date}', '{cur_time}', '{data}', '{jig}', '{index}')"
                        assy_cursor.execute(query_insert)
                        assy_db.commit()
                    
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
                print(f"Error at point 1: {e}")
    except Exception as e:
        print(f"Error at point 2: {e}")
    
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()
            print(f"{port} Disconnected...")

if __name__ == "__main__":
    scan()