# DB 관련 모듈
import mysql.connector
from mysql.connector import Error

# 사운드 관련 모듈
import pygame

# 로컬 시간 모듈
import time

# DB 정보
db_config = {
    "host": "192.168.200.2",
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

# 너트러너 합불값 체크 메소드
def read_input_data():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary = True)

        if db.is_connected():
            print("DB Conncted...")
    except Error as e:
        print(f"Error during DB connection: {e}")
        return
    except Exception as e:
        print(f"Exception during DB connection: {e}")
        return
    
    # read data
    select_query = "SELECT data1, data3 FROM input1 WHERE id = 2"

    cursor.execute(select_query)
    record = cursor.fetchone()

    if record['data1'] == "1":
        ok_sound.play()

        time.sleep(0.1)

        update_query = "UPDATE input1 SET data1 = 0 WHERE id = 2"
        cursor.execute(update_query)
        db.commit()
    elif record['data1'] == "2":
        ng_sound.play()

        time.sleep(0.1)

        update_query = "UPDATE input1 SET data1 = 0 WHERE id = 2"
        cursor.execute(update_query)
        db.commit()

    if record['data3'] == "1":
        ok_sound.play()

        time.sleep(0.1)

        update_query = "UPDATE input1 SET data3 = 0 WHERE id = 2"
        cursor.execute(update_query)
        db.commit()
    elif record['data3'] == "2":
        ng_sound.play()

        time.sleep(0.1)

        update_query = "UPDATE input1 SET data3 = 0 WHERE id = 2"
        cursor.execute(update_query)
        db.commit()

    cursor.close()
    db.close()
    print("DB Disconnected...")

polling_interval = 0.5

while True:
    read_input_data()
    time.sleep(1)