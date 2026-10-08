# PART 2 - AWS DATABASE SERVICES

## RDS - Relational Database Service 
- Fully managed relational database service that handles setup, operation, and scaling of databases. 
- Supports major engines: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, and Aurora.
- Automates backups, patching, monitoring, and failure detection. 
- Provides high availability using Multi‑AZ deployments with automatic failover. 
- Offers read replicas for read scalability and offloading heavy queries. 
- Allows point‑in‑time recovery and snapshot-based restores. 
- Provides cost‑efficient, resizable compute and storage options. 
- Integrates with VPC and IAM for network isolation and access control. 
- Available in On‑Demand and Reserved Instance pricing models. 

## 2.1 RDS Supported Engines

| Engine            | When to use                                                                       |
| ----------------- | --------------------------------------------------------------------------------- |
| **MySQL**         | Most popular open-source relational DB. Great for web apps.                       |
| **PostgreSQL**    | More powerful and feature-rich than MySQL. Good for complex queries.              |
| **MariaDB**       | MySQL fork with extra features. Drop-in MySQL replacement.                        |
| **Oracle**        | Enterprise legacy applications. Expensive licensing.                              |
| **SQL Server**    | Windows and .NET applications. Microsoft ecosystem.                               |
| **Amazon Aurora** | AWS's own cloud-native DB (MySQL/Postgres compatible). Fastest and most scalable. |

---

## 2.2 Amazon Aurora

Aurora is not just another engine -- it is a completely re-architected relational database built by AWS.

- Automatically scales storage from 10 GB up to 128 TB with no downtime
- Up to 5x faster than standard MySQL, 3x faster than PostgreSQL
- 6 copies of your data spread across 3 Availability Zones automatically
- Fully compatible with MySQL and PostgreSQL -- your app does not need code changes to use it
- **Aurora Serverless v2**: DB capacity scales up and down automatically based on workload; ideal for variable or unpredictable traffic

> Use Aurora when you need serious performance and high availability. For dev/test or smaller workloads, standard RDS MySQL or PostgreSQL is fine and cheaper.

---

## 2.3 NoSQL: Amazon DynamoDB

Not all data fits neatly into tables with rows and columns. That is where **NoSQL** databases come in.

**Amazon DynamoDB** is AWS's fully managed NoSQL key-value and document database.

| Feature     | Detail                                                         |
| ----------- | -------------------------------------------------------------- |
| Data model  | Key-value and document (JSON-like items)                       |
| Scaling     | Automatically scales to handle millions of requests per second |
| Latency     | Single-digit millisecond at any scale                          |
| Maintenance | Zero -- no servers, no patching, nothing to manage             |
| Pricing     | Pay per read/write capacity or use on-demand mode              |

**When to use DynamoDB:**

- Shopping carts, session stores (fast key-value lookups)
- IoT data, event logs (high write throughput)
- Gaming leaderboards (simple, extremely fast reads)
- Any use case where access patterns are well-defined and scale is massive

**When NOT to use DynamoDB:**

- Complex joins across multiple entities
- Ad-hoc queries that are not defined upfront
- Scenarios requiring strong consistency across many records at once

---

## 2.4 DEMO - Provision an RDS MySQL Instance & Connect to It

### Goal

- Create a **Free Tier** RDS MySQL instance with **public access enabled**
- Place it in the **Default VPC** using its existing public subnets
- Connect from **AWS CloudShell** using a plain MySQL command
- Run basic SQL commands to demonstrate the database works

> **note:** We enable public access here purely for training convenience so CloudShell can reach the DB without needing a VPN or bastion host. In a real production environment, databases must always go in **private subnets** with Public access set to No - only your application servers inside the same VPC should be able to reach them.

### What you will need

- AWS Console access
- The **Default VPC** (recommended -- it already has public subnets in every AZ, with an IGW already wired up, so no manual networking is needed)
- MySQL client (available in CloudShell by default -- no installation required)

---

### STEP 1 - Create a DB Subnet Group

RDS requires a **DB Subnet Group** - a named collection of subnets across at least 2 Availability Zones where the DB instance can be placed. This is a one-time setup per VPC.

