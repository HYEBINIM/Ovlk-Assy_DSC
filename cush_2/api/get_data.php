<?php
    $host = "localhost";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $query = "SELECT * FROM result1 ORDER BY id DESC LIMIT 1";
    $result = mysqli_query($conn, $query);
    if(!$result) die($conn -> error);

    $record = mysqli_fetch_array($result);

    $data = array();
    if($record['data9'] == "1"){
        array_push($data, 1);   // LH or RH 구분자

        array_push($data, $record['data2']);
        array_push($data, $record['data3']);
        array_push($data, $record['data4']);
        array_push($data, $record['data5']);
        array_push($data, $record['data7']);
    }elseif($record['data9'] == "2"){
        array_push($data, 2);   // LH or RH 구분자

        array_push($data, $record['data2']);
        array_push($data, $record['data3']);
        array_push($data, $record['data5']);
        array_push($data, $record['data7']);
    }else{
        array_push($data, 0);   // 잘못된 데이터 구분자

        $result -> close();
        $conn -> close();

        echo json_encode($data);

        return;
    }

    $return_data = array();

    array_push($return_data, $data);
    array_push($return_data, $record['data6']);    // 토크값
    array_push($return_data, isset($record['data8']) ? $record['data8'] : "");    // 등급값
    array_push($return_data, isset($record['data10']) ? $record['data10'] : "");   // 판독률

    echo json_encode($return_data);
?>