# AWS KT: Networking (VPC)

# PART 1 - AWS NETWORKING (VPC)

## 1.1 Concepts: Why Do We Need a VPC?

When you first use AWS, all your resources would be on a flat public network by default -- meaning any EC2 instance, database, or service would be reachable from the internet unless you manually lock it down. That is dangerous.

**Amazon VPC (Virtual Private Cloud)** lets you provision a logically isolated section of the AWS cloud where you can launch AWS resources in a network that you define. Think of it like your own private data center network inside AWS.

---

## 1.2 Core Networking Components

### VPC (Virtual Private Cloud)

- A virtual network dedicated to your AWS account
- You define the **IP address range** using CIDR notation (e.g., `10.0.0.0/16` gives you 65,536 IP addresses)
- Lives within a single **AWS Region** (e.g., `ap-south-1` Mumbai)
- Completely isolated from other VPCs and the public internet by default

### Subnets

- A subdivision of your VPC's IP range
- Must live within a single **Availability Zone (AZ)**
- Two types:
  - **Public Subnet**: Has a route to the internet via an Internet Gateway. Use for web servers, load balancers, bastion hosts.
  - **Private Subnet**: No direct route to the internet. Use for databases, application servers, internal services.

|                 | Public Subnet            | Private Subnet         |
| --------------- | ------------------------ | ---------------------- |
| Internet access | Yes (via IGW)            | No                     |
| Suitable for    | Web servers, NAT Gateway | Databases, App servers |
| Example CIDR    | `10.0.1.0/24`            | `10.0.2.0/24`          |

### Internet Gateway (IGW)

- A horizontally scaled, redundant, AWS-managed component
- Attached to a VPC -- one IGW per VPC
- Allows resources in a **public subnet** to communicate with the internet
- Without an IGW, nothing in your VPC can reach the internet and nothing from the internet can reach your VPC

### Route Tables

- A set of rules (called **routes**) that determine where network traffic is directed
- Every subnet must be associated with exactly one route table
- The **local route** (`10.0.0.0/16 -> local`) is always present and cannot be deleted -- it handles all traffic within the VPC
- To make a subnet **public**, you add a route: `0.0.0.0/0 -> Internet Gateway ID`

### How it all connects (Traffic Flow)

```
Internet
    |
    v
Internet Gateway (IGW)
    |
    v
Route Table (Public: 0.0.0.0/0 -> IGW)
    |
    v
Public Subnet (10.0.1.0/24)
    |   EC2 Web Server
    |
    |   [Internal VPC traffic only below this point]
    v
Private Subnet (10.0.2.0/24)
    |   RDS Database
    v
  (No internet access)
```

---

## 1.3 DEMO 6 - Build a Custom VPC from Scratch

### Goal

Create a VPC with:

- One **Public Subnet** (for a web server or bastion host)
- One **Private Subnet** (for a database)
- An **Internet Gateway** attached to the VPC
- Updated **Route Tables** so the public subnet has internet access

### What you will need

- AWS Console access
- Region: pick any (e.g., `ap-south-1` Mumbai or `us-east-1` N. Virginia)
- No extra cost -- VPCs themselves are free

---

### STEP 1 - Create the VPC

1. In the AWS Console search bar, type **VPC** and click **VPC** under Services.
2. In the left sidebar, click **Your VPCs**.
3. Click the orange **Create VPC** button (top right).
4. Fill in the form:
   - **Resources to create:** Select `VPC only` (not "VPC and more" -- we will do it manually for learning)
   - **Name tag:** `my-training-vpc`
   - **IPv4 CIDR block:** `10.0.0.0/16`
   - **IPv6 CIDR block:** `No IPv6 CIDR block`
   - **Tenancy:** `Default`
5. Click **Create VPC**.
6. You should see a green success banner. Note the **VPC ID** (e.g., `vpc-0abc1234...`).

---

### STEP 2 - Create the Public Subnet

1. In the left sidebar, click **Subnets**.
2. Click **Create subnet**.
3. Fill in:
   - **VPC ID:** Select `my-training-vpc` from the dropdown
4. Under **Subnet settings**:
   - **Subnet name:** `my-public-subnet`
   - **Availability Zone:** Choose the first AZ in the list (e.g., `ap-south-1a`)
   - **IPv4 CIDR block:** `10.0.1.0/24`
5. Click **Create subnet**.
6. Subnet created. Note the **Subnet ID**.