1. In the AWS Console, search for **RDS** and open the RDS service.
2. In the left sidebar, click **Subnet groups**.
3. Click **Create DB Subnet Group**.
4. Fill in:
   - **Name:** `my-db-subnet-group`
   - **Description:** `Subnet group for training RDS`
   - **VPC:** Select the **Default VPC** (it appears as `vpc-xxxxxxxx (default)`)
5. Under **Add subnets**:
   - **Availability Zones:** Select all available AZs in the list (e.g., `ap-south-1a`, `ap-south-1b`, `ap-south-1c`)
   - **Subnets:** Select all subnets that appear -- these are the Default VPC's pre-built public subnets
6. Click **Create**.
7. Subnet group created.

---

### STEP 2 - Create a Security Group for RDS

We need a Security Group that allows MySQL traffic on port 3306 to reach the RDS instance from CloudShell.

1. In the AWS Console, go to **EC2 -> Security Groups** (left sidebar, under Network & Security).
2. Click **Create security group**.
3. Fill in:
   - **Security group name:** `rds-mysql-sg`
   - **Description:** `Allow MySQL access`
   - **VPC:** Select the **Default VPC**
4. Under **Inbound rules**, click **Add rule**:
   - **Type:** `MySQL/Aurora`
   - **Protocol:** `TCP` (auto-filled)
   - **Port range:** `3306` (auto-filled)
   - **Source:** `0.0.0.0/0`
5. Click **Create security group**.
6. Security group created.

---

### STEP 3 - Create the RDS MySQL Instance

1. In the RDS console, click **Databases** in the left sidebar.
2. Click **Create database**.
3. **Choose a database creation method:** `Standard create`
4. **Engine options:** Select `MySQL`
5. **Edition:** `MySQL Community`
6. **Engine version:** Leave as default (latest)
7. **Templates:** Select **Free tier**

   > This is critical to avoid charges. Free tier gives 750 hours per month of `db.t3.micro` for 12 months on a new AWS account.

8. **Settings:**
   - **DB instance identifier:** `my-training-db`
   - **Master username:** `admin`
   - **Credentials management:** `Self managed`
   - **Master password:** Set a password you will remember (e.g., `Training@2024!`)
   - **Confirm password:** Re-enter the same password

9. **Instance configuration:**
   - **DB instance class:** `db.t3.micro` (pre-selected by the Free tier template)

10. **Storage:**
    - **Storage type:** `gp2`
    - **Allocated storage:** `20 GiB` (minimum, pre-filled)
    - Uncheck **Enable storage autoscaling** (not needed for demo)

11. **Connectivity:**
    - **Compute resource:** `Don't connect to an EC2 compute resource`
    - **Network type:** `IPv4`
    - **Virtual private cloud (VPC):** Select the **Default VPC**
    - **DB subnet group:** `my-db-subnet-group`
    - **Public access:** `Yes` -- This is required. It gives the instance a public IP so CloudShell can reach it.
    - **VPC security group:** Select `rds-mysql-sg`. Remove the `default` security group if it is pre-selected.
    - **Availability Zone:** `No preference`
    - **RDS Proxy:** Leave unchecked

12. **Database authentication:** `Password authentication`

13. **Additional configuration** (click to expand this section):
    - **Initial database name:** `trainingdb`
      > If you skip this field, no database schema is created inside the instance and you will need to run `CREATE DATABASE trainingdb;` manually after connecting.
    - **Backup:** Uncheck **Enable automated backups** (simplifies the demo)
    - **Encryption:** Leave as default

14. Click **Create database**.
15. The database will now show **Status: Creating**. This takes **5 to 10 minutes**. The console refreshes automatically.

> AWS is provisioning a managed server, installing MySQL, configuring the network endpoint, and setting up credentials -- all without you touching a single server or running a single installer.

---

### STEP 4 - Verify Public Access is Enabled

Once status shows **Available**, confirm public access before trying to connect.

1. Click on `my-training-db` to open the instance details.
2. Click the **Connectivity & security** tab.
3. Confirm **Publicly accessible** shows `Yes`.
4. If it shows `No`, click **Modify** (top right), scroll to Connectivity, change Public access to `Yes`, click **Continue**, choose **Apply immediately**, and click **Modify DB instance**. Wait about 2 minutes for it to apply.

---

### STEP 5 - Find the RDS Endpoint

Still on the **Connectivity & security** tab:

1. Find the **Endpoint** field and copy the full value -- it looks like:
   ```
   my-training-db.xxxxxxxx.ap-south-1.rds.amazonaws.com
   ```
2. Note the **Port:** `3306`

Keep this endpoint copied. You will use it in the next step.

---

### STEP 6 - Connect Using AWS CloudShell

**AWS CloudShell** is a browser-based terminal built into the AWS Console. It comes with the MySQL client pre-installed -- no setup needed.

1. In the AWS Console top navigation bar, click the **CloudShell** icon (it looks like `>_`).
2. A terminal panel opens at the bottom. Wait about 30 seconds for it to fully initialize.
3. Verify the MySQL client is available:

   ```bash
   mysql --version
   ```

   Expected output: `mysql  Ver 8.0.xx Distrib ...`

4. Run this command to connect -- replace the endpoint with your actual value and use the username you set:

   ```bash
   mysql -h your-rds-endpoint.rds.amazonaws.com -P 3306 -u your_username -p
   ```

   Concrete example:

   ```bash
   mysql -h my-training-db.c1k8uy6sghai.ap-south-1.rds.amazonaws.com -P 3306 -u admin -p
   ```

   > **Important:** Do not add `--ssl-ca`, `--ssl-mode`, `--ssl-verify-server-cert`, or any certificate flags. The MySQL client handles TLS automatically. Adding those flags requires a cert file that is not present in CloudShell and will cause the connection to hang or fail with an error.

5. You will see the password prompt:

   ```
   Enter password:
   ```

   Type your password (e.g., `Training@2024!`) and press Enter. The password will not appear on screen as you type -- that is expected behaviour.

6. If successful, you will see the MySQL prompt:
   ```
   Welcome to the MySQL monitor.  Commands end with ; or \g.
   ...
   mysql>
   ```

---

### Troubleshooting - If the Connection Fails or Hangs

Work through this checklist in order:

1. RDS **Public access** is set to `Yes` -- check the Connectivity & security tab of the DB instance
2. The DB is in the **Default VPC**, not the custom training VPC (which has only private subnets with no internet route)
3. Security group `rds-mysql-sg` inbound rule: Type `MySQL/Aurora`, Port `3306`, Source `0.0.0.0/0` -- scroll right in the security group console to confirm the Source column value
4. The security group `rds-mysql-sg` is the one actually attached to the RDS instance -- not the `default` SG
5. RDS status is **Available**, not Modifying or Creating
6. You are not using any SSL flags in the connect command

---

### STEP 7 - Run Basic SQL Commands

Once connected at the `mysql>` prompt, run these commands one at a time and explain each to the team:

```sql
-- Show all databases on this instance
SHOW DATABASES;

-- Switch into the training database
USE trainingdb;

-- Create an employees table
CREATE TABLE employees (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    salary     DECIMAL(10,2),
    joined_on  DATE
);

-- Insert sample records
INSERT INTO employees (name, department, salary, joined_on) VALUES
    ('Alice Johnson', 'Engineering', 95000.00, '2022-03-15'),
    ('Bob Smith',     'Marketing',   72000.00, '2021-07-20'),
    ('Carol White',   'Engineering', 110000.00, '2020-01-10'),
    ('David Lee',     'HR',          68000.00, '2023-05-01');

-- Fetch all rows
SELECT * FROM employees;

-- Filter: engineers only
SELECT name, salary FROM employees WHERE department = 'Engineering';

-- Aggregate: average salary per department
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;

-- List all tables in the database
SHOW TABLES;

-- Show the table schema
DESCRIBE employees;
```

Expected output of `SELECT * FROM employees;`:

```
+----+---------------+-------------+-----------+------------+
| id | name          | department  | salary    | joined_on  |
+----+---------------+-------------+-----------+------------+
|  1 | Alice Johnson | Engineering | 95000.00  | 2022-03-15 |
|  2 | Bob Smith     | Marketing   | 72000.00  | 2021-07-20 |
|  3 | Carol White   | Engineering | 110000.00 | 2020-01-10 |
|  4 | David Lee     | HR          | 68000.00  | 2023-05-01 |
+----+---------------+-------------+-----------+------------+
```

Exit the MySQL session when done:

```bash
exit
```

---

### RDS Demo Summary - What We Did

