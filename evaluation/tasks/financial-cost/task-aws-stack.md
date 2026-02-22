---
agent: financial-cost
type: happy-path
description: Standard AWS deployment with ECS, RDS, ElastiCache, S3, CloudFront — full infrastructure cost analysis
expected_outcome: pass
---

# Task: AWS Standard Stack — Full Cost Analysis

## Context

ShipFast is a B2B SaaS project management tool deployed on AWS. The infrastructure is defined in Terraform and runs on ECS Fargate (2 services: web API and background worker), RDS PostgreSQL (db.t3.medium), ElastiCache Redis (cache.t3.micro), S3 for file storage, CloudFront for CDN, and SES for transactional emails. The application serves approximately 800 active users across 60 paying teams. The Terraform configurations are present and well-structured, giving the financial agent concrete infrastructure to analyze.

This scenario tests the agent's ability to produce a thorough, itemized cost breakdown tied to real infrastructure definitions, project scaling costs at multiple user tiers, and identify cost optimization opportunities.

## Input

**Simulated Codebase Structure:**

```
shipfast/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint + test + build Docker image
│       └── deploy.yml                # Terraform plan/apply on main push
├── terraform/
│   ├── main.tf                       # Provider config, backend (S3 state)
│   ├── variables.tf                  # Environment, region, instance sizes
│   ├── outputs.tf
│   ├── vpc.tf                        # VPC, subnets, NAT gateway, security groups
│   ├── ecs.tf                        # ECS cluster, services, task definitions
│   ├── rds.tf                        # RDS PostgreSQL instance
│   ├── elasticache.tf                # Redis cluster
│   ├── s3.tf                         # Asset storage bucket + lifecycle rules
│   ├── cloudfront.tf                 # CDN distribution
│   ├── ses.tf                        # SES domain identity + DKIM
│   ├── alb.tf                        # Application Load Balancer
│   ├── ecr.tf                        # Container registry
│   ├── cloudwatch.tf                 # Log groups, alarms, dashboards
│   ├── iam.tf                        # IAM roles and policies
│   └── terraform.tfvars              # Environment-specific values
├── docker-compose.yml                # Local dev: PostgreSQL, Redis, app
├── Dockerfile                        # Multi-stage Node 20, ~180MB final image
├── package.json
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (dashboard)/
│   │   │   ├── projects/
│   │   │   ├── tasks/
│   │   │   ├── team/
│   │   │   ├── files/                # File upload/download (S3 presigned URLs)
│   │   │   └── billing/
│   │   └── api/
│   │       ├── auth/
│   │       ├── projects/
│   │       ├── tasks/
│   │       ├── files/
│   │       │   ├── upload/route.ts   # S3 presigned URL generation
│   │       │   └── [id]/route.ts     # S3 download proxy
│   │       ├── billing/
│   │       │   ├── checkout/route.ts
│   │       │   ├── webhook/route.ts  # Stripe webhook
│   │       │   └── portal/route.ts
│   │       ├── notifications/
│   │       │   └── route.ts          # SES email dispatch
│   │       └── workers/
│   │           ├── digest/route.ts   # Daily digest email (cron-triggered)
│   │           └── cleanup/route.ts  # S3 orphan cleanup (weekly cron)
│   ├── lib/
│   │   ├── prisma.ts
│   │   ├── stripe.ts
│   │   ├── s3.ts                     # S3 client + presigned URL helpers
│   │   ├── ses.ts                    # SES email sending
│   │   ├── redis.ts                  # ioredis client (caching + sessions)
│   │   └── auth.ts
│   └── components/
├── tests/
└── tsconfig.json
```

**Terraform Key Configurations:**

**terraform/ecs.tf (relevant excerpts):**

```hcl
resource "aws_ecs_cluster" "main" {
  name = "shipfast-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_service" "web" {
  name            = "shipfast-web"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.ecs.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.web.arn
    container_name   = "web"
    container_port   = 3000
  }
}

resource "aws_ecs_task_definition" "web" {
  family                   = "shipfast-web"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512    # 0.5 vCPU
  memory                   = 1024   # 1 GB
  network_mode             = "awsvpc"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "web"
    image = "${aws_ecr_repository.app.repository_url}:latest"
    portMappings = [{ containerPort = 3000, protocol = "tcp" }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"  = aws_cloudwatch_log_group.web.name
        "awslogs-region" = var.region
      }
    }
  }])
}

resource "aws_ecs_service" "worker" {
  name            = "shipfast-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.ecs.id]
  }
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "shipfast-worker"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256    # 0.25 vCPU
  memory                   = 512    # 0.5 GB
  network_mode             = "awsvpc"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "worker"
    image = "${aws_ecr_repository.app.repository_url}:latest"
    command = ["node", "dist/worker.js"]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"  = aws_cloudwatch_log_group.worker.name
        "awslogs-region" = var.region
      }
    }
  }])
}
```

**terraform/rds.tf:**

```hcl
resource "aws_db_instance" "main" {
  identifier           = "shipfast-${var.environment}"
  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = "db.t3.medium"
  allocated_storage    = 50
  max_allocated_storage = 200     # auto-scaling enabled
  storage_type         = "gp3"
  storage_encrypted    = true

  db_name  = "shipfast"
  username = "shipfast_admin"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  multi_az               = false   # Single AZ (no failover)
  backup_retention_period = 7
  skip_final_snapshot     = false

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn
}
```

