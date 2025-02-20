<?php
    $host = "localhost";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $query_dir = "SELECT data0 FROM read1 WHERE id = 1";
    $result_dir = mysqli_query($conn, $query_dir);
    if(!$result_dir) die($conn -> error);

    $record_dir = mysqli_fetch_array($result_dir);
    $dir = $record_dir['data0'];

    $query = "SELECT * FROM read1 WHERE id = 5";
    $result = mysqli_query($conn, $query);
    if(!$result) die($conn -> error);

    $record = mysqli_fetch_array($result);

    $data = array();
    if($dir == '1'){
        // LH
        array_push($data, 1);
        array_push($data, $record['data0']);
        array_push($data, $record['data1']);
        array_push($data, $record['data2']);
        array_push($data, $record['data3']);
        array_push($data, $record['data4']);
    }elseif($dir == '2'){
        // RH
        array_push($data, 2);
        array_push($data, $record['data5']);
        array_push($data, $record['data6']);
        array_push($data, $record['data7']);
        array_push($data, $record['data8']);
        array_push($data, $record['data9']);
    }

    $result_dir -> close();
    $result -> close();
    $conn -> close();

    echo json_encode($data);
?>