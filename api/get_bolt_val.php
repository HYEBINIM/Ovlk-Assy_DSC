<?php
    $no = $_POST['no'];

    // $host = "localhost";
    // $user = "root";
    // $pw = "autoset";
    // $db = "dataset_ov1k";

    $host = "localhost";
    $user = "root";
    $pw = "autoset";
    $db = "dataset";

    // $host = "localhost";
    // $user = "server";
    // $pw = "dltmxm1234";
    // $db = "dataset";

    $conn = mysqli_connect($host, $user, $pw, $db);
    if($conn -> connect_error) die($conn -> connect_error);

    if($no == 1){
        $query_lh = "SELECT DATA0 FROM input1 WHERE id = 1";
    }elseif($no == 2){
        $query_lh = "SELECT DATA2 FROM input1 WHERE id = 1";
    }elseif($no == 3){
        // rh bolt 1
    }elseif($no == 4){
        // rh bolt 2
    }
?>