1. Created a **DB Subnet Group** using the Default VPC's existing public subnets across all AZs
2. Created a **Security Group** (`rds-mysql-sg`) allowing inbound TCP 3306 from `0.0.0.0/0`
3. Provisioned an **RDS MySQL Free Tier** instance (`db.t3.micro`) with **Public access: Yes** in the Default VPC
4. Confirmed the endpoint and verified Public access before connecting
5. Connected from **AWS CloudShell** using the command: `mysql -h ENDPOINT -P 3306 -u admin -p`
6. Created a table, inserted rows, and ran SELECT queries

---

## 2.6 RDS vs Aurora vs DynamoDB - Quick Decision Guide

```
Need a relational database (tables, SQL, joins)?
|
|-- Yes --> Do you need maximum performance and auto-scaling storage?
|           |-- Yes --> Use Aurora (MySQL or Postgres compatible)
|           +-- No  --> Use RDS MySQL / PostgreSQL (simpler, cheaper)
|
+-- No  --> Is your data schema flexible or are you doing key-value lookups?
            |-- Yes --> Use DynamoDB
            +-- No  --> Consider ElastiCache, Neptune, Timestream, etc.
```

---

## 2.7 Other AWS Database Services - Quick Overview

| Service                | Type                               | Best For                                           |
| ---------------------- | ---------------------------------- | -------------------------------------------------- |
| **Amazon ElastiCache** | In-memory (Redis / Memcached)      | Caching, session management, leaderboards          |
| **Amazon Redshift**    | Data Warehouse (columnar SQL)      | Analytics on petabytes of data                     |
| **Amazon Neptune**     | Graph DB                           | Social networks, fraud detection, knowledge graphs |
| **Amazon Timestream**  | Time-series                        | IoT telemetry, monitoring metrics                  |
| **Amazon DocumentDB**  | Document DB (MongoDB compatible)   | JSON documents, content management                 |
| **Amazon Keyspaces**   | Wide-column (Cassandra compatible) | High-volume, low-latency time-series               |
| **Amazon QLDB**        | Ledger DB                          | Audit trails, immutable transaction history        |

---

## 2.8 Cleanup - Avoid Charges After the Session

Delete all demo resources after the session to prevent unexpected billing.

### Delete the RDS Instance

1. Go to **RDS -> Databases**
2. Select `my-training-db`
3. Click **Actions -> Delete**
4. Uncheck **Create final snapshot**
5. Type `delete me` in the confirmation field
6. Click **Delete**

### Delete Supporting Resources

1. Delete the DB Subnet Group: **RDS -> Subnet groups -> select -> Delete**
2. Delete Security Group `rds-mysql-sg`: **EC2 -> Security Groups -> select -> Delete**

### Delete VPC Resources (optional -- VPCs are free, but good hygiene)

1. Detach and delete the IGW: **VPC -> Internet Gateways -> select -> Actions -> Detach, then Delete**
2. Delete the two subnets: **VPC -> Subnets -> select each -> Delete**
3. Delete the public route table: **VPC -> Route Tables -> select -> Delete**
4. Delete the VPC: **VPC -> Your VPCs -> select -> Delete**

---

---

# PART 3 - AMAZON DYNAMODB - DEMO

## What is DynamoDB 

Amazon DynamoDB is a fully managed, serverless NoSQL database. There are no servers to provision, no OS to patch, no subnet groups to configure. You create a table and start using it immediately.

It stores data as **items** (equivalent to rows in SQL) made up of **attributes** (equivalent to columns). Unlike SQL, different items in the same table can have completely different attributes -- the schema is flexible.

---

## Key Concepts Before We Start

| DynamoDB Term | SQL Equivalent         | What it means                                                                                                                 |
| ------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Table         | Table                  | Container for your data                                                                                                       |
| Item          | Row                    | A single record                                                                                                               |
| Attribute     | Column                 | A field on an item                                                                                                            |
| Partition Key | Primary Key            | Uniquely identifies an item. DynamoDB uses this to decide which server to store the item on.                                  |
| Sort Key      | Composite Key (part 2) | Optional. Combined with the Partition Key to form a composite primary key. Allows multiple items with the same Partition Key. |
| Index (GSI)   | Secondary Index        | Lets you query on attributes other than the primary key                                                                       |

### Partition Key vs Sort Key - Quick Example

Imagine a table storing orders:

| Partition Key (customer_id) | Sort Key (order_date) | item     |
| --------------------------- | --------------------- | -------- |
| CUST001                     | 2024-01-10            | Laptop   |
| CUST001                     | 2024-02-05            | Mouse    |
| CUST002                     | 2024-01-20            | Keyboard |

- You can fetch all orders for `CUST001` using just the Partition Key
- You can fetch orders for `CUST001` placed after `2024-02-01` using both keys together
- Without a Sort Key, each customer could only have one order (Partition Key must be unique on its own)

---

## What We Will Build

A simple **Product Catalog** table for an e-commerce application.

- Table name: `ProductCatalog`
- Partition Key: `product_id` (String)
- We will insert products, update them, query them, use filters, and delete items
- We will also create a **Global Secondary Index (GSI)** to query by category

---

## PART 1 - Create the Table

### STEP 1 - Open DynamoDB

1. In the AWS Console search bar, type **DynamoDB** and open the service.
2. Click **Create table** (orange button, top right).

---

### STEP 2 - Configure the Table

1. Fill in the table details:
   - **Table name:** `ProductCatalog`
   - **Partition key:** `product_id` | Type: `String`
   - Leave **Sort key** unchecked for now (we will add a GSI later)

2. Under **Table settings**, select **Customize settings** so we can review the options.

3. **Table class:** `DynamoDB Standard`

4. **Read/write capacity settings:**
   - Select **On-demand**
   - This means you pay per request with no capacity planning needed. Perfect for demos and unpredictable workloads.
   - The alternative is **Provisioned** where you set a fixed number of read and write units per second. Used when your traffic is predictable and you want to control costs.

5. **Encryption at rest:** Leave as default (`Owned by Amazon DynamoDB`)

6. Click **Create table**.

7. Wait about 30 seconds. The table status will change from `Creating` to `Active`.

---

## PART 2 - Insert Items (PutItem)

### STEP 3 - Open the Table and Insert the First Item

1. Click on `ProductCatalog` to open the table.
2. Click the **Actions** button and select **Create item**.
3. You will see a form with one attribute already shown: `product_id`.
4. Set the value of `product_id` to: `P001`
5. Now click **Add new attribute** to add more fields:

   | Attribute name | Type    | Value               |
   | -------------- | ------- | ------------------- |
   | `product_name` | String  | `Wireless Keyboard` |
   | `category`     | String  | `Electronics`       |
   | `price`        | Number  | `49.99`             |
   | `in_stock`     | Boolean | `true`              |
   | `brand`        | String  | `Logitech`          |

6. Click **Create item**.
7. Item saved.

> Notice we did not define any of these extra attributes when we created the table. In DynamoDB you never define columns upfront -- you just add whatever attributes you want on each item. The only requirement is that every item must have the Partition Key (`product_id`).

---

### STEP 4 - Insert More Items

Repeat the same process (Actions -> Create item) for each of the following products. This gives us enough data to demonstrate queries and filters.

**Item 2:**

| Attribute      | Type    | Value         |
| -------------- | ------- | ------------- |
| `product_id`   | String  | `P002`        |
| `product_name` | String  | `USB-C Hub`   |
| `category`     | String  | `Electronics` |
| `price`        | Number  | `34.99`       |
| `in_stock`     | Boolean | `true`        |
| `brand`        | String  | `Anker`       |

**Item 3:**

| Attribute      | Type    | Value           |
| -------------- | ------- | --------------- |
| `product_id`   | String  | `P003`          |
| `product_name` | String  | `Office Chair`  |
| `category`     | String  | `Furniture`     |
| `price`        | Number  | `299.00`        |
| `in_stock`     | Boolean | `false`         |
| `brand`        | String  | `Herman Miller` |

**Item 4:**

| Attribute      | Type    | Value           |
| -------------- | ------- | --------------- |
| `product_id`   | String  | `P004`          |
| `product_name` | String  | `Standing Desk` |
| `category`     | String  | `Furniture`     |
| `price`        | Number  | `549.00`        |
| `in_stock`     | Boolean | `true`          |
| `brand`        | String  | `Flexispot`     |

**Item 5:**

| Attribute      | Type    | Value                 |
| -------------- | ------- | --------------------- |
| `product_id`   | String  | `P005`                |
| `product_name` | String  | `Mechanical Keyboard` |
| `category`     | String  | `Electronics`         |
| `price`        | Number  | `129.00`              |
| `in_stock`     | Boolean | `true`                |
| `brand`        | String  | `Keychron`            |
| `switch_type`  | String  | `Brown`               |

