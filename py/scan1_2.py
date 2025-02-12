# 시리얼 통신 모듈
import serial

# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 지역 시간 모듈
import time

# 지그 번호를 읽어오고 스캔 검증, 스캔 로트 코드 등을 업데이트할 plc DB
main_db_config = {
    "host": "192.168.200.2",
    "port": "3306",
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset",
    "charset": "utf8"
}

# 모니터별로 관리할 assy 테이블이 있는 DB
assy_db_config = {
    "host": "localhost",
    "port": "3306",
    "user": "server",
    "password": "dltmxm1234",
    "database": "dataset",
    "charset": "utf8"
}

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
    port = "COM2"
    baud_rate = 9600

    try:
        ser = serial.Serial(port, baud_rate, timeout = 1)
        print(f"{port} Connected...")

        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode("utf-8").strip()
                    print(f"Recieved Data: {data.encode()}")

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
                        print(f"Error during DB Connection: {e}")
                        return
                    except Exception as e:
                        print(f"Exception during DB Connection: {e}")
                        return
                    
                    cur = time.localtime()
                    cur_date = time.strftime("%Y-%m-%d", cur)
                    cur_time = time.strftime("%H:%M:%S", cur)

                    split_data = data.split(chr(29))
                    try:
                        # 제품 코드 앞에 붙은 'P' 제거
                        part_code = split_data[2][1:]
                        dir = get_direction(part_code)
                    except Exception as e:
                        # 잘못된 QR코드를 스캔한 경우
                        print(f"Invalid data: {e}")
                        return
                    
                    query_insert = ""
                    if dir == "LH":
                        query_insert = f"INSERT INTO assy_lh (date, time, data0) VALUES ('{cur_date}', '{cur_time}', '{data}')"
                    elif dir == "RH":
                        query_insert = f"INSERT INTO assy_rh (date, time, data0) VALUES ('{cur_date}', '{cur_time}', '{data}')"

                    if query_insert:
                        assy_cursor.execute(query_insert)
                        assy_db.commit()

                    query_select = ""
                    if dir == "LH":
                        query_select = f"SELECT id FROM jig_code WHERE lh_code = '{part_code}'"
                    elif dir == "RH":
                        query_select = f"SELECT id FROM jig_code WHERE rh_code = '{part_code}'"
                    
                    jig_code = 0
                    if query_select:
                        main_cursor.execute(query_select)
                        jig_record = main_cursor.fetchone()
                        jig_code = jig_record['id']
                    
                    if jig_code > 0:
                        query_update = ""
                        if dir == "LH":
                            query_update = f"UPDATE assy1read SET data1 = 1, data2 = {jig_code}, contents1 = 2 WHERE id = 2"
                        elif dir == "RH":
                            query_update = f"UPDATE assy1read SET data1 = 1, data2 = {jig_code}, contents1 = 2 WHERE id = 5"
                        
                        if query_update:
                            main_cursor.execute(query_update)
                            main_db.commit()
                    
                    main_cursor.close()
                    main_db.close()
                    print("Main DB Disconnected...")

                    assy_cursor.close()
                    assy_db.close()
                    print("Assy DB Disconnected...")
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