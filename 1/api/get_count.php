<?php
    $host = "localhost";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $today = date('Y-m-d');

    $query = sprintf("SELECT data0 FROM
    (SELECT * FROM assy_lh
    UNION ALL
    SELECT * FROM assy_rh)
    AS combined_tables
    WHERE date = '%s'
    ORDER BY time DESC", $today);
    $result = mysqli_query($conn, $query);
    if(!$result) die($conn -> error);

    $data = array();
    while($record = mysqli_fetch_array($result)){
        $part_code_arr = explode(chr(29), $record['DATA0']);
        $part_code_all = substr($part_code_arr[2], 1);
        $chunks = str_split($part_code_all, 5);
        $part_code = implode("-", $chunks);
        array_push($data, $part_code);
    }

    $result -> close();
    $conn -> close();

    echo json_encode($data);
?>