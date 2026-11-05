# Week 10 - AWS Security, Terraform, Docker & ECS

**A ground-up class: from "what is a security group" to "I just deployed a running container on ECS using Terraform."**

---

# Part 0 - Environment Setup

### 0.1 AWS Account & IAM User (not root!)

Never use the AWS root account for daily work. Create an IAM user:

1. AWS Console → IAM → Users → Create user
2. Attach policy `AdministratorAccess` (fine for a training/sandbox account - **not** for production)
3. Create an **Access Key** (IAM → Security credentials → Access keys → "Command Line Interface (CLI)")
4. Save the Access Key ID + Secret Access Key somewhere safe (shown only once)

### 0.2 Install & configure AWS CLI (Windows)

Open **PowerShell as Administrator**:

```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

> 💡 Alternative: download and double-click the installer directly from **awscli.amazonaws.com/AWSCLIV2.msi** if you prefer a GUI install. Either way, restart PowerShell afterward so the `aws` command is picked up on PATH.

Verify and configure:

```powershell
aws --version
aws configure
# AWS Access Key ID: <paste>
# AWS Secret Access Key: <paste>
# Default region name: us-east-1   (or your preferred region)
# Default output format: json
```

Test it works:

```powershell
aws sts get-caller-identity
```

You should see your Account ID, User ID, and ARN printed back. That confirms the CLI can talk to AWS.

### 0.3 Install Terraform (Windows)

**Option A - Chocolatey (fastest, if you already have it):**

```powershell
choco install terraform
```

**Option B - Manual install (no Chocolatey needed):**

1. Download the Windows AMD64 zip from **developer.hashicorp.com/terraform/install**
2. Extract `terraform.exe` into a folder, e.g. `C:\terraform`
3. Add that folder to your **System PATH**:
   - Search "Environment Variables" in Windows Start menu → Edit the system environment variables → Environment Variables → under "System variables" select `Path` → Edit → New → add `C:\terraform`
4. Close and reopen PowerShell so PATH changes take effect

Verify:

```powershell
terraform -version
```

> 💡 If `terraform` isn't recognized after installing, it's almost always a PATH issue - double-check step 3 and restart your terminal (or reboot if it still doesn't pick up).

### 0.4 Install Docker (Windows)

Install **Docker Desktop for Windows** from docker.com.

- Docker Desktop needs a backend to run Linux containers. Choose **WSL 2** as the backend when prompted (recommended over the older Hyper-V backend) - it's faster and is what almost all tutorials/CI assume.
- If WSL 2 isn't installed yet, Docker Desktop will prompt you, or you can set it up beforehand:

```powershell
wsl --install
```

(requires a restart the first time)

- After installing Docker Desktop, launch it once and make sure it says **"Engine running"** in the bottom-left corner before using the CLI.

Verify (from PowerShell or a normal Command Prompt - Docker Desktop makes `docker` available globally):

```powershell
docker --version
docker run hello-world
```

If you see a "Hello from Docker!" message, everything is working.

### 0.5 Editor

VS Code + these extensions (recommended, optional for students):

- **HashiCorp Terraform** (official) - syntax highlighting, formatting
- **Docker** (Microsoft) - Dockerfile linting, image explorer
- **AWS Toolkit** (optional)

---

# Part 1 - AWS Security Services (Concepts)

### 1.1 The Shared Responsibility Model

AWS secures the **cloud** (physical data centers, hardware, network infrastructure).
You secure **what's in the cloud** - your data, your configurations, your access controls.

> This is the single most important mental model in cloud security. AWS will never patch your Security Group misconfiguration for you.

### 1.2 The AWS Security Services Landscape

"AWS security services" specifically refers to a family of **purpose-built, managed services** whose entire job is to detect threats, protect data, and enforce compliance - you turn them on, and AWS's own ML/rules engines do the watching. This is different from _networking primitives_ like Security Groups (those are covered separately in 1.6, since we build one by hand in the project).

| Category                               | Services                           |
| -------------------------------------- | ---------------------------------- |
| **Threat Detection & Monitoring**      | GuardDuty, Detective, Security Hub |
| **Data Protection**                    | Macie, KMS, Secrets Manager        |
| **Vulnerability & Posture Management** | Inspector, Config                  |
| **Network & App Protection**           | WAF, Shield, Network Firewall      |
| **Identity Governance**                | IAM Access Analyzer                |
| **Audit Trail**                        | CloudTrail                         |

We'll go deeper on the two you specifically flagged - **GuardDuty** and **Macie** - since they're the ones students are most likely to actually click through and enable in a sandbox account.

### 1.3 Amazon GuardDuty - Threat Detection

**What it is:** A managed threat-detection service that continuously monitors your AWS account for malicious or unauthorized activity - **no agents to install, no infrastructure to manage.**

**What it watches:**
| Data source | Detects things like |
|---|---|
| VPC Flow Logs | Traffic to known crypto-mining or C2 (command & control) IP addresses |
| DNS logs | Domain lookups associated with malware |
| CloudTrail (management + S3 data events) | Unusual API calls - e.g., root account usage, disabling CloudTrail itself, credential exfiltration patterns |
| EKS audit logs | Suspicious Kubernetes API activity |
| RDS login activity | Anomalous or brute-force login attempts |

**How it works (conceptually):** AWS aggregates threat intelligence feeds (known-bad IPs/domains) with machine learning models trained on billions of events across AWS, then correlates that against _your_ account's activity. When something matches, it raises a **Finding** with a severity (Low/Medium/High) and a plain-English description.

**Example findings a student might see:**

- `UnauthorizedAccess:EC2/MaliciousIPCaller.Custom` - an EC2 instance is talking to a known malicious IP
- `Recon:IAMUser/MaliciousIPCaller` - API calls made from a Tor exit node or known-bad IP
- `CryptoCurrency:EC2/BitcoinTool.B` - an instance is behaving like a crypto-mining node

**Try it live (free - 30-day trial per account):**

1. AWS Console → search "GuardDuty" → **Enable GuardDuty**
2. It starts analyzing immediately; findings appear over the next hours/days as activity accumulates
3. Console → GuardDuty → **Findings** - this is the dashboard students should bookmark

### 1.4 Amazon Macie - Sensitive Data Discovery

**What it is:** A managed service that uses machine learning + pattern matching to **automatically discover and classify sensitive data** stored in Amazon S3 - things like PII (names, SSNs, credit card numbers), credentials, and financial data.

**Why it exists:** Companies often don't actually know where all their sensitive data lives across dozens/hundreds of S3 buckets. Macie scans bucket contents and flags exactly that.

**What Macie can detect out of the box:**

- Personally Identifiable Information (PII) - names, addresses, passport numbers, SSNs
- Financial data - credit card numbers, bank account numbers
- Credentials - AWS keys, private keys accidentally left in files
- Custom data identifiers - regex patterns you define yourself (e.g., an internal employee ID format)

**How it works:**

1. Macie inventories your S3 buckets and flags **bucket-level risks** first (e.g., "this bucket is public," "this bucket is unencrypted") - this part is free and automatic once enabled
2. You then run (or schedule) a **sensitive data discovery job** against specific buckets - this is the part that costs money, since it actually reads object contents
3. Results appear as **Findings**, similar in style to GuardDuty, e.g. `SensitiveData:S3Object/Financial`

**Try it live:**

1. AWS Console → search "Macie" → **Enable Macie**
2. Console → Macie → **S3 buckets** tab - you'll immediately see a risk score per bucket (public access, encryption status) with zero extra cost
3. To go further: **Jobs** → create a one-time job scoped to a _specific_ test bucket with a couple of dummy files (e.g., a `.csv` with fake SSNs) so students see a real finding without scanning your whole account

> ⚠️ **Cost callback:** Macie discovery jobs charge per GB scanned. For a class demo, scope the job to a tiny test bucket (a few KB of dummy data) - don't point it at a real, large bucket, or you'll rack up cost unexpectedly.

> 🎓 **Analogy:** GuardDuty watches _behavior_ ("is someone doing something suspicious right now?"). Macie inspects _content_ ("is there something sensitive sitting somewhere it shouldn't be?"). They're complementary, not overlapping.

### 1.5 Other AWS Security Services (quick tour)

| Service                                   | One-line purpose                                                                                                                                            |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Security Hub**                          | A single dashboard that aggregates findings from GuardDuty, Macie, Inspector, and more - plus runs automated compliance checks (CIS, PCI-DSS benchmarks)    |
| **Inspector**                             | Automated vulnerability scanning for EC2 instances, container images (great pairing with our ECR images later!), and Lambda functions                       |
| **Detective**                             | Visualizes relationships between findings - helps you investigate _why_ GuardDuty flagged something, by graphing related API calls, IPs, and resources      |
| **AWS WAF**                               | A web application firewall - blocks common exploits (SQL injection, XSS) at the edge, before traffic reaches your app                                       |
| **AWS Shield**                            | DDoS protection - Standard tier is free and automatic for everyone; Advanced adds 24/7 DDoS response support                                                |
| **KMS (Key Management Service)**          | Managed encryption keys for data at rest                                                                                                                    |
| **Secrets Manager / SSM Parameter Store** | Store DB passwords, API keys - never hardcode secrets in Terraform or Docker images                                                                         |
| **IAM Access Analyzer**                   | Flags resources (S3 buckets, IAM roles, KMS keys) that are unintentionally shared outside your account                                                      |
| **AWS Config**                            | Continuously records resource configuration changes and checks them against rules you define (e.g., "flag any Security Group open to 0.0.0.0/0 on port 22") |
| **CloudTrail**                            | Logs every API call made in your account - the audit trail that GuardDuty and Detective actually read from                                                  |

### 1.6 Foundational concepts needed for the project

Two pieces we'll actually build with Terraform later - quick grounding now.

**IAM - Identity and Access Management** (the "who can do what" layer):

| Concept    | What it is                                                      | Example                             |
| ---------- | --------------------------------------------------------------- | ----------------------------------- |
| **User**   | A person or service with long-term credentials                  | `intern-devops`                     |
| **Role**   | A temporary identity assumed by AWS services or federated users | `ECS-Task-Execution-Role`           |
| **Policy** | A JSON document defining permissions (allow/deny)               | Attached to users, groups, or roles |

> **Key principle: Least Privilege.** Only grant the permissions actually needed - nothing more. This matters directly in Part 5, where our ECS Task needs an IAM **Role** to pull images from ECR.

**Security Groups vs Network ACLs:**

|            | **Security Group**                                                              | **Network ACL**                                       |
| ---------- | ------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Level      | Instance/ENI level (attached to EC2, ECS task, RDS, etc.)                       | Subnet level                                          |
| State      | **Stateful** - if inbound is allowed, the response is automatically allowed out | **Stateless** - must explicitly allow both directions |
| Rules      | Allow rules only                                                                | Allow **and** Deny rules                              |
| Evaluation | All rules evaluated together                                                    | Rules evaluated in number order                       |

> 🎓 **Analogy:** A Security Group is like a bouncer at _your specific apartment door_ - checks everyone individually. An NACL is like security at the _building's front gate_ - checks everyone entering/leaving the whole building, and can explicitly ban certain people.

This is exactly what we'll build in Terraform in Part 5 - a Security Group allowing inbound traffic to our container's port.

---

# Part 2 - Terraform 101

### 2.1 What is Infrastructure as Code (IaC)?

Instead of clicking around the AWS Console to create a VPC, EC2 instance, or S3 bucket, you **write code** that describes the infrastructure you want. Run that code, and the tool creates it for you - identically, every time.

**Why it matters:**

- **Repeatable** - spin up the exact same environment in seconds (dev, staging, prod)
- **Version-controlled** - infrastructure changes go through Git, PRs, and review, just like app code
- **Documented by default** - the code _is_ the documentation of what exists
- **Safe** - you can preview changes before they happen (`terraform plan`)

### 2.2 Terraform vs alternatives (brief)

| Tool                      | Approach                                                                                             |
| ------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Terraform** (HashiCorp) | Declarative, cloud-agnostic (AWS/Azure/GCP/etc.), uses HCL                                           |
| **AWS CloudFormation**    | Declarative, AWS-only, uses YAML/JSON                                                                |
| **AWS CDK**               | Imperative-ish, AWS-only, uses real programming languages (Python/TS) that compile to CloudFormation |
| **Pulumi**                | Like CDK but multi-cloud                                                                             |

> 🎓 We use Terraform because it's the industry-standard, cloud-agnostic choice - a huge share of real DevOps job postings mention it by name.

### 2.3 The Terraform Workflow

```
   write .tf files
        │
        ▼
 terraform init     →  downloads providers (e.g., the AWS provider plugin)
        │
        ▼
 terraform plan      →  shows what WILL change (dry run, nothing happens yet)
        │
        ▼
 terraform apply     →  actually creates/updates/destroys real AWS resources
        │
        ▼
 terraform destroy   →  tears everything down when you're done