> Item P005 has an extra attribute `switch_type` that none of the other items have. This is perfectly valid in DynamoDB. You would never be able to do this in a traditional relational database without first running an ALTER TABLE command.

<br/>

#### Another way to Add Data (PartiQL) -  Will discuss it later
```
INSERT INTO "ProductCatalog" VALUE {
  'product_id': 'P002',
  'product_name': 'USB-C Hub',
  'category': 'Electronics',
  'price': 34.99,
  'in_stock': true,
  'brand': 'Anker'
};

INSERT INTO "ProductCatalog" VALUE {
  'product_id': 'P003',
  'product_name': 'Office Chair',
  'category': 'Furniture',
  'price': 299.00,
  'in_stock': false,
  'brand': 'Herman Miller'
};

INSERT INTO "ProductCatalog" VALUE {
  'product_id': 'P004',
  'product_name': 'Standing Desk',
  'category': 'Furniture',
  'price': 549.00,
  'in_stock': true,
  'brand': 'Flexispot'
};

INSERT INTO "ProductCatalog" VALUE {
  'product_id': 'P005',
  'product_name': 'Mechanical Keyboard',
  'category': 'Electronics',
  'price': 129.00,
  'in_stock': true,
  'brand': 'Keychron',
  'switch_type': 'Brown'
};

```

---

## PART 3 - Read Operations

### STEP 5 - Scan (Read All Items)

A **Scan** reads every item in the table from top to bottom. It is the simplest way to read data but the most expensive for large tables because it reads everything regardless of what you are looking for.

1. In the left sidebar, click **Explore items**.
2. Make sure `ProductCatalog` is selected.
3. Under **Scan or query items**, leave it on **Scan** and click **Run**.
4. All 5 items appear in the results panel.

> In a table with 10 million items, a Scan would read all 10 million items to find the ones you want. That is slow and expensive. For production use cases you almost always want a Query or a filter on an index instead.

---

### STEP 6 - Get a Single Item by Partition Key (Query)

A **Query** looks up items using the Partition Key directly. DynamoDB hashes the key and goes straight to the correct storage partition -- no full table scan. This is the fastest and cheapest read operation.

1. Still on the **Explore items** page.
2. Change the operation from **Scan** to **Query**.
3. Under **Partition key**, type: `P003`
4. Click **Run**.
5. Only the Office Chair item appears.

> This is the fundamental DynamoDB access pattern. You design your Partition Key so that the most common query in your application is always a direct key lookup. This is why DynamoDB is so fast -- it never searches, it always goes directly to the right place.

---

### STEP 7 - Scan with a Filter Expression

What if you want all Electronics items? You cannot Query by `category` because it is not the Partition Key. Instead, you Scan with a filter.

1. Change back to **Scan**.
2. Expand **Filters**.
3. Add a filter:
   - **Attribute name:** `category`
   - **Type:** `String`
   - **Condition:** `Equal to`
   - **Value:** `Electronics`
4. Click **Run**.
5. Only the 3 Electronics items (P001, P002, P005) appear.

> Important distinction -- the filter is applied AFTER DynamoDB scans the whole table. It still reads all 5 items internally and then filters the results. For a large table this is still expensive. The correct solution for querying by category is a Global Secondary Index, which we will create next.

---

### STEP 8 - Use PartiQL to Query with SQL Syntax

DynamoDB supports **PartiQL** - a SQL-compatible query language. This is useful for developers already comfortable with SQL.

1. In the left sidebar, click **PartiQL editor**.
2. Run the following statements one at a time by typing them in the editor and clicking **Run**:

**Select all items:**

```sql
SELECT * FROM ProductCatalog
```

**Select a specific item by Partition Key:**

```sql
SELECT * FROM ProductCatalog
WHERE product_id = 'P001'
```

**Select specific attributes only:**

```sql
SELECT product_id, product_name, price FROM ProductCatalog
WHERE product_id = 'P003'
```

**Insert a new item using PartiQL:**

```sql
INSERT INTO ProductCatalog VALUE {
    'product_id': 'P006',
    'product_name': 'Laptop Stand',
    'category': 'Accessories',
    'price': 39.99,
    'in_stock': true,
    'brand': 'Rain Design'
}
```

