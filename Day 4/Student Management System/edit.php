<?php

include 'db.php';

$id = $_GET['id'];

$query = "SELECT * FROM students WHERE id=$id";

$result = mysqli_query($conn, $query);

$row = mysqli_fetch_assoc($result);

if(isset($_POST['update'])) {

    $name = mysqli_real_escape_string($conn, $_POST['name']);
    $email = mysqli_real_escape_string($conn, $_POST['email']);
    $course = mysqli_real_escape_string($conn, $_POST['course']);

    $updateQuery = "UPDATE students
                    SET
                    name='$name',
                    email='$email',
                    course='$course'
                    WHERE id=$id";

    mysqli_query($conn, $updateQuery);

    header("Location:index.php");
    exit();
}

?>

<!DOCTYPE html>
<html>

<head>
<title>Edit Student</title>
</head>

<body>

<h1>Edit Student</h1>

<form method="POST">

<input type="text"
       name="name"
       value="<?php echo $row['name']; ?>"
       required>

<br><br>

<input type="email"
       name="email"
       value="<?php echo $row['email']; ?>"
       required>

<br><br>

<input type="text"
       name="course"
       value="<?php echo $row['course']; ?>"
       required>

<br><br>

<button type="submit" name="update">
Update Student
</button>

</form>

</body>
</html>