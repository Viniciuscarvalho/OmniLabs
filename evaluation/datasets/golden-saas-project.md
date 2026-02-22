# Golden Reference Dataset: TaskFlow Pro

## Project Overview

**Name**: TaskFlow Pro
**Type**: B2B SaaS Project Management Tool
**Stage**: Early-growth (launched 4 months ago, ~120 paying teams)
**Team**: 3 full-stack engineers, 1 designer, 1 founder/CEO
**Tagline**: "Real-time project management for fast-moving teams"

TaskFlow Pro is a collaborative project management platform targeting small-to-midsize software teams (5-50 members). It offers real-time task boards, team workspaces, time tracking, and Stripe-powered subscription billing. The product competes in the crowded project management space but differentiates through developer-friendly features (GitHub integration, keyboard shortcuts, markdown support) and real-time collaboration via WebSockets.

---

## Simulated Codebase Structure

```
taskflow-pro/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # GitHub Actions: lint + test (no deploy)
│       └── dependabot.yml            # Weekly dependency updates
├── docker-compose.yml                # PostgreSQL 15, Redis 7, app
├── Dockerfile                        # Node 20 Alpine, multi-stage build
├── package.json
├── next.config.js
├── prisma/
│   ├── schema.prisma                 # 7 models, 23 relations
│   └── migrations/                   # 14 migration files
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                  # Landing page
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── callback/page.tsx     # Auth0 callback handler
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx            # Sidebar + top nav
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx          # Project list
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx      # Kanban board view
│   │   │   │       ├── list/page.tsx # List view
│   │   │   │       └── settings/page.tsx
│   │   │   ├── team/
│   │   │   │   ├── page.tsx          # Team members
│   │   │   │   └── invite/page.tsx   # Invite flow
│   │   │   └── billing/
│   │   │       ├── page.tsx          # Subscription management
│   │   │       └── invoices/page.tsx # Invoice history
│   │   └── api/
│   │       ├── auth/
│   │       │   ├── [...auth0]/route.ts  # Auth0 SDK routes
│   │       │   └── me/route.ts          # Current user info
│   │       ├── projects/
│   │       │   ├── route.ts             # GET (list), POST (create)
│   │       │   └── [id]/
│   │       │       ├── route.ts         # GET, PUT, DELETE
│   │       │       ├── tasks/route.ts   # GET, POST tasks
│   │       │       └── members/route.ts # GET, POST members
│   │       ├── tasks/
│   │       │   └── [id]/
│   │       │       ├── route.ts         # GET, PUT, DELETE
│   │       │       └── comments/route.ts
│   │       ├── billing/
│   │       │   ├── checkout/route.ts    # Stripe checkout session
│   │       │   ├── portal/route.ts      # Stripe billing portal
│   │       │   └── webhook/route.ts     # Stripe webhook handler
│   │       └── ws/
│   │           └── route.ts             # WebSocket upgrade handler
│   ├── lib/
│   │   ├── prisma.ts                # Singleton Prisma client
│   │   ├── auth0.ts                 # Auth0 SDK config
│   │   ├── stripe.ts                # Stripe SDK config
│   │   ├── redis.ts                 # Redis client (ioredis)
│   │   ├── websocket.ts             # WS server setup
│   │   └── utils.ts                 # Misc helpers
│   ├── components/
│   │   ├── ui/                      # ~18 shared UI components
│   │   ├── kanban/
│   │   │   ├── Board.tsx
│   │   │   ├── Column.tsx
│   │   │   └── Card.tsx
│   │   ├── TaskDetail.tsx
│   │   ├── CommentThread.tsx
│   │   └── TeamSelector.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts          # WS connection hook
│   │   ├── useProject.ts            # SWR-based data fetching
│   │   └── useAuth.ts               # Auth0 hook wrapper
│   └── types/
│       └── index.ts                 # Shared TypeScript types
├── tests/
│   ├── api/
│   │   ├── projects.test.ts         # 12 tests
│   │   ├── tasks.test.ts            # 8 tests
│   │   └── billing.test.ts          # 5 tests
│   └── components/
│       ├── Board.test.tsx           # 4 tests
│       └── Card.test.tsx            # 3 tests
├── .env.example
├── README.md
└── tsconfig.json
```

---

## Key Configuration Details

### package.json (dependencies)

