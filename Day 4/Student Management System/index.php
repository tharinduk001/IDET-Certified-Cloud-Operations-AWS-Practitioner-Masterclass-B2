<?php include 'db.php'; ?>

<!DOCTYPE html>
<html>

<head>

<title>Student Management System</title>

<style>

body{
    font-family: Arial;
    margin:40px;
}

table{
    width:100%;
    border-collapse: collapse;
}

table, th, td{
    border:1px solid black;
    padding:10px;
}

a{
    text-decoration:none;
    padding:5px 10px;
    background:#333;
    color:white;
}

</style>

</head>

<body>

<h1>Student Management System</h1>

<a href="create.php">Add Student</a>

<br><br>

<table>

<tr>
    <th>ID</th>
    <th>Name</th>
    <th>Email</th>
    <th>Course</th>
    <th>Actions</th>
</tr>

<?php

$query = "SELECT * FROM students";

$result = mysqli_query($conn, $query);

while($row = mysqli_fetch_assoc($result)) {

?>

<tr>

<td><?php echo $row['id']; ?></td>
<td><?php echo $row['name']; ?></td>
<td><?php echo $row['email']; ?></td>
<td><?php echo $row['course']; ?></td>

<td>

<a href="edit.php?id=<?php echo $row['id']; ?>">
Edit
</a>

<a href="delete.php?id=<?php echo $row['id']; ?>">
Delete
</a>

</td>

</tr>

<?php } ?>

</table>

</body>
</html>