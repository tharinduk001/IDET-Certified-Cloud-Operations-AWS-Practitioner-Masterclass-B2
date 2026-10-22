# Day 9

# SECTION 1 - AWS Billing & Cost Management

## 1.1 How AWS Charges You

AWS uses a **pay-as-you-go** model. You only pay for what you use - no upfront contracts required (unless you choose Reserved pricing).

### Three Core Billing Principles

1. **Pay for what you use** - Resources are metered by the second, minute, or hour
2. **Pay less when you reserve** - Commit to 1–3 years for up to 72% discount
3. **Pay less as you use more** - Volume discounts apply to services like S3 and data transfer

---

## 1.2 AWS Free Tier

AWS provides a **Free Tier** for new accounts (first 12 months + some always-free services).

### Free Tier Types (OLD)

| Type              | Description                            | Example                                                |
| ----------------- | -------------------------------------- | ------------------------------------------------------ |
| **Always Free**   | Never expires, any account             | Lambda (1M requests/month), DynamoDB (25 GB)           |
| **12-Month Free** | Free for first 12 months after sign-up | EC2 (750 hrs/month t2.micro), S3 (5 GB), RDS (750 hrs) |
| **Trials**        | Short-term free access                 | SageMaker (2-month trial)                              |

---

### Free Tier Types (New)

6 Months access with 100 USD Credits to use AWS Services

---

## 1.3 AWS Billing Dashboard

### Where to Find It

`AWS Console → Your Account Name (top-right) → Billing and Cost Management`

### Key Sections in the Billing Dashboard

```
Billing Dashboard
│
├── Bills                   → Detailed monthly charges broken down by service
├── Free Tier               → See your current Free Tier usage vs. limits
├── Cost Explorer           → Visualize and analyze your spending trends
├── Budgets                 → Set spending limits and get alerts
├── Cost Allocation Tags    → Organize costs by project/team
└── Payment Methods         → Manage credit cards, bank accounts
```

---

## 1.4 Understanding Your AWS Bill

### How a Bill Looks

```
Example Monthly Bill
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service             Usage             Charge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Amazon EC2          720 hrs t2.micro  $8.35
Amazon S3           50 GB storage     $1.15
Amazon RDS          720 hrs db.t3     $28.00
Data Transfer OUT   10 GB             $0.90
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total                                 $38.40
```

### Common Charges to Watch

- **EC2 Instances** - Billed per second (Linux) or per hour (Windows) while running
- **EBS Volumes** - Billed per GB provisioned per month, even if EC2 is stopped
- **Data Transfer** - **Inbound is free**. Outbound to the internet costs money
- **Elastic IPs** - Free when attached to a running instance; charged when idle

---

## 1.5 EC2 Pricing Models

| Model                  | Best For                                 | Savings vs On-Demand   |
| ---------------------- | ---------------------------------------- | ---------------------- |
| **On-Demand**          | Unpredictable workloads, short-term use  | Baseline (no discount) |
| **Reserved Instances** | Steady-state, predictable workloads      | Up to 72% off          |
| **Savings Plans**      | Flexible commitment to $/hour usage      | Up to 66% off          |
| **Spot Instances**     | Fault-tolerant, flexible jobs (batch/ML) | Up to 90% off          |
| **Dedicated Hosts**    | Compliance, BYOL licensing               | Higher cost            |

---

## 1.6 AWS Cost Explorer

Cost Explorer lets you **visualize, analyze, and forecast** your AWS spending.

### What You Can Do

- View costs by service, region, linked account, or tag
- See **monthly trends** over the last 12 months
- Forecast next month's costs
- Filter by usage type (e.g., only see EC2 costs)

**Navigation:** `Billing Dashboard → Cost Explorer → Launch Cost Explorer`

---

## 1.7 AWS Budgets

Set a **spending threshold** and get notified when you're approaching or exceeding it.

### Budget Types