```json
{
  "name": "taskflow-pro",
  "version": "0.8.2",
  "dependencies": {
    "next": "14.1.0",
    "@auth0/nextjs-auth0": "3.5.0",
    "stripe": "14.14.0",
    "@prisma/client": "5.9.1",
    "prisma": "5.9.1",
    "ioredis": "5.3.2",
    "ws": "8.16.0",
    "swr": "2.2.4",
    "zod": "3.22.4",
    "date-fns": "3.3.1",
    "nanoid": "5.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "tailwindcss": "3.4.1",
    "@radix-ui/react-dialog": "1.0.5",
    "@radix-ui/react-dropdown-menu": "2.0.6",
    "@radix-ui/react-tooltip": "1.0.7",
    "lucide-react": "0.312.0",
    "class-variance-authority": "0.7.0",
    "clsx": "2.1.0",
    "react-beautiful-dnd": "13.1.1",
    "react-hot-toast": "2.4.1",
    "sharp": "0.33.2"
  },
  "devDependencies": {
    "typescript": "5.3.3",
    "jest": "29.7.0",
    "@testing-library/react": "14.1.2",
    "@types/node": "20.11.5",
    "@types/react": "18.2.48",
    "eslint": "8.56.0",
    "eslint-config-next": "14.1.0"
  }
}
```

### Prisma Schema (models)

```prisma
model User {
  id          String   @id @default(cuid())
  auth0Id     String   @unique
  email       String   @unique
  name        String?
  avatarUrl   String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  memberships TeamMember[]
  comments    Comment[]
  assignedTasks Task[] @relation("assignee")
}

model Team {
  id           String   @id @default(cuid())
  name         String
  slug         String   @unique
  tenant_id    String   @default(cuid())  // shared DB multi-tenancy
  createdAt    DateTime @default(now())
  members      TeamMember[]
  projects     Project[]
  subscription Subscription?
  invoices     Invoice[]
}

model TeamMember {
  id     String @id @default(cuid())
  role   String @default("member")  // "owner" | "admin" | "member"
  user   User   @relation(fields: [userId], references: [id])
  userId String
  team   Team   @relation(fields: [teamId], references: [id])
  teamId String
  @@unique([userId, teamId])
}

model Project {
  id          String   @id @default(cuid())
  name        String
  description String?
  status      String   @default("active")
  team        Team     @relation(fields: [teamId], references: [id])
  teamId      String
  tasks       Task[]
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

model Task {
  id          String   @id @default(cuid())
  title       String
  description String?
  status      String   @default("todo")  // todo, in_progress, review, done
  priority    String   @default("medium")
  position    Int
  project     Project  @relation(fields: [projectId], references: [id])
  projectId   String
  assignee    User?    @relation("assignee", fields: [assigneeId], references: [id])
  assigneeId  String?
  comments    Comment[]
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

model Comment {
  id        String   @id @default(cuid())
  content   String
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  task      Task     @relation(fields: [taskId], references: [id])
  taskId    String
  createdAt DateTime @default(now())
}

model Subscription {
  id               String   @id @default(cuid())
  stripeCustomerId String   @unique
  stripeSubId      String   @unique
  plan             String   @default("starter")  // starter, pro, enterprise
  status           String   // active, canceled, past_due
  team             Team     @relation(fields: [teamId], references: [id])
  teamId           String   @unique
  currentPeriodEnd DateTime
}

model Invoice {
  id              String   @id @default(cuid())
  stripeInvoiceId String   @unique
  amount          Int      // cents
  status          String   // paid, open, void
  team            Team     @relation(fields: [teamId], references: [id])
  teamId          String
  createdAt       DateTime @default(now())
}
```

### Environment Variables (.env.example)

```bash
# App
DATABASE_URL="postgresql://taskflow:password@localhost:5432/taskflow"
REDIS_URL="redis://localhost:6379"
NEXTAUTH_URL="http://localhost:3000"
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# Auth0
AUTH0_SECRET="LONG_RANDOM_VALUE"
AUTH0_BASE_URL="http://localhost:3000"
AUTH0_ISSUER_BASE_URL="https://taskflow-dev.us.auth0.com"
AUTH0_CLIENT_ID="your_client_id"
AUTH0_CLIENT_SECRET="your_client_secret"

# Stripe
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."

# WebSocket
WS_PORT=3001
```

### CI Configuration (.github/workflows/ci.yml)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npx prisma migrate deploy
      - run: npm run lint
      - run: npm test -- --coverage
        # No deploy step — manual deploys via docker-compose
```

### Docker Compose (docker-compose.yml)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
      - "3001:3001"
    environment:
      - DATABASE_URL=postgresql://taskflow:password@db:5432/taskflow
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  db:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: taskflow
      POSTGRES_PASSWORD: password
      POSTGRES_DB: taskflow
  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
volumes:
  pgdata:
  redisdata:
```

---

## Feature Inventory

### What Exists

