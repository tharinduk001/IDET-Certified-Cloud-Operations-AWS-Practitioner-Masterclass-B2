# DAY 05

---

# PART 1 - HIGH AVAILABILITY: ELB & AUTO SCALING
## Scaling
### Vertical Scaling (Scale Up/Down)
- Add more CPU/RAM to an existing EC2 instance
- _Example: t3.micro → t3.xlarge_
- Simple, no code changes needed


**Problems**

Has a ceiling - you can't go beyond the biggest instance type.

Single point of failure - if that one instance dies, everything dies  

Requires downtime to resize

---

### **Horizontal Scaling (Scale Out/In) **
- Add more EC2 instances to handle load 
- Virtually unlimited scale 
- No single point of failure 
- Can scale in and out automatically (cost-efficient) 


**Problems**

Application needs to be designed to be stateless



---

## Load Balancing
| Type | Best For  | Layer |
| ----- | ----- | ----- |
| Application Load Balancer (ALB) | HTTP/HTTPS, web apps, microservices | Layer 7 |
| Network Load Balancer (NLB)  | Ultra-high performance, TCP/UDP  | Layer 4 |
| Gateway Load Balancer (GWLB) | Firewalls, deep packet inspection | Layer 3 |


We are using ALB today because: 

- It understands HTTP - can route based on URL paths  (/api/* → server A, /images/* → server B)
- Has built-in health checks - automatically stops sending traffic to unhealthy instances 
- Supports SSL termination 


Key ALB components:

- Listener - watches for incoming requests on a port (e.g. port 80) 
- Target Group - a group of EC2 instances to receive traffic 
- Health Check - ALB regularly pings each instance; if it fails, traffic stops going to it 
---

##  Auto Scaling Groups (ASG)
1. You define a Launch Template - the blueprint for new instances (AMI, instance type, user data) 

2. You set Min / Desired / Max capacity (e.g. min=2, desired=2, max=5) 

3. You attach scaling policies - rules that trigger scaling (e.g. "when CPU > 70% for 2 minutes, add 1 instance") 

4. ASG registers new instances with the ALB Target Group automatically



```
  ﻿Internet
     │
     ▼
[Application Load Balancer]   ← single entry point, distributes traffic
     │         │
     ▼         ▼
  [EC2-1]   [EC2-2]           ← target group (managed by ASG)
               ↑
         [EC2-3 added]        ← ASG adds this when CPU spikes 
```
# ALB + Auto Scaling Group [DEMO]
## Phase 1: Launch Two EC2 Instances
### Step 1: Open EC2 Console
1. Go to AWS Console
2. Search for EC2
3. Open the EC2 Dashboard
4. Click Launch Instances
---

## Step 2: Configure Instance 1
| Setting | Value |
| ----- | ----- |
| Name | `webserver-1`  |
| AMI | Amazon Linux 2023 AMI |
| Instance Type | `t2.micro`  |
| Key Pair | Create/select `demo-keypair`  |
| VPC | Default VPC |
| Subnet | `us-east-1a`  |
| Public IP | Enable |
| Security Group | `webserver-sg`  |
### Security Group Rules
| Type | Port | Source |
| ----- | ----- | ----- |
| HTTP | 80 | 0.0.0.0/0 |
| SSH | 22 | My IP |
### User Data Script
```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<html><h1>Hello from WebServer 1 - $(hostname -f)</h1></html>" > /var/www/html/index.html
```
Click Launch Instance.

---

## Step 3: Configure Instance 2
Repeat the same process with these changes:

| Setting | Value |
| ----- | ----- |
| Name | `webserver-2`  |
| Subnet | `us-east-1b`  |
| Security Group | Existing `webserver-sg`  |
### User Data Script
```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<html><h1>Hello from WebServer 2 - $(hostname -f)</h1></html>" > /var/www/html/index.html
```
Click Launch Instance.

---

## Step 4: Verify Instances
1. Navigate to EC2 → Instances
2. Wait until:
    - Status = Running
    - Health Checks = 2/2 Passed

3. Copy each Public IPv4 address
4. Open them in the browser and verify both web pages
---

# Phase 2: Create a Target Group
## Step 5: Create Target Group
### Navigation
```text
EC2 → Target Groups → Create Target Group
```
### Configuration
| Setting | Value |
| ----- | ----- |
| Target Type | Instances |
| Name | `demo-tg`  |
| Protocol | HTTP |
| Port | 80 |
| VPC | Default VPC |
| Health Check Path | `/`  |
### Register Targets
Select:

- `webserver-1` 
- `webserver-2` 
Then:

1. Click Include as pending below
2. Click Create target group


---

# Phase 3: Create Application Load Balancer
## Step 6: Create ALB
### Navigation
```text
EC2 → Load Balancers → Create Load Balancer
```
Select:

- Application Load Balancer
### Configuration
| Setting | Value |
| ----- | ----- |
| Name | `demo-alb`  |
| Scheme | Internet-facing |
| IP Type | IPv4 |
| VPC | Default VPC |
### Network Mapping
Enable both Availability Zones:

- `us-east-1a` 
- `us-east-1b` 
---

### Security Group
Create:

- `alb-sg` 
### Inbound Rule
| Type | Port | Source |
| ----- | ----- | ----- |
| HTTP | 80 | 0.0.0.0/0 |
---

### Listener Configuration
| Setting | Value |
| ----- | ----- |
| Protocol | HTTP |
| Port | 80 |
| Forward To | `demo-tg`  |
Click Create Load Balancer.



---

# Phase 4: Test the Load Balancer
## Step 7: Verify ALB
1. Open EC2 → Load Balancers
2. Select `demo-alb` 
3. Copy the DNS Name
Example:

```text
demo-alb-1234567890.us-east-1.elb.amazonaws.com
```
1. Open the DNS name in the browser
2. Refresh multiple times
Expected behavior:

- Requests alternate between WebServer 1 and WebServer 2


---

## Live Failure Demo
SSH into one instance:

```bash
sudo systemctl stop httpd
```
Observe:

- ALB health checks fail
- Traffic automatically routes only to the healthy instance
---

# Phase 5: Create Auto Scaling Group
## Step 8: Create Launch Template
### Navigation
```text
EC2 → Launch Templates → Create Launch Template
```
### Configuration
| Setting | Value |
| ----- | ----- |
| Name | `demo-launch-template`  |
| AMI | Amazon Linux 2023 |
| Instance Type | `t2.micro`  |
| Key Pair | `demo-keypair`  |
| Security Group | `webserver-sg`  |
### User Data Script
```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<html><h1>Auto-Scaled Instance - $(hostname -f)</h1></html>" > /var/www/html/index.html
```
Click Create launch template.

---

## Step 9: Create Auto Scaling Group
### Navigation
```text
EC2 → Auto Scaling Groups → Create Auto Scaling Group
```
### Configuration
| Setting | Value |
| ----- | ----- |
| Name | `demo-asg`  |
| Launch Template | `demo-launch-template`  |
| VPC | Default VPC |
| Availability Zones | `us-east-1a`, `us-east-1b`  |
---

### Load Balancing
Select:

- Attach to an existing load balancer
- Choose `demo-tg` 
---

### Group Size
| Setting | Value |
| ----- | ----- |
| Desired Capacity | 2 |
| Minimum Capacity | 1 |
| Maximum Capacity | 4 |
---

### Scaling Policy
| Setting | Value |
| ----- | ----- |
| Policy Type | Target Tracking |
| Metric | Average CPU Utilization |
| Target Value | 50% |
Click through the remaining screens and create the Auto Scaling Group.

## Resources Cleanup
Do this after the demo to avoid AWS charges:

1. **ASG:** EC2 → Auto Scaling Groups → delete `demo-asg` 
2. **ALB:** EC2 → Load Balancers → delete `demo-alb` 
3. **Target Group:** EC2 → Target Groups → delete `demo-tg` 
4. **EC2 Instances:** EC2 → Instances → terminate `webserver-1`  and `webserver-2` 
5. **Launch Template:** EC2 → Launch Templates → delete `demo-launch-template` 

