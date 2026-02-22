---
agent: financial-cost
type: edge-case
description: Fully serverless AWS stack with Lambda, DynamoDB, API Gateway — tests non-traditional cost modeling
expected_outcome: partial
---

# Task: Serverless Architecture — Per-Invocation Cost Modeling

## Context

NotifyHub is a notification orchestration service that routes messages across email, SMS, push, and webhook channels. The entire backend is serverless on AWS: Lambda functions for all business logic, DynamoDB for data storage, API Gateway for HTTP endpoints, S3 for templates, and CloudFront for the admin dashboard. The infrastructure is defined using AWS SAM (Serverless Application Model). There is no persistent compute — every execution is event-driven and billed per invocation.

This scenario tests whether the financial-cost agent can correctly model per-invocation cost structures, understand DynamoDB pricing modes, and avoid applying traditional server-based cost models to a serverless architecture.

## Input

**Simulated Codebase Structure:**

```
notifyhub/
├── template.yaml                     # SAM template (all infrastructure)
├── samconfig.toml                    # Deployment configuration
├── src/
│   ├── handlers/
│   │   ├── api/
│   │   │   ├── createNotification.ts   # POST /notifications — create + enqueue
│   │   │   ├── getNotification.ts      # GET /notifications/{id}
│   │   │   ├── listNotifications.ts    # GET /notifications (paginated)
│   │   │   ├── createTemplate.ts       # POST /templates — store in S3
│   │   │   ├── getTemplate.ts          # GET /templates/{id}
│   │   │   └── getStats.ts             # GET /stats — aggregated delivery stats
│   │   ├── processors/
│   │   │   ├── emailProcessor.ts       # SQS consumer — sends via SES
│   │   │   ├── smsProcessor.ts         # SQS consumer — sends via SNS
│   │   │   ├── pushProcessor.ts        # SQS consumer — sends via Firebase
│   │   │   └── webhookProcessor.ts     # SQS consumer — HTTP POST to endpoint
│   │   ├── events/
│   │   │   ├── deliveryCallback.ts     # SNS/SES delivery status updates
│   │   │   └── dlqProcessor.ts         # Dead letter queue handler
│   │   └── scheduled/
│   │       ├── dailyDigest.ts          # EventBridge cron — aggregate + send digest
│   │       └── cleanupExpired.ts       # EventBridge cron — remove old notifications
│   ├── lib/
│   │   ├── dynamodb.ts                 # DynamoDB DocumentClient wrapper
│   │   ├── sqs.ts                      # SQS send/receive helpers
│   │   ├── ses.ts                      # SES email sending
│   │   ├── sns.ts                      # SNS SMS sending
│   │   ├── s3.ts                       # S3 template storage
│   │   ├── firebase.ts                 # Firebase Admin for push notifications
│   │   └── template-engine.ts          # Handlebars template rendering
│   └── types/
│       └── index.ts
├── tests/
│   ├── handlers/
│   │   ├── createNotification.test.ts  # 12 tests
│   │   ├── emailProcessor.test.ts      # 8 tests
│   │   ├── smsProcessor.test.ts        # 6 tests
│   │   └── webhookProcessor.test.ts    # 5 tests
│   └── lib/
│       └── template-engine.test.ts     # 7 tests
├── package.json
├── tsconfig.json
└── README.md
```

**template.yaml (SAM template — key resources):**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: NotifyHub - Notification Orchestration Service

Globals:
  Function:
    Runtime: nodejs20.x
    Timeout: 30
    MemorySize: 256
    Architectures:
      - arm64
    Environment:
      Variables:
        TABLE_NAME: !Ref NotificationsTable
        TEMPLATE_BUCKET: !Ref TemplateBucket
        EMAIL_QUEUE_URL: !Ref EmailQueue
        SMS_QUEUE_URL: !Ref SmsQueue
        PUSH_QUEUE_URL: !Ref PushQueue
        WEBHOOK_QUEUE_URL: !Ref WebhookQueue