| Feature | Status | Implementation Quality |
|---------|--------|----------------------|
| User authentication (Auth0) | Complete | Good - SDK properly integrated |
| Team creation and management | Complete | Good - role-based access |
| Project CRUD | Complete | Good - Prisma ORM |
| Task CRUD with Kanban board | Complete | Good - drag-and-drop |
| Task list view | Complete | Basic |
| Task comments | Complete | Basic - no threading |
| Real-time task updates (WebSocket) | Complete | Fragile - no reconnect logic |
| Stripe subscription billing | Complete | Good - 3 tiers |
| Stripe webhook handling | Complete | Partial - missing some events |
| Invoice history | Complete | Basic |
| Team member invitations | Complete | Email-based, no expiry |
| GitHub Actions CI | Complete | Lint + test only |
| Docker Compose deployment | Complete | Dev-friendly, not prod-ready |
| Input validation (Zod) | Partial | Only on task/project creation |
| ISR (Incremental Static Regeneration) | Partial | Landing page only |

### What is Missing

| Feature | Impact | Notes |
|---------|--------|-------|
| Rate limiting | HIGH | No protection on any API route |
| Structured logging | HIGH | Only console.log statements |
| Monitoring/alerting | HIGH | No APM, no health checks |
| Caching strategy | MEDIUM | Redis exists but only used for WS pub/sub |
| Multi-tenancy isolation | HIGH | Shared DB with tenant_id column, no RLS |
| WebSocket reconnection | MEDIUM | Client drops on network blip |
| Webhook retry handling | MEDIUM | No idempotency keys |
| Error boundaries | MEDIUM | No global error boundary component |
| E2E tests | MEDIUM | Only unit/integration tests |
| Database indexes | MEDIUM | Only default PK indexes, no composite |
| Audit logging | LOW | No tracking of who changed what |
| File attachments | LOW | Not implemented |
| Search functionality | LOW | No full-text search |
| Mobile responsiveness | LOW | Desktop-first, basic responsive |

---

## Expected Analysis Patterns

### Business & Product Agent

**Market Opportunity Score**: Expected 6-7/10

Expected findings:
- **TAM**: Global project management software market ~$6-8B (2024), growing 10-13% CAGR
- **SAM**: B2B SaaS project management for software teams, ~$2-3B
- **SOM**: Realistic year-1 capture <$1M given team size and market maturity
- **Competitors identified**: Asana, Monday.com, Linear, ClickUp, Jira, Notion, Trello, Basecamp
- **PMF signals**: Stripe integration indicates paying customers exist; 3-tier pricing shows monetization thinking; 120 teams is early traction
- **Moat assessment**: Weak to None -- no proprietary data advantage, no strong network effects, low switching costs in a crowded market
- **Differentiation**: Developer-friendly features (GitHub integration path, markdown, keyboard shortcuts) position against general PM tools but compete directly with Linear
- **GTM recommendation**: Product-led growth (PLG) with freemium tier; developer community marketing; content marketing around engineering team workflows
- **Revenue model**: Current Stripe 3-tier subscription is viable; should consider per-seat pricing
- **Key risk**: Red ocean market with well-funded incumbents; differentiation is easily copied

### Financial & Cost Agent

**Financial Health Score**: Expected 5-6/10

Expected findings:
- **Auth0 costs**: Free tier covers ~7K MAU; paid starts at ~$23/month for Essential plan; at scale (10K+ users), Auth0 becomes expensive ($228+/mo for Professional, enterprise pricing required above 50K)
- **Stripe fees**: 2.9% + $0.30 per transaction; at $29/mo starter plan, that is ~$1.14/transaction (3.9% effective rate); improves at higher plan prices
- **Infrastructure costs at current scale**:
  - Hosting (single VPS or small instance): $20-50/month
  - PostgreSQL (managed, e.g., RDS db.t3.micro): $15-30/month
  - Redis (managed, e.g., ElastiCache t3.micro): $12-25/month
  - Auth0: Free tier (under 7K MAU)
  - Domain + DNS: ~$15/year
  - GitHub Actions: Free tier
  - **Total current**: ~$50-120/month
- **Scaling projection concerns**:
  - 1K users: ~$150-300/month
  - 10K users: ~$500-1,200/month (Auth0 jumps significantly here)
  - 100K users: ~$3,000-8,000/month (need dedicated DB, multiple app instances)
  - 1M users: ~$15,000-40,000/month (requires architecture overhaul)
- **Cost optimization opportunities**: Replace Auth0 with self-hosted auth (NextAuth.js/Lucia) to eliminate scaling cost cliff; implement Redis caching to reduce DB load; add CDN for static assets
- **Financial risks**: Auth0 vendor lock-in is the largest cost risk; no cost monitoring means surprise bills; Docker Compose cannot auto-scale