```

### 2.4 HCL Basics (HashiCorp Configuration Language)

Four building blocks you'll see constantly:

**1. Provider** - which cloud/platform Terraform talks to

```hcl
provider "aws" {
  region = "us-east-1"
}
```

**2. Resource** - a real thing Terraform will create

```hcl
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-unique-bucket-name-12345"
}
```

Pattern: `resource "<TYPE>" "<LOCAL_NAME>" { ...config... }`

**3. Variable** - an input, so code isn't hardcoded

```hcl
variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket"
  default     = "my-default-bucket"
}
```

Used elsewhere as `var.bucket_name`.

**4. Output** - a value Terraform prints after apply (useful for grabbing IDs, URLs, IPs)

```hcl
output "bucket_arn" {
  value = aws_s3_bucket.my_bucket.arn
}
```

### 2.5 Your first Terraform example - a single S3 bucket

Create a folder and one file:

```
first-terraform-demo/
└── main.tf
```

`main.tf`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "demo" {
  bucket = "devops-class-demo-bucket-2026" # must be globally unique
}
```

Run it:

```bash
terraform init     # downloads the AWS provider plugin
terraform plan      # shows: "1 to add, 0 to change, 0 to destroy"
terraform apply     # type 'yes' when prompted
```

Go check the AWS Console → S3. The bucket exists. Then:

```bash
terraform destroy   # cleans it up, type 'yes'
```

### 2.6 The State File - `terraform.tfstate`

After `apply`, Terraform creates `terraform.tfstate` - a JSON file that maps your code to the _real_ resources in AWS (their actual IDs). This is how Terraform knows what it created and what needs to change on the next `plan`.

> ⚠️ **Never hand-edit `terraform.tfstate`.** In real teams, this file lives in a remote backend (e.g., an S3 bucket + DynamoDB lock table) so multiple engineers share the same source of truth. For this class, local state (the default) is fine.

### 2.7 Recommended file structure

For anything beyond a one-file demo, split responsibilities:

```
project/
├── main.tf          # resources
├── variables.tf     # input variable declarations
├── outputs.tf        # output declarations
├── providers.tf      # provider + terraform{} block
├── terraform.tfvars  # actual values for variables (often gitignored if secret)
└── .gitignore         # ignore .terraform/, *.tfstate, *.tfvars if sensitive
```

We'll use exactly this structure in the main project (Part 5).

---

# Part 3 - Docker 101

### 3.1 The problem Docker solves

"It works on my machine" - different OS, different library versions, missing dependencies. Docker packages an application **and everything it needs to run** (code, runtime, libraries, system tools) into one portable unit called a **container**.

