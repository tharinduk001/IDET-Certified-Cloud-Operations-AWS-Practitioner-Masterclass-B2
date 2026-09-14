# IDET DAY 4 - AWS EC2 PHP CRUD Application Deployment Guide

---

## Deploy a Student Management System on AWS EC2 Using Apache, PHP, and MySQL

# Project Overview

This project demonstrates how to deploy a complete CRUD (Create, Read, Update, Delete) web application on AWS EC2 using:

- AWS EC2
- Ubuntu Linux
- Apache Web Server
- PHP
- MySQL Database

By completing this project, you will learn:

- Launching and configuring EC2 instances
- Connecting to Linux servers using SSH
- Installing Apache, PHP, and MySQL
- Creating MySQL databases and tables
- Hosting a PHP application
- Building a CRUD system
- Configuring AWS Security Groups
- Troubleshooting Apache and PHP errors

---

# Final Architecture

```text
User → AWS EC2 → Apache → PHP Application → MySQL Database
```

---

# Technology Stack

| Component      | Technology          |
| -------------- | ------------------- |
| Cloud Provider | AWS                 |
| Compute        | EC2                 |
| OS             | Ubuntu Server 24.04 |
| Web Server     | Apache2             |
| Backend        | PHP                 |
| Database       | MySQL               |

---

# Step 1 - Create AWS Account

Go to:

```text
https://aws.amazon.com/console/
```

Sign in and open:

- EC2 Dashboard

---

# Step 2 - Launch EC2 Instance

Click:

```text
Launch Instance
```

## Configure Instance

### Name

```text
student-management-server
```

### AMI

```text
Ubuntu Server 24.04 LTS
```

### Instance Type

```text
t2.micro
```

### Key Pair

Create a new key pair:

```text
student-management-key.pem
```

Download and securely store the `.pem` file.

---

# Step 3 - Configure Security Group

Allow these inbound rules:

| Type  | Port |
| ----- | ---- |
| SSH   | 22   |
| HTTP  | 80   |
| HTTPS | 443  |

---

# Step 4 - Connect to EC2

## Linux / Mac / Git Bash

```bash
chmod 400 student-management-key.pem

ssh -i student-management-key.pem ubuntu@YOUR_PUBLIC_IP
```

Example:

```bash
ssh -i student-management-key.pem ubuntu@13.xx.xx.xx
```

---

# Step 5 - Update Ubuntu Server

```bash
sudo apt update && sudo apt upgrade -y
```

---

# Step 6 - Install Apache, PHP, and MySQL

Install required packages:

```bash
sudo apt install apache2 mysql-server php php-mysql libapache2-mod-php -y
```

Restart Apache:

```bash
sudo systemctl restart apache2
```

Enable services:

```bash
sudo systemctl enable apache2
sudo systemctl enable mysql
```

---

# Step 7 - Verify Services

Check Apache:

```bash
sudo systemctl status apache2
```

Check MySQL:

```bash
sudo systemctl status mysql
```

Both should show:

```text
active (running)
```

---

# Step 8 - Verify Apache Website

Open browser:

```text
http://YOUR_PUBLIC_IP
```

You should see:

```text
Apache2 Ubuntu Default Page
```

---

# Step 9 - Secure MySQL

Run:

```bash
sudo mysql_secure_installation
```

Recommended answers:

| Question                  | Answer |
| ------------------------- | ------ |
| Set root password         | YES    |
| Remove anonymous users    | YES    |
| Disable remote root login | YES    |
| Remove test database      | YES    |
| Reload privilege tables   | YES    |

---

# Step 10 - Create Database and Table

Login to MySQL:

```bash
sudo mysql
```

Run these SQL commands EXACTLY:

```sql
CREATE DATABASE IF NOT EXISTS studentapp;

CREATE USER IF NOT EXISTS 'appuser'@'localhost'
IDENTIFIED BY 'StrongPassword123';

GRANT ALL PRIVILEGES
ON studentapp.*
TO 'appuser'@'localhost';

FLUSH PRIVILEGES;

USE studentapp;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    course VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Verify table exists:

```sql
SHOW TABLES;
```

Expected output:

```text
students
```

Exit MySQL:

```sql
EXIT;
```

---

# Step 11 - Prepare Application Directory

Move to web root:

```bash
cd /var/www/html
```

Remove default Apache page:

```bash
sudo rm index.html
```

Create application files:

```bash
sudo touch db.php
sudo touch index.php
sudo touch create.php
sudo touch edit.php
sudo touch delete.php
```

Set permissions:

```bash
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

---

# Step 12 - Configure Database Connection

Open:

```bash
sudo nano /var/www/html/db.php
```

Paste:

```php
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
```

Save file.

---

# Step 13 - Create Main Page (Read Operation)

Open:

```bash
sudo nano /var/www/html/index.php
```

Paste:

```php
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
```

Save file.

---

# Step 14 - Create Student Page (Create Operation)

Open:

```bash
sudo nano /var/www/html/create.php
```

Paste:

```php
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
```

Save file.

---

# Step 15 - Create Edit Page (Update Operation)

Open:

```bash
sudo nano /var/www/html/edit.php
```

Paste:

```php
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
```

Save file.

---

# Step 16 - Create Delete Page (Delete Operation)

Open:

```bash
sudo nano /var/www/html/delete.php
```

Paste:

```php
<?php

include 'db.php';

$id = $_GET['id'];

$query = "DELETE FROM students WHERE id=$id";

mysqli_query($conn, $query);

header("Location:index.php");
exit();

?>
```

Save file.

---

# Step 17 - Restart Apache

```bash
sudo systemctl restart apache2
```

---

# Step 18 - Verify PHP is Working

Create test file:

```bash
sudo nano /var/www/html/test.php
```

Paste:

```php
<?php
phpinfo();
?>
```

Open browser:

```text
http://YOUR_PUBLIC_IP/test.php
```

If PHP information page appears, PHP is working correctly.

Delete test file after verification:

```bash
sudo rm /var/www/html/test.php
```

---

# Step 19 - Access the CRUD Application

Open:

```text
http://YOUR_PUBLIC_IP
```

Now you can:

- Add Students
- View Students
- Edit Students
- Delete Students

---

# Troubleshooting Guide

## HTTP ERROR 500

Check Apache logs:

```bash
sudo tail -f /var/log/apache2/error.log
```

---

## Verify mysqli Extension

Run:

```bash
php -m | grep mysqli
```

If empty:

```bash
sudo apt install php-mysql -y
sudo systemctl restart apache2
```

---

## Verify Database Connection

Login:

```bash
mysql -u appuser -p
```

Password:

```text
StrongPassword123
```

Check database:

```sql
SHOW DATABASES;

USE studentapp;

SHOW TABLES;

SELECT * FROM students;
```

---

# Final Project Structure

```text
/var/www/html
│
├── db.php
├── index.php
├── create.php
├── edit.php
├── delete.php
```

---

# Features Implemented

| Feature              | Description     |
| -------------------- | --------------- |
| Create               | Add students    |
| Read                 | View students   |
| Update               | Edit students   |
| Delete               | Remove students |
| Database Integration | PHP + MySQL     |
| Cloud Hosting        | AWS EC2         |

---

# Skills Learned

This project teaches:

- AWS EC2
- Linux Administration
- Apache Configuration
- PHP Development
- MySQL Database
- CRUD Operations
- Cloud Hosting
- SSH Access
- Web Deployment
- Troubleshooting