### Technical Architecture Agent

**Architecture Health Score**: Expected 5/10

Expected dimension scores:
- **Scalability**: 4-5/10 -- Single Docker Compose deployment, no horizontal scaling, WebSocket server is stateful, no load balancer, Redis used only for WS pub/sub not caching
- **Reliability**: 4-5/10 -- No health checks, no circuit breakers, no retry logic, WebSocket has no reconnection, webhook handler lacks idempotency
- **Maintainability**: 6-7/10 -- Clean Next.js App Router structure, Prisma ORM, TypeScript, Zod validation (partial), but 45% test coverage is below acceptable threshold
- **Security**: 5-6/10 -- Auth0 handles auth well, but no rate limiting on API routes, shared DB multi-tenancy without RLS is a data isolation risk, Zod validation is incomplete, no CSRF protection verification
- **Observability**: 2-3/10 -- Only console.log, no structured logging, no metrics, no tracing, no alerting, no health endpoints
- **Operability**: 3-4/10 -- CI runs tests but no CD pipeline, Docker Compose is not production-grade, no IaC, no feature flags, no runbooks

Critical findings expected:
- CRITICAL: No rate limiting on any API endpoint
- CRITICAL: Multi-tenancy via tenant_id without Row Level Security
- HIGH: Zero observability infrastructure
- HIGH: WebSocket server cannot scale horizontally (no sticky sessions or shared state beyond Redis pub/sub)
- MEDIUM: 45% test coverage with no E2E tests
- MEDIUM: No database indexes beyond primary keys

### Devil's Advocate Agent

**Risk Score**: Expected 6-7/10

Expected findings:
- **Assumption Audit**:
  - "Small teams prefer simpler tools" -- Questionable. Small teams often use free tiers of enterprise tools (Jira, Asana)
  - "WebSockets provide a competitive advantage" -- Questionable. Real-time is table stakes in 2024; competitors all have it
  - "Auth0 simplifies authentication" -- Valid short-term, Questionable long-term due to cost scaling
- **Failure Scenarios**:
  - Most Likely: Acquisition stalls at ~500 teams due to inability to compete on features with well-funded competitors; growth flatlines, team burns out
  - Most Damaging: Multi-tenancy data leak due to missing RLS; a tenant sees another tenant's data; complete loss of trust
  - Black Swan: Auth0 has a security breach affecting all customers; TaskFlow Pro is unable to authenticate any users and has no fallback auth mechanism
- **Key challenges**:
  - 45% test coverage = 55% of code paths are untested; any refactoring is risky
  - WebSocket scaling: Current architecture supports ~1,000 concurrent connections per server instance; no plan for horizontal scaling
  - Observability gap: Cannot detect issues before users report them; mean time to detection (MTTD) is effectively infinite
  - No competitive moat: Every feature can be replicated by a competitor with more resources in weeks
- **Blind spots**:
  - No data backup strategy documented
  - No consideration of GDPR/data privacy compliance
  - Invite system has no expiry, creating potential security exposure
  - No consideration of API versioning for future breaking changes
- **Cross-references**: Should challenge business agent's TAM estimate (market is mature, not greenfield), financial agent's cost projections (Auth0 cost cliff), and technical agent's maintainability score (45% coverage should lower it further)

### Lead Synthesis Agent

**Expected Decision**: CONDITIONAL GO

**Expected Composite Score**: 5-6/10

**Expected Conditions**:
1. Implement rate limiting and Row Level Security within 30 days
2. Achieve 70%+ test coverage within 60 days
3. Deploy basic observability (structured logging + health checks + error tracking) within 30 days
4. Develop Auth0 migration plan to avoid cost cliff at scale

**Consensus Findings** (3+ agents agree):
- Observability is critically lacking
- Auth0 presents a cost/risk concern at scale
- Market is competitive but viable if differentiation sharpens
- Multi-tenancy isolation is a security risk

**Contested Findings**:
- Business says market opportunity is strong; Devil's Advocate says it is a red ocean with low moat
- Technical says maintainability is acceptable (6-7); Devil's Advocate says 45% coverage makes it fragile

**Implementation Roadmap**:
- Phase 1 (Days 1-30): Security hardening (rate limiting, RLS, input validation)
- Phase 2 (Days 31-60): Observability foundation (structured logging, health checks, error tracking, basic dashboards)
- Phase 3 (Days 61-90): Scale preparation (caching strategy, WebSocket scaling plan, Auth0 migration evaluation, test coverage push to 70%)