- **Cost Budget** - Alert when you spend more than $X
- **Usage Budget** - Alert when you use more than X hours of EC2
- **Reservation Budget** - Track Reserved Instance utilization

### 🖥️ Demo: Creating a Budget Alert

**Step 1:** Go to `Billing → Budgets → Create a Budget`  
**Step 2:** Select **"Use a template (simplified)"**  
**Step 3:** Choose **"Zero spend budget"** (alerts you when ANY charges occur)  
**Step 4:** Enter your email address  
**Step 5:** Click **Create budget**

---

## 1.8 Cost Allocation Tags

Tags are **key-value labels** you attach to AWS resources to organize and track costs.

```
Example Tags:
  Project  = "WebApp"
  Team     = "Backend"
  Env      = "Production"
```

After enabling tags in Billing, you can filter your bill by tag - so you know exactly how much each project or team is costing you.

> 💡 **Best Practice:** Always tag resources from day one. It's nearly impossible to track costs without tags in a large environment.

---

## 1.9 Billing Best Practices - Quick Summary

```
✅ Enable billing alerts immediately after creating your account
✅ Set a Zero Spend Budget for learning accounts
✅ Use the Free Tier wisely - track usage in the Free Tier dashboard
✅ Stop/terminate unused EC2 instances
✅ Delete unused EBS volumes (they bill even when EC2 is off!)
✅ Release unused Elastic IPs
✅ Use Cost Explorer monthly to spot unexpected charges
```

---

---

# SECTION 2 - Amazon EBS (Elastic Block Store)

---

## 2.1 What is EBS?

**Amazon EBS (Elastic Block Store)** is a **persistent block storage service** for use with EC2 instances.

Think of it like a **hard drive (HDD/SSD) that you plug into your virtual server.**

### Key Characteristics

```
┌─────────────────────────────────────────────┐
│              Amazon EC2 Instance             │
│                                             │
│   ┌──────────────┐   ┌──────────────────┐   │
│   │  Root Volume │   │  Extra EBS Volume│   │
│   │  (Boot Disk) │   │  (Data Disk)     │   │
│   └──────┬───────┘   └────────┬─────────┘   │
└──────────┼────────────────────┼─────────────┘
           │                    │
    ┌──────▼────────────────────▼──────┐
    │        AWS EBS Storage Layer      │
    └───────────────────────────────────┘
```

- ✅ **Persistent** - Data survives EC2 instance stop/restart
- ✅ **Block-level** - Acts like a raw physical disk
- ✅ **Attachable** - Attach/detach from EC2 instances
- ✅ **Snapshots** - Back up to S3 at any time
- ❌ **Single AZ** - Tied to one Availability Zone
- ❌ **One EC2 at a time** - Typically attached to one instance (except io1/io2 Multi-Attach)

---

## 2.2 EBS Volume Types

### SSD-Backed Volumes (for IOPS-sensitive workloads)

| Type    | Name                   | Use Case                                | Max IOPS | Max Throughput |
| ------- | ---------------------- | --------------------------------------- | -------- | -------------- |
| **gp3** | General Purpose SSD v3 | Most workloads, boot volumes            | 16,000   | 1,000 MB/s     |
| **gp2** | General Purpose SSD v2 | Older default, being replaced by gp3    | 16,000   | 250 MB/s       |
| **io2** | Provisioned IOPS SSD   | Critical databases (Oracle, SQL Server) | 64,000   | 1,000 MB/s     |
| **io1** | Provisioned IOPS SSD   | High-performance databases              | 64,000   | 1,000 MB/s     |

### HDD-Backed Volumes (for throughput-sensitive workloads)

| Type    | Name                     | Use Case                             | Max Throughput |
| ------- | ------------------------ | ------------------------------------ | -------------- |
| **st1** | Throughput Optimized HDD | Big data, log processing, Kafka      | 500 MB/s       |
| **sc1** | Cold HDD                 | Archival, infrequently accessed data | 250 MB/s       |

