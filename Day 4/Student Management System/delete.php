<?php

include 'db.php';

$id = $_GET['id'];

$query = "DELETE FROM students WHERE id=$id";

mysqli_query($conn, $query);

header("Location:index.php");
exit();

?>