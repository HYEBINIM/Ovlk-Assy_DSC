# 라벨프린터 출력 코드
# 30 _1E RS
# 29 _1D GS
# 04 _04 EOT

import socket
import sys

def main():
    host = "127.0.0.1"
    port = 12345
    # host = "192.168.94.48"  # 프린터의 IP 주소
    # port = 6101              # 프린터의 포트 번호

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((host, port))  # 프린터에 연결
    print(f"프린터에 연결됨: {host}:{port}")

    # 커맨드라인 인자에서 데이터 가져오기
    date = sys.argv[1]  # DATE
    lot_start = sys.argv[2]  # LOT START
    part_number = sys.argv[3]  # PART NUMBER
    qty = sys.argv[4]  # QTY
    positions = sys.argv[5:]  # 바코드 위치 데이터

    # ZPL 코드 생성
    zpl1 = """
        ^XA
        ^CF0,20
        ^FO{x},{y}^A0N,40,32^FD {part_number} ^FS
        ^FO{x},{y}^A0N,20,22^FD D_RH NA TER RMT H1R ^FS
        ^FO{x},{y}^A0N,25,23^FD {date} ^FS
        ^FO{x},{y}^A0N,25,23^FD {lot_start} ^FS
        ^FO{x},{y}^A0N,25,23^FD QTY: {qty} ^FS
    """.format(part_number=part_number, date=date, lot_start=lot_start, qty=qty)

    # 각 바코드 위치에 대한 ZPL 추가
    for pos in positions:
        x, y, w, h = pos.split(',')  # X, Y, W, H 값을 분리
        zpl1 += f"^FO{x},{y}^BXN,{w},{h},Y,N,N,N,D,{part_number}^FS\n"

    zpl1 += "^XZ"  # ZPL 종료

    server_socket.sendall(zpl1.encode('utf-8'))  # ZPL 코드 전송
    print("ZPL 코드 전송 완료")

    server_socket.close()
    print("서버 종료")

if __name__ == "__main__":
    main()