Resources:
  # API Gateway
  HttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: prod
      CorsConfiguration:
        AllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
        AllowOrigins:
          - "*"
      Auth:
        DefaultAuthorizer: JwtAuthorizer
        Authorizers:
          JwtAuthorizer:
            AuthorizationScopes:
              - api:access
            IdentitySource: $request.header.Authorization
            JwtConfiguration:
              issuer: !Sub "https://${Auth0Domain}"
              audience:
                - !Ref Auth0Audience

  # API Lambda Functions
  CreateNotificationFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/api/createNotification.handler
      MemorySize: 512
      Timeout: 10
      Events:
        Api:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Path: /notifications
            Method: POST
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref NotificationsTable
        - SQSSendMessagePolicy:
            QueueName: !GetAtt EmailQueue.QueueName
        - SQSSendMessagePolicy:
            QueueName: !GetAtt SmsQueue.QueueName
        - SQSSendMessagePolicy:
            QueueName: !GetAtt PushQueue.QueueName
        - SQSSendMessagePolicy:
            QueueName: !GetAtt WebhookQueue.QueueName

  GetNotificationFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/api/getNotification.handler
      MemorySize: 256
      Events:
        Api:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Path: /notifications/{id}
            Method: GET
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref NotificationsTable

  ListNotificationsFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/api/listNotifications.handler
      MemorySize: 256
      Timeout: 15
      Events:
        Api:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Path: /notifications
            Method: GET
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref NotificationsTable

  # SQS Processor Functions
  EmailProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/processors/emailProcessor.handler
      MemorySize: 256
      Timeout: 60
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt EmailQueue.Arn
            BatchSize: 10
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref NotificationsTable
        - Statement:
            Effect: Allow
            Action: ses:SendEmail
            Resource: "*"

  SmsProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/processors/smsProcessor.handler
      MemorySize: 256
      Timeout: 30
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt SmsQueue.Arn
            BatchSize: 5
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref NotificationsTable
        - Statement:
            Effect: Allow
            Action: sns:Publish
            Resource: "*"

  PushProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/processors/pushProcessor.handler
      MemorySize: 256
      Timeout: 30
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt PushQueue.Arn
            BatchSize: 10

  WebhookProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/processors/webhookProcessor.handler
      MemorySize: 512
      Timeout: 60
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt WebhookQueue.Arn
            BatchSize: 5

  # Scheduled Functions
  DailyDigestFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/scheduled/dailyDigest.handler
      MemorySize: 512
      Timeout: 300
      Events:
        Schedule:
          Type: Schedule
          Properties:
            Schedule: cron(0 8 * * ? *)
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref NotificationsTable

  CleanupExpiredFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/scheduled/cleanupExpired.handler
      MemorySize: 256
      Timeout: 300
      Events:
        Schedule:
          Type: Schedule
          Properties:
            Schedule: rate(1 day)
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref NotificationsTable

  # DynamoDB Tables
  NotificationsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "notifyhub-notifications-${AWS::StackName}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
        - AttributeName: GSI1SK
          AttributeType: S
        - AttributeName: GSI2PK
          AttributeType: S
        - AttributeName: GSI2SK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: GSI1SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: GSI2
          KeySchema:
            - AttributeName: GSI2PK
              KeyType: HASH
            - AttributeName: GSI2SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      TimeToLiveSpecification:
        AttributeName: expiresAt
        Enabled: true

  StatsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "notifyhub-stats-${AWS::StackName}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE

  ConfigTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "notifyhub-config-${AWS::StackName}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH

  # SQS Queues
  EmailQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 120
      MessageRetentionPeriod: 345600
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt EmailDLQ.Arn
        maxReceiveCount: 3

  EmailDLQ:
    Type: AWS::SQS::Queue
    Properties:
      MessageRetentionPeriod: 1209600

  SmsQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 60
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt SmsDLQ.Arn
        maxReceiveCount: 3

  SmsDLQ:
    Type: AWS::SQS::Queue

  PushQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 60
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt PushDLQ.Arn
        maxReceiveCount: 3

  PushDLQ:
    Type: AWS::SQS::Queue

  WebhookQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 120
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt WebhookDLQ.Arn
        maxReceiveCount: 5

  WebhookDLQ:
    Type: AWS::SQS::Queue

  # S3
  TemplateBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

  # CloudFront (Admin Dashboard)
  DashboardDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !Sub "${DashboardBucket}.s3.amazonaws.com"
            Id: dashboard-origin
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${DashboardOAI}"
        DefaultCacheBehavior:
          TargetOriginId: dashboard-origin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6
        Enabled: true
        DefaultRootObject: index.html
