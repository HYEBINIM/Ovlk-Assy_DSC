<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // JSON 데이터 읽기
    $data = json_decode(file_get_contents('php://input'), true);
    
    // 데이터가 잘 수신되었는지 확인
    if ($data === null) {
        echo json_encode(["message" => "데이터 수신 실패."]);
        exit;
    }

    // 필요한 데이터 추출
    $data1 = $data['data1']; //header
    $data2 = $data['data2']; //업체코드
    $data3 = $data['data3']; //부품번호
    $data4 = $data['data4']; //서열코드
    $data5 = $data['data5']; //EO번호
    $data6 = $data['data6']; //생산일자
    $data7 = $data['data7']; //부품4M
    $data8 = $data['data8']; //A_or_at
    $data9 = $data['data9']; //추적번호
    $data10 = $data['data10']; //업체영역
    $data11 = $data['data11']; //trailer

    // ZPL 코드 작성
    $zpl = "
        ^XA
        ^CF0,20
        ^FO145,25^A0N,40,32^FD ".$data3." ^FS
        ^FO145,70^A0N,20,22^FD D_RH NA TER RMT H1R ^FS
        ^FO145,100^A0N,25,23^FD ".$data6." ^FS
        ^FO300,100^A0N,25,23^FD 1 ^FS
        ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
        ^FO20,20^BXN,3,200^FH_^FD".$data1."_1DV".$data2."_1DP".$data3."_1DS".$data4."_1DE".$data5."_1DT".$data6.$data7.$data8.$data9."_1DA_1DC".$data10."_1D".$data11."^FS     
        ^XZ
    ";

    // // 프린터에 ZPL 전송
    // $host = "192.168.200.4";  // 프린터의 IP 주소
    // $port = 6101;              // 프린터의 포트 번호

    // $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    // if ($socket === false) {
    //     echo json_encode(["message" => "소켓 생성 실패."]);
    //     exit;
    // }

    // if (!socket_connect($socket, $host, $port)) {
    //     echo json_encode(["message" => "프린터 연결 실패."]);
    //     exit;
    // }

    // socket_write($socket, $zpl);
    // socket_close($socket);

    echo json_encode($zpl);
} else {
    echo json_encode($zpl);
}
?>
