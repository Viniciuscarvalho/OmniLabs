---
agent: technical-architecture
type: happy-path
description: Go microservices on Kubernetes with full observability stack
expected_outcome: pass
---

# Task: Go Microservices with Kubernetes and Observability

## Context

A fintech startup building a payment orchestration platform called "PayRoute." The system routes transactions across multiple payment processors (Stripe, Adyen, Braintree) to optimize for cost and success rates. The team of 8 engineers has built 4 Go microservices deployed on Kubernetes with a full Istio service mesh, distributed tracing via Jaeger, and monitoring via Prometheus + Grafana. Inter-service communication uses gRPC. The platform processes ~200,000 transactions/month and is growing 15% month-over-month.

## Input

**Project**: PayRoute
**Type**: B2B Fintech Payment Orchestration
**Stage**: Series A ($4M raised), 18 months in production
**Team**: 8 engineers (3 backend, 2 platform/infra, 1 frontend, 1 QA, 1 lead)

### Simulated Codebase Structure

```
payroute/
├── services/
│   ├── api-gateway/
│   │   ├── cmd/
│   │   │   └── main.go                   # HTTP server entry point
│   │   ├── internal/
│   │   │   ├── handlers/
│   │   │   │   ├── transaction.go        # POST /v1/transactions
│   │   │   │   ├── merchant.go           # Merchant CRUD
│   │   │   │   ├── webhook.go            # Inbound webhooks from processors
│   │   │   │   └── health.go             # /healthz and /readyz endpoints
│   │   │   ├── middleware/
│   │   │   │   ├── auth.go               # JWT validation + API key auth
│   │   │   │   ├── ratelimit.go          # Token bucket rate limiter
│   │   │   │   ├── logging.go            # Structured request logging
│   │   │   │   └── tracing.go            # OpenTelemetry span creation
│   │   │   └── router/
│   │   │       └── router.go             # Chi router with middleware chain
│   │   ├── go.mod
│   │   ├── go.sum
│   │   ├── Dockerfile                    # Multi-stage Go build
│   │   └── Makefile
│   ├── user-service/
│   │   ├── cmd/
│   │   │   └── main.go                   # gRPC server entry point
│   │   ├── internal/
│   │   │   ├── service/
│   │   │   │   ├── user.go               # User management logic
│   │   │   │   └── merchant.go           # Merchant onboarding
│   │   │   ├── repository/
│   │   │   │   ├── user_repo.go          # PostgreSQL user queries
│   │   │   │   └── merchant_repo.go      # PostgreSQL merchant queries
│   │   │   └── grpc/
│   │   │       └── server.go             # gRPC server implementation
│   │   ├── proto/
│   │   │   └── user.proto                # Protobuf definitions
│   │   ├── go.mod
│   │   ├── Dockerfile
│   │   └── migrations/
│   │       └── *.sql                     # 18 migration files
│   ├── order-service/
│   │   ├── cmd/
│   │   │   └── main.go                   # gRPC + NATS subscriber
│   │   ├── internal/
│   │   │   ├── service/
│   │   │   │   ├── transaction.go        # Transaction orchestration logic
│   │   │   │   ├── routing.go            # Processor selection algorithm
│   │   │   │   └── retry.go             # Retry logic with exponential backoff
│   │   │   ├── repository/
│   │   │   │   └── transaction_repo.go   # PostgreSQL transaction records
│   │   │   ├── processor/
│   │   │   │   ├── interface.go          # Processor interface definition
│   │   │   │   ├── stripe.go             # Stripe adapter
│   │   │   │   ├── adyen.go              # Adyen adapter
│   │   │   │   └── braintree.go          # Braintree adapter
│   │   │   └── grpc/
│   │   │       └── server.go
│   │   ├── proto/
│   │   │   └── order.proto
│   │   ├── go.mod
│   │   ├── Dockerfile
│   │   └── migrations/
│   │       └── *.sql                     # 24 migration files
│   └── notification-service/
│       ├── cmd/
│       │   └── main.go                   # NATS subscriber entry point
│       ├── internal/
│       │   ├── service/
│       │   │   ├── email.go              # SendGrid email delivery
│       │   │   ├── webhook.go            # Outbound webhook delivery
│       │   │   └── slack.go              # Slack alerting for failures
│       │   └── subscriber/
│       │       └── events.go             # NATS event handlers
│       ├── go.mod
│       └── Dockerfile
├── proto/
│   ├── common/
│   │   └── types.proto                   # Shared protobuf types
│   └── buf.yaml                          # Buf protobuf tooling
├── infra/
│   ├── kubernetes/
│   │   ├── base/
│   │   │   ├── namespace.yaml
│   │   │   ├── api-gateway/
│   │   │   │   ├── deployment.yaml       # 3 replicas, resource limits
│   │   │   │   ├── service.yaml          # ClusterIP
│   │   │   │   └── hpa.yaml             # HorizontalPodAutoscaler (CPU 70%)
│   │   │   ├── user-service/
│   │   │   │   ├── deployment.yaml       # 2 replicas
│   │   │   │   ├── service.yaml
│   │   │   │   └── hpa.yaml
│   │   │   ├── order-service/
│   │   │   │   ├── deployment.yaml       # 3 replicas
│   │   │   │   ├── service.yaml
│   │   │   │   └── hpa.yaml
│   │   │   └── notification-service/
│   │   │       ├── deployment.yaml       # 2 replicas
│   │   │       └── service.yaml
│   │   └── overlays/
│   │       ├── staging/
│   │       │   └── kustomization.yaml
│   │       └── production/
│   │           └── kustomization.yaml
│   ├── helm/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-staging.yaml
│   │   └── values-production.yaml
│   ├── istio/
│   │   ├── gateway.yaml                  # Istio ingress gateway
│   │   ├── virtual-services.yaml         # Traffic routing rules
│   │   ├── destination-rules.yaml        # Circuit breaker configs
│   │   └── peer-authentication.yaml      # mTLS enforcement
│   └── terraform/
│       ├── main.tf                        # GKE cluster definition
│       ├── networking.tf                  # VPC, subnets, firewall rules
│       ├── database.tf                    # Cloud SQL PostgreSQL (HA)
│       ├── monitoring.tf                  # Prometheus/Grafana stack
│       └── variables.tf
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yaml               # Scrape configs for all services
│   │   └── rules/
│   │       ├── alerts.yaml               # Alert rules (latency, error rate)
│   │       └── recording-rules.yaml      # Pre-computed metrics
│   ├── grafana/
│   │   └── dashboards/
│   │       ├── api-gateway.json          # Request rate, latency, errors
│   │       ├── order-service.json        # Transaction success rate
│   │       └── infrastructure.json       # Node/pod resource usage
│   └── jaeger/
│       └── jaeger.yaml                   # Jaeger all-in-one deployment
├── .github/
│   └── workflows/
│       ├── ci.yml                        # Lint, test, build per service
│       ├── cd-staging.yml                # Auto-deploy to staging on merge
│       └── cd-production.yml             # Manual approval deploy to prod
├── Makefile                               # Top-level build commands
└── README.md
```

