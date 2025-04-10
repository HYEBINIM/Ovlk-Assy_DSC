<?php
    $host = "localhost";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $query = "SELECT * FROM result1 ORDER BY id DESC LIMIT 5";
    $result = mysqli_query($conn, $query);
    if(!$result) die($conn -> error);

    $idx = 0;
    $data = array();
    while($record = mysqli_fetch_array($result)){
        $data[$idx]['dir'] = $record['data9'] == "1" ? "LH" : "RH";
        $data[$idx]['count'] = $record['data9'] == "1" ? $record['data0'] : $record['data1'];
        $data[$idx]['data1'] = $record['data2'];
        $data[$idx]['data2'] = $record['data3'];
        $data[$idx]['data3'] = $record['data4'];
        $data[$idx]['data4'] = $record['data5'];
        $data[$idx]['data5'] = $record['data7'];
        $data[$idx]['data6'] = $record['data8'];
        $idx++;
    }

    echo json_encode($data);
?>