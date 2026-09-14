<?php

include 'db.php';

if(isset($_POST['submit'])) {

    $name = mysqli_real_escape_string($conn, $_POST['name']);
    $email = mysqli_real_escape_string($conn, $_POST['email']);
    $course = mysqli_real_escape_string($conn, $_POST['course']);

    $query = "INSERT INTO students(name,email,course)
              VALUES('$name','$email','$course')";

    $result = mysqli_query($conn, $query);

    if($result){
        header("Location: index.php");
        exit();
    } else {
        echo "Error: " . mysqli_error($conn);
    }
}

?>

<!DOCTYPE html>
<html>

<head>
<title>Add Student</title>
</head>

<body>

<h1>Add Student</h1>

<form method="POST">

<input type="text"
       name="name"
       placeholder="Student Name"
       required>

<br><br>

<input type="email"
       name="email"
       placeholder="Student Email"
       required>

<br><br>

<input type="text"
       name="course"
       placeholder="Course"
       required>

<br><br>

<button type="submit" name="submit">
Save Student
</button>

</form>

</body>
</html>