### Key Configuration Details

**go.mod (api-gateway, representative)**:
```go
module github.com/payroute/api-gateway

go 1.21

require (
    github.com/go-chi/chi/v5 v5.0.11
    github.com/golang-jwt/jwt/v5 v5.2.0
    google.golang.org/grpc v1.61.0
    google.golang.org/protobuf v1.32.0
    github.com/nats-io/nats.go v1.32.0
    go.opentelemetry.io/otel v1.22.0
    go.opentelemetry.io/otel/exporters/jaeger v1.17.0
    go.uber.org/zap v1.26.0
    github.com/prometheus/client_golang v1.18.0
    github.com/jmoiron/sqlx v1.3.5
    github.com/lib/pq v1.10.9
)
```

**Istio Circuit Breaker (destination-rules.yaml)**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: order-service
spec:
  host: order-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 30s
      baseEjectionTime: 60s
      maxEjectionPercent: 50
```

**HPA Configuration (api-gateway)**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

**Test coverage**: 65% overall. Breakdown: api-gateway 72%, user-service 68%, order-service 61%, notification-service 55%. Unit tests exist for all services. Integration tests exist for api-gateway and order-service. No end-to-end tests across services.

**Deployment**: GKE cluster (3 nodes, e2-standard-4). Staging auto-deploys on merge to main. Production requires manual approval in GitHub Actions.

## Expected Behaviors

- Evaluates the gRPC inter-service communication patterns, noting advantages (type safety, performance) and risks (debugging complexity, schema evolution)
- Identifies distributed system failure modes: network partitions between services, cascading failures, data consistency challenges across service boundaries
- Scores observability highly given the Jaeger + Prometheus + Grafana stack with custom dashboards and alert rules
- Recognizes the Istio circuit breaker and outlier detection as strong reliability patterns
- Notes the operational complexity overhead of K8s + Istio + Helm + Kustomize for an 8-person team (2 of whom are platform engineers)
- Identifies that 65% test coverage is below acceptable thresholds, especially for a fintech platform handling payments
- Flags the absence of E2E tests across service boundaries as a gap in a microservices architecture
- Acknowledges the strong IaC practice (Terraform + Helm + Kustomize)
- Notes the NATS messaging for async communication between order-service and notification-service

## Success Criteria

- [ ] Scalability score is 7-9/10, reflecting HPA, multiple replicas, and horizontal scaling capability
- [ ] Reliability score is 6-8/10, reflecting circuit breakers and retry logic but noting no chaos engineering or E2E resilience testing
- [ ] Maintainability score is 5-7/10, reflecting clean Go code and Protobuf contracts but noting 65% coverage and 4-service complexity
- [ ] Security score is 7-9/10, reflecting mTLS via Istio, JWT auth, rate limiting, and VPC networking
- [ ] Observability score is 8-9/10, reflecting Jaeger tracing, Prometheus metrics, Grafana dashboards, and structured logging
- [ ] Operability score is 7-8/10, reflecting CI/CD pipelines, IaC, and Kubernetes orchestration
- [ ] Identifies the team-to-complexity ratio as a concern (8 engineers maintaining K8s + Istio + 4 services)
- [ ] Notes that the Jaeger "all-in-one" deployment is not production-grade for a fintech platform
- [ ] Discusses the trade-off between microservices flexibility and distributed system complexity

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT ignore the operational complexity cost of running K8s + Istio for this team size
- [ ] Should NOT overlook the 65% test coverage as inadequate for a fintech payment processing platform
- [ ] Should NOT assume the architecture is correct just because it uses microservices and Kubernetes
- [ ] Should NOT fail to mention the lack of E2E tests across service boundaries
- [ ] Should NOT give observability a perfect 10/10 without noting the Jaeger all-in-one limitation
- [ ] Should NOT ignore the NATS dependency as a potential single point of failure if not clustered