> PartiQL makes DynamoDB accessible to anyone who knows SQL. However, the underlying constraints still apply - a SELECT without a WHERE on the Partition Key triggers a full scan. The syntax looks like SQL but the performance rules are still DynamoDB's rules.

---

## PART 4 - Update an Item

### STEP 9 - Update an Item via the Console

Scenario: The Office Chair (P003) is now back in stock and the price has been reduced.

1. Go back to **Explore items**.
2. Run a Scan to see all items.
3. Click on the `P003` row to open the item editor.
4. Find the `in_stock` attribute and click the edit (pencil) icon next to it.
   - Change the value from `false` to `true`
   - Click the checkmark to confirm
5. Find the `price` attribute and click the edit icon.
   - Change the value from `299.00` to `249.00`
   - Click the checkmark to confirm
6. Click **Save changes**.
7. Item updated.

---

### STEP 10 - Update an Item Using PartiQL

You can also update using PartiQL. Go to the **PartiQL editor** and run:

```sql
UPDATE ProductCatalog
SET price = 44.99
SET in_stock = true
WHERE product_id = 'P002'
```

Then verify the change:

```sql
SELECT product_id, product_name, price, in_stock
FROM ProductCatalog
WHERE product_id = 'P002'
```

---

## PART 5 - Global Secondary Index (GSI)

A **Global Secondary Index** lets you query DynamoDB on attributes other than the Partition Key. It is essentially a copy of your table, automatically maintained by DynamoDB, but organised by a different key.

### STEP 11 - Create a GSI on the category Attribute

This will allow us to query all products in a specific category efficiently -- without scanning the whole table.

1. Open the `ProductCatalog` table.
2. Click the **Indexes** tab.
3. Click **Create index**.
4. Fill in:
   - **Partition key:** `category` | Type: `String`
   - **Sort key:** Leave empty for now
   - **Index name:** `category-index` (auto-filled, you can keep it)
   - **Attribute projections:** `All` (copies all attributes into the index)
5. Click **Create index**.
6. Wait about 1 to 2 minutes for the index status to change from `Creating` to `Active`.

---

### STEP 12 - Query Using the GSI

Now we can query by `category` directly without a Scan.

1. Go to **Explore items**.
2. Change the operation to **Query**.
3. You will now see a dropdown next to the table name -- change it from `ProductCatalog` to `category-index`.
4. Under **Partition key**, type: `Electronics`
5. Click **Run**.
6. Only the Electronics items appear - and this was a direct key lookup on the index, not a full table scan.

> This is the right way to solve the "query by category" problem. You define the access patterns you need upfront and create indexes for each one. DynamoDB maintains these indexes automatically as you write data. The trade-off is slightly higher write costs and storage, since DynamoDB is maintaining extra copies of the data.

---

## PART 6 - Delete Operations

### STEP 13 - Delete a Single Item

1. Go to **Explore items** and run a Scan.
2. Check the checkbox next to the `P006` row (the Laptop Stand we inserted via PartiQL).
3. Click **Actions -> Delete items**.
4. Confirm the deletion.
5. Item deleted.

---

### STEP 14 - Delete an Item Using PartiQL

```sql
DELETE FROM ProductCatalog
WHERE product_id = 'P005'
```

Run a SELECT to confirm it is gone:

```sql
SELECT * FROM ProductCatalog
WHERE product_id = 'P005'
```

No results returned confirms the item was deleted.

---

## PART 7 - Conditional Writes

One of DynamoDB's powerful features is **conditional expressions** on writes. You can tell DynamoDB to only perform a write if a certain condition is true - preventing accidental overwrites.

### STEP 15 - Conditional Write Using PartiQL

Scenario: Only update the price of P004 if it is currently above 500. This prevents overwriting a price that was already discounted.

```sql
UPDATE ProductCatalog
SET price = 499.00
WHERE product_id = 'P004'
AND price > 500
```

Run it once - it will succeed because the current price is 549.00.

Run it again - it will fail with a `ConditionalCheckFailedException` because the price is now 499.00, which is not greater than 500.

> This is extremely useful in high-concurrency scenarios. For example, an inventory system where two processes might try to decrement stock at the same time. You can write: "only decrement stock if current stock is greater than 0" -- preventing negative inventory without needing application-level locking.