> 💡 **Rule of thumb:** Use `gp3` for most things. Use `io2` for production databases. Use `st1` for big sequential reads/writes.

---

## 2.3 EBS Snapshots

A **snapshot** is a point-in-time backup of an EBS volume, stored in **Amazon S3** (managed by AWS).

```
EBS Volume  ──── Snapshot ────► S3 (Managed by AWS)
                    │
                    ├── Restore to a new EBS Volume (same or different AZ/Region)
                    ├── Copy to another Region
                    └── Share with another AWS Account
```

---

## 2.4 EBS Encryption

- EBS volumes can be **encrypted at rest** using **AWS KMS** keys
- Encryption is **transparent** - no code changes needed
- Snapshots of encrypted volumes are also encrypted
- You can set account-level default: "Always encrypt new EBS volumes"

---

## 2.5 🖥️ DEMO - Create and Attach an EBS Volume to EC2

> **Prerequisites:** An EC2 instance running in your account (any Linux AMI)

---

### Demo Part A: Launch an EC2 Instance (if not already running)

**Step 1:** Go to `EC2 → Instances → Launch Instance`

**Step 2:** Configure the instance:

```
Name:           demo-server
AMI:            Amazon Linux 2023 (free tier eligible)
Instance Type:  t2.micro
Key Pair:       Create new → name it "demo-key" → Download .pem file
Network:        Default VPC, default subnet
Security Group: Allow SSH (port 22) from your IP
Storage:        Leave default (8 GB gp3 root volume)
```

**Step 3:** Click **Launch Instance** → Wait for status to show `running`

---

### Demo Part B: Create a New EBS Volume

**Step 1:** Go to `EC2 → Elastic Block Store → Volumes → Create Volume`

**Step 2:** Configure the new volume:

```
Volume Type:        gp3
Size:               10 GiB
Availability Zone:  ⚠️ MUST be the SAME AZ as your EC2 instance
                    (e.g., ap-southeast-1a)
Encryption:         Leave default (or enable for demo)
```

**Step 3:** Click **Create Volume** → Volume state shows `available`

---

### Demo Part C: Attach the Volume to EC2

**Step 1:** Select your new volume → **Actions → Attach Volume**

**Step 2:** Choose your EC2 instance from the dropdown  
**Step 3:** Device name: leave as `/dev/sdf`  
**Step 4:** Click **Attach** → Volume state changes to `in-use`

---

### Demo Part D: Format and Mount the Volume (SSH into EC2)

**Connect to EC2 via SSH:**

```bash
ssh -i "demo-key.pem" ec2-user@<your-ec2-public-ip>
```

**Step 1: Verify the disk is attached**

```bash
lsblk
# You should see nvme1n1 (your new 10 GB disk) listed
```

**Step 2: Format the volume with ext4 filesystem**

```bash
sudo mkfs -t ext4 /dev/nvme1n1
```

**Step 3: Create a mount directory**

```bash
sudo mkdir /mydata
```

**Step 4: Mount the volume**

```bash
sudo mount /dev/nvme1n1 /mydata
```

**Step 5: Verify the mount**

```bash
df -h
# You should see /mydata mounted with 10 GB available
```

**Step 6: Write a test file**

```bash
echo "Hello from EBS!" | sudo tee /mydata/test.txt
cat /mydata/test.txt
```

**Step 7: Make the mount persist after reboot (optional)**

```bash
# Get the UUID of your volume
sudo blkid /dev/nvme1n1

# Edit /etc/fstab (replace UUID with your actual UUID)
echo "UUID=<your-uuid>  /mydata  ext4  defaults,nofail  0  2" | sudo tee -a /etc/fstab
```

```
✅ DEMO RESULT:
   - New 10 GB EBS volume created and attached to EC2
   - Volume formatted and mounted at /mydata
   - Data written to the volume persists across reboots
```

---

### Demo Part E: Create a Snapshot

