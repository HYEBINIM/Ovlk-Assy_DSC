<?php
    // count 데이터를 가져올 키오스크 DB 정보
    $host = "192.168.200.2:3306";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $query_lh = "SELECT id, lh_code, lh_count FROM index_code WHERE lh_code IS NOT NULL AND lh_code <> ''";
    $query_rh = "SELECT id, rh_code, rh_count FROM index_code WHERE rh_code IS NOT NULL AND rh_code <> ''";

    $result_lh = mysqli_query($conn, $query_lh);
    if(!$result_lh) die($conn -> error);
    $result_rh = mysqli_query($conn, $query_rh);
    if(!$result_rh) die($conn -> error);

    $idx = 0;
    $count = array();
    while($record_lh = mysqli_fetch_array($result_lh)){
        $count[$idx]['index'] = $record_lh['id'];
        $count[$idx]['dir'] = "LH";
        $count[$idx]['code'] = $record_lh['lh_code'];
        $count[$idx]['count'] = $record_lh['lh_count'];
        $idx++;
    }

    while($record_rh = mysqli_fetch_array($result_rh)){
        $count[$idx]['index'] = $record_rh['id'];
        $count[$idx]['dir'] = "RH";
        $count[$idx]['code'] = $record_rh['rh_code'];
        $count[$idx]['count'] = $record_rh['rh_count'];
        $idx++;
    }

    $result_lh -> close();
    $result_rh -> close();
    $conn -> close();

    echo json_encode($count);
?>