**terraform/elasticache.tf:**

```hcl
resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "shipfast-${var.environment}"
  description          = "ShipFast Redis"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = "cache.t3.micro"
  num_cache_clusters   = 1         # Single node, no replication

  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
}
```

**terraform/s3.tf:**

```hcl
resource "aws_s3_bucket" "assets" {
  bucket = "shipfast-assets-${var.environment}"
}

resource "aws_s3_bucket_lifecycle_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
  }
}
```

**terraform/cloudfront.tf:**

```hcl
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "alb"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  origin {
    domain_name = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_id   = "s3-assets"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.main.cloudfront_access_identity_path
    }
  }

  enabled             = true
  default_root_object = ""
  price_class         = "PriceClass_100"   # US, Canada, Europe only

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "alb"
    forwarded_values {
      query_string = true
      cookies { forward = "all" }
    }
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
  }
}
```

**terraform/variables.tf:**

```hcl
variable "environment" {
  default = "production"
}

variable "region" {
  default = "us-east-1"
}

variable "db_password" {
  sensitive = true
}
```

**package.json dependencies:**

```json
{
  "name": "shipfast",
  "version": "1.2.0",
  "dependencies": {
    "next": "14.2.3",
    "@auth0/nextjs-auth0": "3.5.0",
    "stripe": "15.1.0",
    "@prisma/client": "5.12.1",
    "ioredis": "5.3.2",
    "@aws-sdk/client-s3": "3.540.0",
    "@aws-sdk/s3-request-presigner": "3.540.0",
    "@aws-sdk/client-ses": "3.540.0",
    "swr": "2.2.5",
    "zod": "3.23.4",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "tailwindcss": "3.4.3"
  }
}
```

**Key Technical Details:**
- ECS Fargate web service: 2 tasks at 0.5 vCPU / 1GB each
- ECS Fargate worker service: 1 task at 0.25 vCPU / 0.5GB
- RDS PostgreSQL db.t3.medium: 2 vCPU, 4GB RAM, 50GB gp3 storage (auto-scaling to 200GB)
- RDS is single-AZ (no Multi-AZ failover)
- ElastiCache Redis cache.t3.micro: single node, no replication
- S3 with lifecycle rule transitioning to IA after 90 days
- CloudFront PriceClass_100 (US/Canada/Europe only)
- SES for transactional emails (digest, invites, notifications)
- ALB fronting ECS web service
- NAT Gateway in VPC for private subnet internet access
- Container Insights enabled on ECS cluster
- RDS Performance Insights enabled
- Auth0 for authentication (external service)
- Stripe for billing (external service)
- GitHub Actions for CI/CD
- ~800 active users, 60 paying teams

## Expected Behaviors

- Produces an itemized monthly cost breakdown by AWS service, referencing specific Terraform resource configurations
- Identifies all major cost categories: compute (ECS Fargate), database (RDS), caching (ElastiCache), storage (S3), CDN (CloudFront), networking (NAT Gateway, ALB, data transfer), monitoring (CloudWatch, Container Insights, Performance Insights), email (SES), and external services (Auth0, Stripe)
- Explicitly calls out NAT Gateway as a significant cost often overlooked (~$32/month base + data processing fees)
- Provides scaling projections at 4 tiers: 1K, 10K, 100K, 1M users
- Identifies RDS db.t3.medium as a scaling bottleneck (max_connections, IOPS limits)
- Recognizes single-AZ RDS and single-node Redis as reliability risks that will require cost increases to address
- Suggests reserved instances or Savings Plans for Fargate and RDS
- Identifies S3 lifecycle rule as an existing cost optimization
- References specific Terraform files and resource configurations throughout
- Provides concrete dollar estimates grounded in current AWS pricing

## Success Criteria

- [ ] Itemized cost breakdown covers at least 8 distinct AWS service categories
- [ ] Each cost item references the specific Terraform resource that defines it (e.g., `rds.tf` db.t3.medium, `ecs.tf` 0.5 vCPU / 1GB)
- [ ] NAT Gateway costs are explicitly identified (commonly missed)
- [ ] Scaling projections provided for at least 3 user tiers with non-linear cost modeling
- [ ] RDS identified as a scaling bottleneck with specific thresholds (connection limits, IOPS)
- [ ] Reserved Instances or Savings Plans recommended with estimated savings
- [ ] External service costs included (Auth0, Stripe fees)
- [ ] Single-AZ RDS and single-node Redis flagged as reliability risks that would increase costs if addressed
- [ ] CloudWatch/Container Insights/Performance Insights costs included (monitoring is not free)
- [ ] Total monthly estimate is within a plausible range for this stack ($400-$900/month at current scale)

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT miss NAT Gateway costs — this is one of the most commonly overlooked AWS charges
- [ ] Should NOT use outdated AWS pricing (should reference current-generation pricing)
- [ ] Should NOT ignore data transfer costs between services (ECS to RDS, ECS to S3, NAT Gateway data processing)
- [ ] Should NOT model scaling projections as simple linear multipliers of base cost
- [ ] Should NOT overlook CloudWatch log ingestion and storage costs (Container Insights generates significant log volume)
- [ ] Should NOT present RDS storage auto-scaling (50GB to 200GB) without mentioning the cost implications
- [ ] Should NOT ignore Stripe transaction fees in the total cost picture
- [ ] Should NOT recommend Multi-AZ or read replicas without quantifying the cost increase