**Step 1:** Go to `EC2 → Volumes` → Select your volume  
**Step 2:** `Actions → Create Snapshot`  
**Step 3:** Add description: `"demo-snapshot-class"`  
**Step 4:** Click **Create Snapshot**

Go to `EC2 → Snapshots` to see it being created.

> 💡 **Point out:** This snapshot can now restore a new EBS volume in ANY Availability Zone or even another Region!

---

## 2.6 EBS Key Points - Summary

```
✅ EBS = Block storage for EC2 (like a hard drive)
✅ Persists independently from EC2 instance lifecycle
✅ Lives in ONE Availability Zone
✅ gp3 is the recommended default volume type
✅ Snapshots = incremental backups stored in S3
✅ You are BILLED for provisioned GB even if the disk is mostly empty
✅ DETACH volumes before deleting instances to save them
```

---

---

# SECTION 3 - Amazon EFS (Elastic File System)

## 3.1 What is EFS?

**Amazon EFS (Elastic File System)** is a **fully managed, scalable, shared file system** for use with AWS cloud services and on-premises resources.

Think of it like a **shared network drive (NFS)** that multiple EC2 instances can access simultaneously.

```
┌──────────────────────────────────────────────────────────┐
│                      Amazon EFS                          │
│                 (Shared File System)                     │
└──────────────┬──────────────────────┬────────────────────┘
               │                      │
    ┌──────────▼────────┐  ┌──────────▼────────┐
    │   EC2 Instance A  │  │   EC2 Instance B  │
    │   (AZ: us-east-1a)│  │   (AZ: us-east-1b)│
    └───────────────────┘  └───────────────────┘
```

---

## 3.2 EFS vs EBS - Side-by-Side Comparison

| Feature                 | EBS                            | EFS                                 |
| ----------------------- | ------------------------------ | ----------------------------------- |
| **Type**                | Block storage                  | File storage (NFS)                  |
| **Scope**               | Single Availability Zone       | Multiple AZs (Regional)             |
| **Simultaneous Access** | 1 EC2 instance (usually)       | Thousands of EC2 instances          |
| **Scaling**             | Manual (you choose GB upfront) | Automatic (grows/shrinks with data) |
| **Performance Mode**    | IOPS-focused                   | Throughput or IOPS                  |
| **Cost Model**          | Per GB provisioned             | Per GB stored                       |
| **Use Case**            | OS disk, databases             | Shared content, CMS, big data       |
| **Protocol**            | Block device                   | NFS v4.1                            |
| **OS Support**          | Linux & Windows                | Linux only                          |

---

## 3.3 EFS Storage Classes

EFS automatically moves files between storage classes to optimize cost:

| Storage Class   | Use Case                         | Cost                      |
| --------------- | -------------------------------- | ------------------------- |
| **Standard**    | Actively accessed files          | Highest                   |
| **Standard-IA** | Infrequent access (30+ days old) | ~92% cheaper              |
| **One Zone**    | Single AZ, active files          | 47% cheaper than Standard |
| **One Zone-IA** | Single AZ, infrequent access     | Cheapest option           |

> 💡 Enable **EFS Lifecycle Management** to automatically move files to IA after 7, 14, 30, 60, or 90 days.

---

## 3.4 EFS Performance Modes

| Mode                | When to Use                                                |
| ------------------- | ---------------------------------------------------------- |
| **General Purpose** | Default. Best for web servers, CMS, home directories       |
| **Max I/O**         | Highly parallelized workloads (big data, media processing) |

---

## 3.5 EFS Throughput Modes

| Mode                      | Description                                           |
| ------------------------- | ----------------------------------------------------- |
| **Elastic (recommended)** | Automatically scales throughput up/down with workload |
| **Provisioned**           | Set a fixed throughput regardless of storage size     |
| **Bursting**              | Scales with file system size (legacy default)         |

---

## 3.6 🖥️ DEMO - Create and Mount an EFS File System

