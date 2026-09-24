
# Day 6 
---
# AMAZON S3 & STORAGE
## The Three Types of Storage
### Storage Comparison
| Feature | Block Storage (EBS) | File Storage (EFS) | Object Storage (S3) |
| ----- | ----- | ----- | ----- |
| Analogy | Hard drive attached to 1 PC | Shared network drive | Infinite filing cabinet |
| Access Type | OS-level block access | Shared file access | Object/key-based access |
| Scalability | Limited | Shared scaling | Virtually unlimited |
| Multi-instance Support | No* | Yes | Yes |
| Latency | Very low | Moderate | Higher |
| Cost | Medium | Higher | Cheapest |
| File System | Yes | Yes | No (flat object structure) |
| Best Use Cases | OS disks, databases | Shared CMS/code | Images, backups, static sites |


---

# Amazon S3 Deep Dive
## Important S3 Facts
- Bucket names must be globally unique
- Single object size limit = 5 TB
- Buckets can store unlimited objects
- S3 is not a traditional file system
- "Folders" are simulated using `/`  in object keys
- S3 provides 99.999999999% durability (11 nines)
- Data is automatically replicated across multiple Availability Zones
---

# S3 Storage Classes
## Storage Classes Comparison
| Storage Class | Use Case | Retrieval Speed | Relative Cost |
| ----- | ----- | ----- | ----- |
| S3 Standard | Frequently accessed data | Instant | $$$ |
| S3 Standard-IA | Infrequently accessed data | Instant | $$ |
| S3 One Zone-IA | Infrequent data tolerant to AZ loss | Instant | $ |
| S3 Glacier Instant | Quarterly archive access | Milliseconds | $ |
| S3 Glacier Flexible | Long-term archives | Minutes to hours | ¢ |
| S3 Glacier Deep Archive | Compliance retention | Up to 12 hours | ¢¢ |
| S3 Intelligent-Tiering | Unknown/changing access | Instant | Automatic |
---

## Real Cost Example
> S3 Standard costs approximately $0.023 per GB/month while Glacier Deep Archive costs approximately $0.00099 per GB/month.

### Example Scenario
- 10 TB old compliance logs
- Standard Storage = ~$235/month
- Glacier Deep Archive = ~$10/month
- 7-year savings ≈ $16,800
---

## Lifecycle Policies
### Example Lifecycle Strategy
```text
After 30 days → Move to Standard-IA
After 90 days → Move to Glacier
After 7 years → Delete automatically
```
---

# S3 Versioning & Security
## S3 Versioning
### Features
- Stores every version of an object
- Protects against accidental deletion
- Protects against overwrites
- Delete operations create delete markers
- Older versions can be restored anytime
---

## S3 Security Layers
| Security Layer | Purpose |
| ----- | ----- |
| Bucket Policies | Define bucket-level permissions |
| ACLs | Legacy permission model |
| Block Public Access | Prevent accidental public exposure |
| IAM Policies | Control user/role access |
| Encryption | Encrypt data at rest and in transit |
---

# S3 Static Website Hosting [DEMO]
## Goal
Create:

- An S3 bucket
- Static website hosting
- Public access policy
- Versioned object storage
---

# Phase 1 - Create the S3 Bucket
## Step 1: Navigate to S3
### Navigation
```text
AWS Console → Search S3 → Open S3 Console
```
Click:

- Create Bucket
---

## Step 2: Configure Bucket
| Setting | Value |
| ----- | ----- |
| Bucket Name | `demo-static-website-[yourname]-2024`  |
| Region | us-east-1 or closest region |
| Object Ownership | ACLs Disabled |
| Block Public Access | Disable "Block all public access" |
| Versioning | Enable |
### Important Notes
- Bucket names must be globally unique
- Use lowercase letters, numbers, and hyphens only
- Confirm acknowledgement warning for public access
Click Create Bucket.



---

# Phase 2 - Create and Upload Website Files
## Step 3: Create index.html
### index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My AWS Static Website</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #232f3e, #ff9900);
            color: white;
            text-align: center;
        }
        .container {
            background: rgba(0,0,0,0.4);
            padding: 40px;
            border-radius: 12px;
        }
        h1 { font-size: 2.5rem; margin-bottom: 10px; }
        p  { font-size: 1.2rem; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Hello from Amazon S3!</h1>
        <p>This static website is hosted entirely on S3.</p>
        <p>No servers. No EC2. No maintenance.</p>
        <p><strong>AWS Training Demo — Day 2</strong></p>
    </div>
</body>
</html>
```
---

## Create error.html
```html
<!DOCTYPE html>
<html>
<head><title>Page Not Found</title></head>
<body>
    <h1>404 - Page Not Found</h1>
    <p><a href="index.html">Go Home</a></p>
</body>
</html>
```
---

## Step 4: Upload Files
1. Open the bucket
2. Click Upload
3. Add both files:
    - index.html
    - error.html

4. Click Upload
5. Wait for upload success confirmation


---

# Phase 3 - Enable Static Website Hosting
## Step 5: Enable Hosting
### Navigation
```text
S3 Bucket → Properties → Static Website Hosting → Edit
```
### Configuration
| Setting | Value |
| ----- | ----- |
| Hosting Type | Host a static website |
| Index Document | `index.html`  |
| Error Document | `error.html`  |
Click Save Changes.

---

## Website Endpoint Example
```text
http://demo-static-website-yourname-2024.s3-website-us-east-1.amazonaws.com
```
---

## Expected Result
Opening the endpoint initially shows:

```text
403 Forbidden
```
because the bucket policy has not yet granted public access.



---

# Phase 4 - Add Bucket Policy
## Step 6: Configure Bucket Policy
### Navigation
```text
S3 Bucket → Permissions → Bucket Policy → Edit
```
### Bucket Policy
Replace `YOUR-BUCKET-NAME` with your actual bucket name.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```
Click Save Changes.

---

## Bucket Policy Breakdown
| Policy Element | Meaning |
| ----- | ----- |
| Version | Policy language version |
| Effect | Allow access |
| Principal | Everyone (`*`) |
| Action | Read/download objects |
| Resource | All objects inside bucket |


---

## Step 7: Test Website
1. Open Properties tab
2. Scroll to Static Website Hosting
3. Open Bucket Website Endpoint
4. Website should now load successfully
---

# Phase 5 - Demonstrate Versioning
## Step 8: Upload Updated Version
1. Edit `index.html` 
2. Change heading to:
```html
<h1>Version 2 - Updated!</h1>
```
1. Upload the same file again
2. Refresh website
3. Enable Show Versions in S3 object list
4. Observe multiple versions of the file


---

# Wrap-up Talking Points
- S3 static hosting costs fractions of a cent per month
- Ideal for landing pages, documentation, and frontend applications
- S3 only serves static content
- Dynamic applications still require EC2, ECS, or Lambda
- CloudFront is commonly placed in front of S3 for HTTPS and caching
- Major companies use S3 at massive scale
---

