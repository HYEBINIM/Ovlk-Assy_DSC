<?php
    $process = $_POST['process'];

    $host = "localhost";
    $user = "server";
    $pw = "dltmxm1234";
    $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    $query_lh = "SELECT * FROM assy_lh ORDER BY date DESC, time DESC LIMIT 1";
    $query_rh = "SELECT * FROM assy_rh ORDER BY date DESC, time DESC LIMIT 1";

    $result_lh = mysqli_query($conn, $query_lh);
    if(!$result_lh) die($conn -> error);

    $result_rh = mysqli_query($conn, $query_rh);
    if(!$result_rh) die($conn -> error);

    $record_lh = mysqli_fetch_array($result_lh);
    $record_rh = mysqli_fetch_array($result_rh);

    $part_code_arr_lh = explode(chr(29), $record_lh['DATA0']);
    $part_code_arr_rh = explode(chr(29), $record_rh['DATA0']);
    $part_code_lh = substr($part_code_arr_lh[2], 1);
    $part_code_rh = substr($part_code_arr_rh[2], 1);

    $data_lh = array();
    $data_rh = array();

    array_push($data_lh, $part_code_lh);
    array_push($data_rh, $part_code_rh);

    switch($process){
        case 1:
            array_push($data_lh, $record_lh['DATA1']);
            array_push($data_lh, $record_lh['DATA2']);
            array_push($data_lh, $record_lh['DATA3']);
            array_push($data_lh, $record_lh['DATA4']);
            array_push($data_lh, $record_lh['DATA5']);
            array_push($data_lh, $record_lh['DATA6']);

            array_push($data_rh, $record_rh['DATA1']);
            array_push($data_rh, $record_rh['DATA2']);
            array_push($data_rh, $record_rh['DATA3']);
            array_push($data_rh, $record_rh['DATA4']);
            array_push($data_rh, $record_rh['DATA5']);
            array_push($data_rh, $record_rh['DATA6']);
            break;
        case 2:
            array_push($data_lh, $record_lh['DATA1']);
            array_push($data_lh, $record_lh['DATA2']);
            array_push($data_lh, $record_lh['DATA3']);
            array_push($data_lh, $record_lh['DATA4']);
            array_push($data_lh, $record_lh['DATA5']);

            array_push($data_rh, $record_rh['DATA1']);
            array_push($data_rh, $record_rh['DATA2']);
            array_push($data_rh, $record_rh['DATA3']);
            array_push($data_rh, $record_rh['DATA4']);
            array_push($data_rh, $record_rh['DATA5']);
            break;
        case 3:
            array_push($data_lh, $record_lh['DATA1']);
            array_push($data_lh, $record_lh['DATA2']);
            array_push($data_lh, $record_lh['DATA3']);
            array_push($data_lh, $record_lh['DATA4']);
            array_push($data_lh, $record_lh['DATA5']);
            array_push($data_lh, $record_lh['DATA11']);
            array_push($data_lh, $record_lh['DATA12']);
            array_push($data_lh, $record_lh['DATA13']);
            array_push($data_lh, $record_lh['DATA6']);

            $rank_lh = array();
            array_push($rank_lh, $record_lh['DATA8']);
            array_push($rank_lh, $record_lh['DATA9']);

            array_push($data_rh, $record_rh['DATA1']);
            array_push($data_rh, $record_rh['DATA2']);
            array_push($data_rh, $record_rh['DATA3']);
            array_push($data_rh, $record_rh['DATA4']);
            array_push($data_rh, $record_rh['DATA5']);
            array_push($data_rh, $record_rh['DATA11']);
            array_push($data_rh, $record_rh['DATA12']);
            array_push($data_rh, $record_rh['DATA13']);
            array_push($data_rh, $record_rh['DATA6']);

            $rank_rh = array();
            array_push($rank_rh, $record_rh['DATA8']);
            array_push($rank_rh, $record_rh['DATA9']);
    }

    $data = array();
    array_push($data, $data_lh);
    array_push($data, $data_rh);

    if($process == 3){
        array_push($data, $rank_lh);
        array_push($data, $rank_rh);
    }

    $result_lh -> close();
    $result_rh -> close();
    $conn -> close();

    echo json_encode($data);
?>