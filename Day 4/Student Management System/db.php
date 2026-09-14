<?php

$host = "localhost";
$user = "appuser";
$password = "StrongPassword123";
$database = "studentapp";

$conn = mysqli_connect(
    $host,
    $user,
    $password,
    $database
);

if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

?>