### 3.2 Container vs Virtual Machine

|           | Virtual Machine               | Container                                               |
| --------- | ----------------------------- | ------------------------------------------------------- |
| Includes  | Full guest OS + app           | Just the app + its dependencies (shares host OS kernel) |
| Boot time | Minutes                       | Seconds (often <1s)                                     |
| Size      | GBs                           | MBs typically                                           |
| Isolation | Very strong (separate kernel) | Process-level isolation                                 |

### 3.3 Core vocabulary

| Term           | Meaning                                                     |
| -------------- | ----------------------------------------------------------- |
| **Image**      | A read-only template/blueprint (e.g., "python:3.12-slim")   |
| **Container**  | A running (or stopped) _instance_ of an image               |
| **Dockerfile** | A text recipe describing how to build an image              |
| **Registry**   | Where images are stored/shared (Docker Hub, or AWS **ECR**) |

### 3.4 Essential Docker commands

```bash
docker pull nginx              # download an image from a registry
docker images                   # list images on your machine
docker run -d -p 8080:80 nginx  # run a container, map host port 8080 → container port 80
docker ps                       # list running containers
docker ps -a                    # list ALL containers (including stopped)
docker stop <container_id>      # stop a running container
docker rm <container_id>        # remove a stopped container
docker logs <container_id>       # view container output/logs
docker exec -it <container_id> sh   # get a shell inside a running container
```

