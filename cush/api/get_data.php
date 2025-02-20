<?php
    $host = "localhost";
    $user = "server";
    $pw = "dltmxm1234";
    $dv = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $query = "SELECT * FROM read1 WHERE id = 5";
    $result = mysqli_query($conn, $query);
    if(!$result) die($conn -> error);

    $record = mysqli_fetch_array($result);

    $data = array();
    array_push($data, $record['data0']);
    array_push($data, $record['data1']);
    array_push($data, $record['data2']);
    array_push($data, $record['data3']);
    array_push($data, $record['data4']);
    array_push($data, $record['data5']);
    array_push($data, $record['data6']);
    array_push($data, $record['data7']);
    array_push($data, $record['data8']);
    array_push($data, $record['data9']);

    $result -> close();
    $conn -> close();

    echo json_encode($data);
?>