---

### Demo Part A: Create EFS File System

**Step 1:** Go to `Services → EFS → Create File System`

**Step 2:** Click **Customize** for full options:

```
Name:               demo-efs
Storage Class:      Standard
Lifecycle Policy:   30 days (move to IA after 30 days)
Performance Mode:   General Purpose
Throughput Mode:    Elastic
Encryption:         Enable (AES-256)
```

**Step 3:** Click **Next → Configure Network Access**

```
VPC:            Your default VPC
Mount Targets:  One per AZ (auto-created)
Security Group: Create or select one that allows NFS (port 2049)
```

**Step 4:** Click through and **Create** → Takes ~30 seconds

---

### Demo Part B: Configure Security Group for NFS

**If you need to create an NFS security group:**

`EC2 → Security Groups → Create Security Group`

```
Name:        efs-sg
Description: Allow NFS access for EFS
Inbound Rule:
  Type:   NFS
  Port:   2049
  Source: Your EC2's security group (or 0.0.0.0/0 for demo)
```

---

### Demo Part C: Mount EFS on EC2 (SSH into your EC2 instance)

**Step 1: Install the EFS mount helper**

```bash
sudo yum install -y amazon-efs-utils
```

**Step 2: Create a mount directory**

```bash
sudo mkdir /shared
```

**Step 3: Get your EFS File System ID**  
Go to `EFS → Your file system` → Copy the **File System ID** (e.g., `fs-0abc1234`)

**Step 4: Mount the EFS file system**

```bash
sudo mount -t efs -o tls fs-0abc1234:/ /shared
```

**Step 5: Verify the mount**

```bash
df -h
# You'll see /shared listed with a huge available size (EFS is elastic!)
```

**Step 6: Write a test file**

```bash
echo "Hello from EFS!" | sudo tee /shared/test.txt
cat /shared/test.txt
```

**Step 7: Make it persist after reboot**

```bash
echo "fs-0abc1234:/ /shared efs defaults,_netdev,tls 0 0" | sudo tee -a /etc/fstab
```

---

### Demo Part D (Optional): Access Same EFS from a Second EC2

To show **shared access**, SSH into a second EC2 instance in a different AZ and repeat Steps 1–4.

```bash
# On the second EC2:
cat /shared/test.txt
# Output: Hello from EFS!

# Write from second EC2:
echo "Hello from EC2-B!" | sudo tee /shared/from-ec2b.txt
```

Go back to your first EC2:

```bash
ls /shared/
# You'll see both files! Real-time shared file system.
```

```
✅ DEMO RESULT:
   - EFS file system created and mounted on EC2
   - Multiple EC2 instances can share the same file system
   - Data automatically available across Availability Zones
```

---

## 3.7 EFS Key Points - Summary

```
✅ EFS = Fully managed shared file system (NFS)
✅ Works across MULTIPLE EC2 instances and AZs simultaneously
✅ Automatically scales storage up and down (no capacity planning)
✅ Linux ONLY (unlike EBS which also supports Windows)
✅ More expensive than EBS per GB - use IA storage classes to cut costs
✅ Great for: CMS (WordPress), shared code repos, data science notebooks
```

---

---

# SECTION 4 - AWS Security Services

## 4.1 The AWS Shared Responsibility Model

Before covering security services, understand WHO is responsible for WHAT:

```
┌─────────────────────────────────────────────────────────┐
│                  YOU ARE RESPONSIBLE FOR                 │
│  (Security IN the Cloud)                                │
│                                                         │
│  • IAM users/roles/policies                             │
│  • Data encryption                                      │
│  • OS-level patching (for EC2)                          │
│  • Network/Security Group configuration                 │
│  • Application security                                 │
├─────────────────────────────────────────────────────────┤
│                AWS IS RESPONSIBLE FOR                   │
│  (Security OF the Cloud)                                │
│                                                         │
│  • Physical data center security                        │
│  • Hardware/hypervisor security                         │
│  • Managed service patching (RDS, Lambda, EFS, etc.)    │
│  • Global network infrastructure                        │
└─────────────────────────────────────────────────────────┘
```

