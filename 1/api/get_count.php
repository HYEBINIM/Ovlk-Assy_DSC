<?php
    $host = "192.168.200.2:3306";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $query_lh = "SELECT lh_code, lh_count FROM index_code WHERE lh_code IS NOT NULL AND lh_code <> ''";
    $query_rh = "SELECT rh_code, rh_count FROM index_code WHERE rh_code IS NOT NULL AND rh_code <> ''";

    $result_lh = mysqli_query($conn, $query_lh);
    if(!$result_lh) die($conn -> error);

    $result_rh = mysqli_query($conn, $query_rh);
    if(!$result_rh) die($conn -> error);

    $data_lh = array();
    $data_rh = array();

    $idx = 0;
    while($record_lh = mysqli_fetch_array($result_lh)){
        $data_lh[$idx]['code'] = $record_lh['lh_code'];
        $data_lh[$idx]['count'] = $record_lh['lh_count'];
        $idx++;
    }

    $idx = 0;
    while($record_rh = mysqli_fetch_array($result_rh)){
        $data_rh[$idx]['code'] = $record_rh['rh_code'];
        $data_rh[$idx]['code'] = $record_rh['rh_count'];
        $idx++;
    }

    $data = array();
    array_push($data, $data_lh);
    array_push($data, $data_rh);

    echo json_encode($data);
?>