Try it live:

```bash
docker run -d -p 8080:80 --name my-nginx nginx
```

Open `http://localhost:8080` in a browser - nginx's welcome page. Then:

```bash
docker stop my-nginx
docker rm my-nginx
```

### 3.5 Writing your own Dockerfile

Let's containerize a tiny web app so students build something themselves before we get to ECS.

Folder structure:

```
docker-demo/
├── app.py
├── requirements.txt
└── Dockerfile
```

`app.py` (a minimal Flask app):

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from inside a Docker container! 🐳"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

`requirements.txt`:

```
flask==3.0.3
```

`Dockerfile`:

```dockerfile
# 1. Start from a small official base image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependency file first (layer caching optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code
COPY . .

# 5. Document which port the container listens on
EXPOSE 5000

# 6. The command that runs when the container starts
CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t my-flask-app .
docker run -d -p 5000:5000 --name flask-demo my-flask-app
```

Visit `http://localhost:5000` → see the message.

```bash
docker logs flask-demo     # see Flask's request logs
docker stop flask-demo && docker rm flask-demo
```

This exact Flask app (or a similar tiny container) is what we'll push to **ECR** and run on **ECS** in Part 5 - so keep this folder, we're reusing it.

---

# Part 4 - Amazon ECS Concepts (Before We Build)

ECS = **Elastic Container Service** - AWS's own service for running containers at scale, without you having to manage the underlying servers (if you choose Fargate).

### 4.1 The core building blocks

| Concept                              | What it is                                                                                                          |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **ECR** (Elastic Container Registry) | Where your Docker images live in AWS (like Docker Hub, but private & AWS-native)                                    |
| **Cluster**                          | A logical grouping of resources where your containers run                                                           |
| **Task Definition**                  | A blueprint - "run this image, with this much CPU/memory, on this port" (like a Dockerfile, but for ECS scheduling) |
| **Task**                             | One running instance of a Task Definition (like a container instance)                                               |
| **Service**                          | Keeps a specified number of Tasks running continuously; restarts them if they crash                                 |

### 4.2 Fargate vs EC2 launch type

|                   | **Fargate**                       | **EC2 launch type**                                 |
| ----------------- | --------------------------------- | --------------------------------------------------- |
| Server management | None - fully serverless           | You manage the EC2 instances (patching, scaling)    |
| Billing           | Pay per task (vCPU/memory used)   | Pay for the EC2 instances regardless of utilization |
| Best for          | Most modern workloads, simplicity | Fine-grained control, cost optimization at scale    |

> 🎓 We'll use **Fargate** in the project - it removes an entire layer of infrastructure management, which is perfect for a first ECS deployment.