---

## 4.2 IAM - Identity and Access Management

**IAM** is the foundation of AWS security. It controls **who can do what** in your AWS account.

### IAM Core Concepts

```
IAM
│
├── USERS       → Individual people or service accounts
├── GROUPS      → Collections of users (e.g., "Developers", "Admins")
├── ROLES       → Temporary permissions for services or cross-account access
└── POLICIES    → JSON documents defining what actions are allowed/denied
```

### Example IAM Policy (JSON)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

This policy **allows** reading and writing objects in `my-bucket` only.

### IAM Best Practices

```
✅ NEVER use root account for day-to-day tasks
✅ Enable MFA on root account immediately
✅ Grant LEAST PRIVILEGE - only permissions that are needed
✅ Use IAM Roles for EC2 (not hardcoded credentials)
✅ Rotate access keys regularly
✅ Use IAM Groups to manage permissions at scale
```

---

## 4.3 Security Groups vs NACLs

### Security Groups (Instance-level Firewall)

```
┌────────────────────────────────────┐
│           Security Group           │
│                                   │
│  Inbound Rules:                   │
│    Allow TCP 22 (SSH) from My IP  │
│    Allow TCP 80 (HTTP) from 0.0.0.0│
│    Allow TCP 443 (HTTPS) from Any  │
│                                   │
│  Outbound Rules:                  │
│    Allow All traffic              │
└────────────────────────────────────┘
```

- Acts as a **virtual firewall** at the **instance level**
- **Stateful** - if inbound is allowed, response automatically goes out
- Only **ALLOW** rules (no explicit deny)
- Changes take effect **immediately**

### NACLs - Network Access Control Lists (Subnet-level Firewall)

- Acts at the **subnet level** (applies to all instances in the subnet)
- **Stateless** - you must explicitly allow both inbound AND outbound
- Supports both **ALLOW and DENY** rules
- Rules evaluated in **number order** (lowest first)

### Quick Comparison

| Feature    | Security Group             | NACL           |
| ---------- | -------------------------- | -------------- |
| Level      | Instance                   | Subnet         |
| State      | Stateful                   | Stateless      |
| Rules      | Allow only                 | Allow + Deny   |
| Default    | Deny all in, Allow all out | Allow all      |
| Evaluation | All rules checked          | Rules in order |

---

## 4.4 AWS GuardDuty

**GuardDuty** is an **intelligent threat detection service** that continuously monitors your AWS account for malicious activity.

### What It Monitors

- **CloudTrail Logs** - Unusual API calls, unauthorized deployments
- **VPC Flow Logs** - Suspicious network traffic, crypto-mining traffic
- **DNS Logs** - Communication with known malicious domains
- **S3 Logs** - Unusual data access patterns

### Threat Categories GuardDuty Detects

```
🔴 HIGH SEVERITY:
   - Unauthorized access from Tor exit nodes
   - Cryptocurrency mining activity detected
   - Instance communicating with known malware C&C servers

🟡 MEDIUM SEVERITY:
   - Brute force attacks on EC2 instances
   - Unusual API calls from unfamiliar locations
   - Disabled CloudTrail logging (suspicious behavior)

🟢 LOW SEVERITY:
   - Port scanning from EC2 instances
   - Unusual S3 access patterns
```

> 💡 GuardDuty runs **without agents** - it analyzes existing AWS logs. 30-day free trial available.

---

## 4.5 AWS Shield - DDoS Protection

**AWS Shield** protects AWS resources from **Distributed Denial of Service (DDoS) attacks.**

