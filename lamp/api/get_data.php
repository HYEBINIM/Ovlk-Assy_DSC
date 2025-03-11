<?php
    // kiosk DB config
    $host = "192.168.200.2:3306";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    // connection
    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    // select query
    $query = "SELECT * FROM call1 ORDER BY id DESC LIMIT 1";
    $result = mysqli_query($conn, $query);
    if(!$result) die($conn -> error);

    $record = mysqli_fetch_array($result);

    $data = array();
    array_push($data, $record['DATA0']);
    array_push($data, $record['DATA1']);
    array_push($data, $record['DATA2']);
    array_push($data, $record['DATA3']);
    array_push($data, $record['DATA4']);
    array_push($data, $record['DATA5']);
    array_push($data, $record['DATA6']);
    array_push($data, $record['DATA7']);

    $result -> close();
    $conn -> close();

    echo json_encode($data);
?>