### 4.3 How it all connects (the mental model for Part 5)

```
 Docker image (built locally)
        │  docker push
        ▼
   ECR repository  (image storage)
        │  referenced by
        ▼
  Task Definition   (CPU, memory, container port, image URI, IAM execution role)
        │  run by
        ▼
   ECS Service  (desired count = 1, keeps it alive)
        │  runs inside
        ▼
   ECS Cluster  (Fargate)
        │  network access controlled by
        ▼
   Security Group  (e.g., allow inbound TCP 5000 from anywhere)
        │  inside
        ▼
        VPC / Subnets
```

This is _exactly_ the order we build things in Part 5.

---

# Part 5 - THE PROJECT: Provisioning AWS Infra with Terraform

**Goal:** Using Terraform, provision a **Security Group**, an **ECR repository**, an **ECS Fargate Cluster + Service**, then build our Docker image from Part 3, push it to ECR, and see it running live on AWS.

### 5.1 Why we do this in two phases

Terraform will create the **ECR repository** before any image exists in it. Our ECS **Task Definition** needs to reference an image that's _already pushed_. So we apply in two small phases:

- **Phase A:** Terraform creates the ECR repo (+ IAM role + Security Group) → we push our Docker image →
- **Phase B:** Terraform creates the ECS Cluster/Task/Service referencing that now-existing image.

This mirrors how real CI/CD pipelines work: infra pipeline creates ECR, app pipeline builds & pushes, infra pipeline (or a second Terraform apply) deploys the service.

### 5.2 Final file structure

```
ecs-terraform-project/
├── providers.tf
├── variables.tf
├── data.tf
├── security_group.tf
├── ecr.tf
├── iam.tf
├── ecs.tf
├── outputs.tf
└── terraform.tfvars
```

Also reuse the Docker app from Part 3 (`app.py`, `requirements.txt`, `Dockerfile`) - copy that folder in alongside, or keep it as a sibling project folder.

---

### 5.3 `providers.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

### 5.4 `variables.tf`

```hcl
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefix used for naming all resources"
  type        = string
  default     = "devops-class-app"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 5000
}

variable "image_tag" {
  description = "Docker image tag to deploy (set this AFTER pushing to ECR)"
  type        = string
  default     = "latest"
}
```

### 5.5 `terraform.tfvars`

```hcl
aws_region     = "us-east-1"
project_name   = "devops-class-app"
container_port = 5000
image_tag      = "latest"
```

### 5.6 `data.tf` - use the account's default VPC (keeps scope class-friendly)

```hcl
# Reuse the default VPC & its subnets instead of building networking from scratch -
# keeps this class focused on ECS/Security Groups/ECR, not VPC design.
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
```

> 🎓 **Note:** In production, you'd design a custom VPC with public/private subnets, NAT gateways, etc. We use the default VPC here purely to keep the lesson focused - call this out so nobody thinks this is production-grade networking.

### 5.7 `security_group.tf`

```hcl
resource "aws_security_group" "ecs_service_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow inbound traffic to the containerized app"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "App traffic"
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # class demo only - restrict this in real environments
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}
```

### 5.8 `ecr.tf`

```hcl
resource "aws_ecr_repository" "app_repo" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-ecr"
  }
}
```

### 5.9 `iam.tf` - the role ECS needs to pull images & write logs

```hcl
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
```

### 5.10 `ecs.tf`

```hcl
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 3
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                       = "256"  # 0.25 vCPU
  memory                    = "512"  # 512 MB
  execution_role_arn        = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-container"
      image     = "${aws_ecr_repository.app_repo.repository_url}:${var.image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "app_service" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true # public subnet in default VPC → task gets a public IP
  }
}
```

### 5.11 `outputs.tf`

```hcl
output "ecr_repository_url" {
  description = "Push your Docker image here"
  value       = aws_ecr_repository.app_repo.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app_service.name
}
```

---

### 5.12 Phase A - create ECR + IAM + Security Group only