---

## PART 8 - TTL (Time to Live)

**TTL** lets DynamoDB automatically delete items after a certain time. You mark an attribute as the TTL attribute and set it to a Unix epoch timestamp. DynamoDB checks this periodically and deletes expired items at no extra cost.

### STEP 16 - Enable TTL on the Table

1. Open the `ProductCatalog` table.
2. Click the **Additional settings** tab.
3. Under **Time to Live (TTL)**, click **Enable**.
4. Set the **TTL attribute name** to: `expires_at`
5. Click **Enable TTL**.

Now insert an item with a short TTL to demonstrate (TTL value must be a Unix timestamp -- items typically expire within 48 hours, not instantly):

```sql
INSERT INTO ProductCatalog VALUE {
    'product_id': 'P007',
    'product_name': 'Flash Sale Item',
    'category': 'Electronics',
    'price': 9.99,
    'in_stock': true,
    'brand': 'Generic',
    'expires_at': 1700000000
}
```

> The `expires_at` value `1782844799` is a timestamp in the past (June 30 2026), so DynamoDB will mark this item for deletion. Note that DynamoDB TTL deletion is not instant - it happens within 48 hours of expiry. You can filter out expired items in your application by checking the `expires_at` value yourself if you need immediate exclusion.

> TTL is extremely useful for: session tokens that should expire after 24 hours, temporary discount codes, cache entries, audit logs you only need to keep for 90 days, and any data with a natural expiry. You get automatic cleanup with zero extra cost.

---

## Summary - Operations Covered

| Operation          | Method Used       | What it Does                                                 |
| ------------------ | ----------------- | ------------------------------------------------------------ |
| Create table       | Console           | Provisions a serverless DynamoDB table                       |
| PutItem            | Console form      | Inserts a new item with any attributes                       |
| Scan               | Console + PartiQL | Reads all items in the table                                 |
| Query (by PK)      | Console + PartiQL | Reads items by Partition Key -- fast and cheap               |
| Scan with Filter   | Console           | Scans all, then filters results in memory                    |
| Update             | Console + PartiQL | Modifies attributes on an existing item                      |
| Conditional Update | PartiQL           | Updates only if a condition is true                          |
| Create GSI         | Console           | Creates a secondary index for querying by non-key attributes |
| Query (by GSI)     | Console           | Queries the secondary index directly -- no table scan        |
| Delete             | Console + PartiQL | Removes a specific item                                      |
| TTL                | Console + PartiQL | Automatically expires items at a given timestamp             |

---

## DynamoDB vs RDS - Side by Side Comparison

|              | DynamoDB                                  | RDS MySQL                                            |
| ------------ | ----------------------------------------- | ---------------------------------------------------- |
| Type         | NoSQL (key-value / document)              | Relational (SQL)                                     |
| Schema       | Flexible - attributes defined per item   | Fixed - columns defined at table creation           |
| Scaling      | Infinite, automatic, serverless           | Manual (scale up instance size or add read replicas) |
| Query style  | Key-based lookups, limited ad-hoc queries | Full SQL - joins, subqueries, aggregates            |
| Latency      | Single-digit milliseconds at any scale    | Milliseconds, degrades under load without tuning     |
| Provisioning | Zero - no servers, no subnets            | Instance + subnet group + security group required    |
| Free tier    | Permanent (25 GB, 25 RCU/WCU forever)     | 750 hours per month for 12 months only               |
| Best for     | Known access patterns, massive scale      | Complex relationships, reporting, ad-hoc queries     |

---

## When to Choose DynamoDB

Use DynamoDB when:

- You can define your access patterns upfront
- You need single-digit millisecond latency at any scale
- You do not need complex joins or ad-hoc reporting queries
- You want zero infrastructure management

Do not use DynamoDB when:

- Your queries are unpredictable or highly ad-hoc
- You need complex joins across multiple entities
- Your team is new to NoSQL and the project has a tight deadline -- the learning curve around access pattern design is real

---

## Cleanup - Delete the Table

1. Open the `ProductCatalog` table.
2. Click **Actions -> Delete table**.
3. Type `confirm` in the confirmation field.
4. Click **Delete**.

The table, all its items, and all its indexes are deleted together. No separate cleanup needed.

---