---

### STEP 3 - Create the Private Subnet

1. Click **Create subnet** again.
2. Fill in:
   - **VPC ID:** Select `my-training-vpc`
3. Under **Subnet settings**:
   - **Subnet name:** `my-private-subnet`
   - **Availability Zone:** You can use the same AZ or a different one (e.g., `ap-south-1b`)
   - **IPv4 CIDR block:** `10.0.2.0/24`
4. Click **Create subnet**.
5. Private subnet created.

---

### STEP 4 - Create and Attach an Internet Gateway

1. In the left sidebar, click **Internet Gateways**.
2. Click **Create internet gateway**.
3. Fill in:
   - **Name tag:** `my-training-igw`
4. Click **Create internet gateway**.
5. You will see the IGW is created but its **State** shows `Detached`.
6. **Now attach it to your VPC:**
   - With the new IGW selected, click the **Actions** button (top right).
   - Click **Attach to VPC**.
   - In the **Available VPCs** dropdown, select `my-training-vpc`.
   - Click **Attach internet gateway**.
7. The IGW State should now show `Attached`.

---

### STEP 5 - Create a Public Route Table

AWS creates a **Main route table** for every VPC automatically. Best practice is **not to modify** the main route table (it applies to all subnets by default). Instead, we create a dedicated one for our public subnet.

1. In the left sidebar, click **Route Tables**.
2. You will see an existing route table -- this is the **main** one for `my-training-vpc`. Notice it only has the local route (`10.0.0.0/16 -> local`).
3. Click **Create route table**.
4. Fill in:
   - **Name:** `my-public-route-table`
   - **VPC:** Select `my-training-vpc`
5. Click **Create route table**.
6. New route table created.

---

### STEP 6 - Add the Internet Route to the Public Route Table

1. Click on `my-public-route-table` to open its details.
2. Click the **Routes** tab.
3. Click **Edit routes**.
4. Click **Add route**.
5. Fill in the new route:
   - **Destination:** `0.0.0.0/0` -- This means "all traffic going anywhere on the internet"
   - **Target:** Click the dropdown, select **Internet Gateway**, then select `my-training-igw`
6. Click **Save changes**.
7. The Routes tab should now show two routes:
   - `10.0.0.0/16 -> local` (VPC internal traffic)
   - `0.0.0.0/0 -> igw-xxxxxxxx` (internet traffic)

---

### STEP 7 - Associate the Public Subnet with the Public Route Table

Adding a route to the route table is not enough -- we need to explicitly tell the public subnet to use this route table.

1. Still on the `my-public-route-table` details page.
2. Click the **Subnet associations** tab.
3. Click **Edit subnet associations**.
4. Check the box next to `my-public-subnet`.
5. Click **Save associations**.
6. The public subnet is now associated with the public route table.

---

### STEP 8 - Enable Auto-assign Public IP for the Public Subnet

When you launch an EC2 instance into the public subnet, it needs a public IP to be reachable from the internet.

1. In the left sidebar, click **Subnets**.
2. Select `my-public-subnet`.
3. Click **Actions -> Edit subnet settings**.
4. Under **Auto-assign IP settings**, check **Enable auto-assign public IPv4 address**.
5. Click **Save**.
6. Done. Any EC2 instance launched into this subnet will automatically receive a public IP.

---

### VPC Summary - What We Built

```
VPC: my-training-vpc (10.0.0.0/16)
|
|-- Public Subnet: my-public-subnet (10.0.1.0/24)
|       |
|       +-- Route Table: my-public-route-table
|               |-- 10.0.0.0/16 -> local
|               +-- 0.0.0.0/0  -> my-training-igw   [Internet access]
|
|-- Private Subnet: my-private-subnet (10.0.2.0/24)
|       |
|       +-- Route Table: Main (auto-created)
|               +-- 10.0.0.0/16 -> local             [No internet access]
|
+-- Internet Gateway: my-training-igw (Attached)
```

---

### Key Takeaways - Networking

- A **VPC** is your private network inside AWS
- **Subnets** are segments of that network, each scoped to one Availability Zone
- A subnet becomes **public** only when it has a route to an Internet Gateway
- **Route tables** are the traffic directors -- each subnet has one
- The **Internet Gateway** is the single entry and exit point for internet traffic
- Best practice: databases go in **private subnets**, web servers go in **public subnets**

---