Comment out (or temporarily move elsewhere) the contents of `ecs.tf` for this first pass - we only want the ECR repo to exist so we have somewhere to push the image.

```bash
terraform init
terraform plan
terraform apply
```

Note the `ecr_repository_url` output, e.g.:

```
ecr_repository_url = "123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-class-app"
```

### 5.13 Build & push the Docker image to ECR

From the Part 3 Docker app folder:

```bash
1. Build the image
docker build -t devops-class-app .

2. Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 050752629903.dkr.ecr.us-east-1.amazonaws.com

3. Tag it for ECR
docker tag devops-class-app:latest 050752629903.dkr.ecr.us-east-1.amazonaws.com/devops-class-app:latest

4. Push
docker push 050752629903.dkr.ecr.us-east-1.amazonaws.com/devops-class-app:latest
```

> Replace `123456789012...` with your actual `ecr_repository_url` output value.

Confirm in AWS Console → ECR → your repo → you should see the `latest` image tag.

### 5.14 Phase B - deploy the ECS cluster/service

Uncomment `ecs.tf` back in, then:

```bash
terraform plan
terraform apply
```

Terraform will create: CloudWatch log group → Task Definition (pointing at the image you just pushed) → ECS Cluster → ECS Service (which schedules a Task using that Task Definition on Fargate, inside the Security Group we made in Phase A).

### 5.15 Verify it's running

**AWS Console:** ECS → Clusters → `devops-class-app-cluster` → Services → `devops-class-app-service` → Tasks tab → click the running task → find its **Public IP** under the "Configuration" section (ENI attachment).

**Or via CLI:**

```bash
aws ecs list-tasks --cluster devops-class-app-cluster
aws ecs describe-tasks --cluster devops-class-app-cluster --tasks <task-arn>
```

Look for the `networkInterfaces` → `privateIpv4Address`, then cross-reference the ENI in the EC2 Console → Network Interfaces to find the associated **public IP**.

Visit `http://<public-ip>:5000` in a browser →

```
Hello from inside a Docker container! 🐳
```

---

# Part 6 - Cleanup & Wrap-Up

### 6.1 Tear everything down (important - avoid surprise AWS bills)

```bash
terraform destroy
```

Review the plan carefully, type `yes`. This removes the ECS Service, Cluster, Task Definition, IAM Role, Security Group, and ECR repository (and any images inside it, since we didn't set deletion protection).

> ⚠️ If `destroy` fails on the ECR repo because it still contains images, either delete the images manually first (ECR Console → repo → select image → Delete) or add `force_delete = true` to the `aws_ecr_repository` resource before re-running destroy.

### 6.2 Recap - what students actually learned

- **AWS Security:** IAM users/roles/policies, least privilege, Security Groups vs NACLs
- **Terraform:** IaC concepts, HCL syntax (provider/resource/variable/output), the init→plan→apply→destroy loop, state files, file structuring
- **Docker:** images vs containers, Dockerfile authoring, build/run/push workflow, layer caching
- **ECS:** Cluster/Task Definition/Task/Service model, Fargate vs EC2 launch type, how it all wires together with ECR + IAM + Security Groups
- **A real, working deployment** they can point to and explain end-to-end

---

## Appendix - Full command cheat-sheet

```bash
# AWS CLI
aws configure
aws sts get-caller-identity

# Terraform
terraform init
terraform plan
terraform apply
terraform destroy
terraform fmt        # auto-format .tf files
terraform validate   # check syntax without touching AWS

# Docker
docker build -t <name> .
docker run -d -p <host_port>:<container_port> --name <name> <image>
docker ps
docker logs <container>
docker stop <container> && docker rm <container>

# ECR + Docker
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag <local-image>:latest <ecr-url>:latest
docker push <ecr-url>:latest

# ECS
aws ecs list-clusters
aws ecs list-services --cluster <cluster-name>
aws ecs list-tasks --cluster <cluster-name>
aws ecs describe-tasks --cluster <cluster-name> --tasks <task-arn>
```