| Tier                | Cost             | Protection                                                         |
| ------------------- | ---------------- | ------------------------------------------------------------------ |
| **Shield Standard** | FREE (automatic) | Layer 3 & 4 DDoS protection for all AWS resources                  |
| **Shield Advanced** | ~$3,000/month    | Layer 7 protection, 24/7 DDoS Response Team (DRT), cost protection |

Shield Standard protects:

- Amazon CloudFront
- Amazon Route 53
- AWS Global Accelerator
- Elastic Load Balancer

---

## 4.6 AWS WAF - Web Application Firewall

**AWS WAF** protects web applications from common **Layer 7 (application-layer) attacks.**

### What WAF Blocks

```
Common Attacks WAF Protects Against:
├── SQL Injection (SQLi)      → Malicious SQL in web requests
├── Cross-Site Scripting (XSS) → Injected JavaScript attacks
├── Bad Bots                  → Scrapers, credential stuffing
├── Rate Limiting             → Too many requests from one IP
└── Geo-Blocking              → Block entire countries
```

### How WAF Works

```
User Request
    │
    ▼
[ AWS WAF ] ── Rules evaluated
    │
    ├── ✅ ALLOW → Request passes to your application
    └── 🚫 BLOCK → 403 Forbidden returned immediately
```

WAF integrates with: **CloudFront, Application Load Balancer, API Gateway, AppSync**

---

## 4.7 AWS KMS - Key Management Service

**KMS** allows you to **create and control encryption keys** used to protect your data.

```
Your Data ──► KMS Encrypts ──► Encrypted Data stored in S3/EBS/RDS

To read:
Encrypted Data ──► KMS Decrypts (if you have permission) ──► Plain Data
```

### KMS Key Types

| Key Type                        | Description                                                    |
| ------------------------------- | -------------------------------------------------------------- |
| **AWS Managed Keys**            | Free, auto-rotated, managed by AWS (e.g., `aws/s3`, `aws/ebs`) |
| **Customer Managed Keys (CMK)** | You create and control; $1/month per key                       |
| **Custom Key Store**            | Keys stored in your own CloudHSM hardware                      |

### Where KMS Is Used

- EBS volume encryption
- S3 server-side encryption (SSE-KMS)
- RDS database encryption
- Secrets Manager (secrets encrypted with KMS)
- CloudTrail log encryption

---

## 4.8 AWS CloudTrail

**CloudTrail** records **all API calls** made in your AWS account - it's your audit log.

```
Any Action in AWS
      │
      ▼
  CloudTrail records:
  ┌─────────────────────────────────┐
  │  Who made the call (user/role)  │
  │  What action was taken          │
  │  When it happened (timestamp)   │
  │  From where (IP address)        │
  │  Was it successful or denied    │
  └─────────────────────────────────┘
      │
      ▼
  Stored in S3 / CloudWatch Logs
```

> ✅ CloudTrail is **enabled by default** for the last 90 days. Enable a **Trail** to keep logs permanently in S3.

---

## 4.9 🖥️ DEMO - IAM: Create a User with Limited Permissions

---

### Demo Part A: Create an IAM User

**Step 1:** Go to `IAM → Users → Create User`

**Step 2:** Configure:

```
User Name:          demo-student
AWS Console Access: Enable ✅
Password:           Custom → "TempPassword123!"
Require reset:      ✅ (user must change on first login)
```

**Step 3:** Set Permissions - Select **"Attach policies directly"**  
Search and attach: `AmazonS3ReadOnlyAccess`

**Step 4:** Review and **Create User**

**Step 5:** Copy the **Console Sign-in URL** shown on the success screen

---

### Demo Part B: Test the Limited Permissions

**Step 1:** Open a **private/incognito browser window**

**Step 2:** Go to the sign-in URL → Log in as `demo-student`

**Step 3:** Try to access S3:

```
✅ Should SUCCEED: Browsing S3 buckets (read access)
```

**Step 4:** Try to create an EC2 instance:

```
🚫 Should FAIL: "You are not authorized to perform this action"
```

**Step 5:** Try to access IAM:

```
🚫 Should FAIL: No IAM permissions granted
```

```
✅ DEMO RESULT:
   - IAM User created with restricted S3 read-only access
   - User can browse S3 but cannot perform any other AWS actions
   - This demonstrates the Principle of Least Privilege in action
```

---

### Demo Part C: Enable MFA on an IAM User (Optional)

**Step 1:** Log back in as admin → Go to `IAM → Users → demo-student`

**Step 2:** Go to the **Security Credentials** tab

**Step 3:** Click **Assign MFA Device**

```
MFA Device Type: Authenticator App
```

**Step 4:** Scan the QR code with Google Authenticator or Authy

**Step 5:** Enter two consecutive 6-digit codes → **Add MFA**

```
✅ DEMO RESULT:
   - MFA now required for this user to log in
   - Even if password is stolen, account is protected
```

---

## 4.10 🖥️ DEMO - Enable GuardDuty (5-Minute Setup)

**Step 1:** Go to `Services → GuardDuty → Get Started`

**Step 2:** Click **Enable GuardDuty** (30-day free trial starts)

**Step 3:** View the dashboard:

```
GuardDuty Dashboard shows:
├── Findings (threats detected)
├── Severity breakdown (High / Medium / Low)
└── Resources at risk
```

**Step 4:** Explore sample findings (optional):

```
Settings → Generate Sample Findings
```

This creates **fake findings** across all categories so you can explore what real alerts look like without any actual threat.

```
✅ DEMO RESULT:
   - GuardDuty enabled and monitoring your account
   - Continuously analyzes CloudTrail, VPC Flow Logs, and DNS logs
   - No agents needed - fully managed threat detection
```

---

## 4.11 Security Services - Quick Reference

| Service             | What It Does                          | Key Use Case                    |
| ------------------- | ------------------------------------- | ------------------------------- |
| **IAM**             | Controls who can do what              | User/role/permission management |
| **Security Groups** | Instance-level firewall (allow rules) | Control EC2 network access      |
| **NACLs**           | Subnet-level firewall (allow + deny)  | Broad network control           |
| **GuardDuty**       | Threat detection (AI-powered)         | Detect compromised instances    |
| **Shield**          | DDoS protection                       | Protect web apps from attacks   |
| **WAF**             | Web app firewall (L7)                 | Block SQLi, XSS, bots           |
| **KMS**             | Encryption key management             | Encrypt EBS, S3, RDS data       |
| **CloudTrail**      | API audit logs                        | Who did what, when              |

---

---

# Recap

## What We Covered Today

### AWS Billing

- Pay-as-you-go model and Free Tier
- Billing Dashboard, Cost Explorer, Budgets
- EC2 pricing models (On-Demand, Reserved, Spot)
- How to set billing alerts to avoid surprise charges

### EBS - Elastic Block Store

- Block storage for EC2 (like a hard drive)
- Volume types: gp3, io2, st1, sc1
- Snapshots for backup and recovery
- **Demo:** Create, attach, format, and mount an EBS volume

### EFS - Elastic File System

- Shared NFS file system for multiple EC2 instances
- Automatically scales, spans multiple AZs
- Lifecycle policies to save costs
- **Demo:** Create EFS, mount on EC2, share files across instances

### Security Services

- IAM: Users, Groups, Roles, Policies - least privilege principle
- Security Groups vs NACLs
- GuardDuty, Shield, WAF, KMS, CloudTrail
- **Demo:** Create limited IAM user + Enable GuardDuty

---

## Cleanup Checklist (To Avoid Charges!)

```
After class, make sure to:

[ ] Terminate any EC2 instances created during demos
[ ] Delete EBS volumes that are no longer needed
[ ] Delete EFS file systems
[ ] Remove IAM demo users
[ ] Disable GuardDuty if no longer needed
    (GuardDuty → Settings → Suspend/Disable)
[ ] Verify in Billing → Bills that no unexpected charges appear
```