```

**package.json:**

```json
{
  "name": "notifyhub",
  "version": "1.5.0",
  "dependencies": {
    "@aws-sdk/client-dynamodb": "3.540.0",
    "@aws-sdk/lib-dynamodb": "3.540.0",
    "@aws-sdk/client-sqs": "3.540.0",
    "@aws-sdk/client-ses": "3.540.0",
    "@aws-sdk/client-sns": "3.540.0",
    "@aws-sdk/client-s3": "3.540.0",
    "firebase-admin": "12.0.0",
    "handlebars": "4.7.8",
    "zod": "3.23.4",
    "nanoid": "5.0.7",
    "date-fns": "3.6.0"
  },
  "devDependencies": {
    "typescript": "5.4.5",
    "vitest": "1.4.0",
    "aws-sam-cli": "latest",
    "@types/aws-lambda": "8.10.136",
    "esbuild": "0.20.2"
  }
}
```

**Key Technical Details:**
- 12 Lambda functions total: 6 API handlers, 4 SQS processors, 2 scheduled
- All functions use arm64 architecture (Graviton, 20% cheaper)
- Default memory: 256MB; some functions elevated to 512MB
- DynamoDB: 3 tables, all on-demand (PAY_PER_REQUEST) billing mode
- DynamoDB: 2 GSIs on the main table (ProjectionType: ALL — duplicates all data)
- SQS: 4 processing queues + 4 dead letter queues (8 queues total)
- API Gateway: HTTP API (not REST API — cheaper per request)
- TTL enabled on notifications table for automatic cleanup
- SES for email, SNS for SMS, Firebase for push, HTTP for webhooks
- No persistent compute whatsoever — pure event-driven

## Expected Behaviors

- Models costs on a per-invocation/per-request basis rather than monthly fixed compute
- Correctly identifies that HTTP API Gateway is cheaper than REST API ($1/million requests vs $3.50/million)
- Calculates Lambda costs based on invocation count + duration + memory allocation
- Notes the arm64/Graviton 20% pricing advantage
- Compares DynamoDB on-demand vs provisioned pricing, and identifies when provisioned becomes cheaper
- Flags that GSIs with ProjectionType: ALL double the storage and WCU costs for the notifications table
- Accounts for SQS pricing (first 1M requests free, then $0.40/million)
- Includes SES ($0.10/1000 emails) and SNS SMS costs (variable by country)
- Discusses cold start implications for latency-sensitive API functions
- Provides a cost-per-notification metric across different volume scenarios
- Notes that the free tier covers significant usage for many of these services

## Success Criteria

- [ ] Per-invocation cost model used (not traditional monthly server costs)
- [ ] Lambda costs broken down by function with memory, duration, and invocation estimates
- [ ] API Gateway HTTP API pricing correctly applied (~$1/million requests)
- [ ] DynamoDB on-demand vs provisioned pricing comparison provided with crossover point
- [ ] GSI storage and write cost duplication identified as an optimization target
- [ ] SQS, SES, and SNS costs modeled per-message
- [ ] Cold start implications mentioned (arm64 + 256MB can have ~500ms cold starts)
- [ ] Free tier coverage identified (Lambda 1M free invocations, SQS 1M free, DynamoDB 25 RCU/WCU free)
- [ ] Cost-per-notification metric provided at different volumes (1K/day, 10K/day, 100K/day, 1M/day)
- [ ] References specific SAM template resources and configurations

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT apply traditional server cost models (no EC2-style hourly pricing)
- [ ] Should NOT ignore API Gateway costs — they can become the largest cost component at scale
- [ ] Should NOT miss the SQS queue costs (8 queues with different message volumes)
- [ ] Should NOT treat all Lambda functions as having the same cost profile (memory and timeout vary)
- [ ] Should NOT forget SMS costs via SNS (these can be expensive at scale, especially international)
- [ ] Should NOT present DynamoDB on-demand as always cheaper without comparing to provisioned at higher volumes
- [ ] Should NOT ignore the DLQ storage costs (messages retained for up to 14 days)
- [ ] Should NOT skip CloudFront costs for the admin dashboard
