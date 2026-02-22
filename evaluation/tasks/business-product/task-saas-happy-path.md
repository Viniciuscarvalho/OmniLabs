---
agent: business-product
type: happy-path
description: B2B SaaS analytics platform with clear revenue model, established competitors, and mature codebase
expected_outcome: pass
---

# Task: SaaS Analytics Platform — Full Business Analysis

## Context

InsightBoard is a B2B SaaS analytics platform that helps product teams understand user behavior, track feature adoption, and measure business KPIs. The product has been in development for 6 months with a small team (2 full-stack engineers, 1 data engineer, 1 designer). It launched a private beta 2 months ago with 35 paying teams. The product targets mid-market companies (50-500 employees) with data-driven product teams. Revenue comes from a tiered subscription model with Stripe billing already integrated.

The analytics space is well-understood with clear incumbents (Mixpanel, Amplitude, Heap, PostHog) and a growing market driven by product-led growth trends. InsightBoard differentiates by offering a self-serve setup with no-code event tracking, built-in A/B testing, and a significantly lower price point than enterprise incumbents.

## Input

**Simulated Codebase Structure:**

```
insightboard/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # GitHub Actions: lint + test + build
│       └── deploy.yml                # Vercel preview + production deploys
├── docker-compose.yml                # PostgreSQL 16, Redis 7, ClickHouse
├── Dockerfile
├── package.json
├── next.config.js
├── prisma/
│   ├── schema.prisma                 # 12 models, 31 relations
│   └── migrations/                   # 22 migration files
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                  # Marketing landing page
│   │   ├── pricing/page.tsx          # 3 tiers: Starter ($29), Growth ($79), Scale ($199)
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   └── callback/page.tsx     # Auth0 callback handler
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx            # Sidebar navigation + workspace selector
│   │   │   ├── overview/page.tsx     # Key metrics dashboard
│   │   │   ├── events/
│   │   │   │   ├── page.tsx          # Event explorer with filters
│   │   │   │   ├── live/page.tsx     # Real-time event stream
│   │   │   │   └── setup/page.tsx    # No-code event setup wizard
│   │   │   ├── funnels/
│   │   │   │   ├── page.tsx          # Funnel builder
│   │   │   │   └── [id]/page.tsx     # Individual funnel analysis
│   │   │   ├── retention/
│   │   │   │   └── page.tsx          # Cohort retention charts
│   │   │   ├── experiments/
│   │   │   │   ├── page.tsx          # A/B test list
│   │   │   │   └── [id]/page.tsx     # Experiment results + stat significance
│   │   │   ├── users/
│   │   │   │   ├── page.tsx          # User list with segments
│   │   │   │   └── [id]/page.tsx     # Individual user timeline
│   │   │   ├── team/
│   │   │   │   ├── page.tsx          # Team management
│   │   │   │   └── invite/page.tsx   # Invite flow with role selection
│   │   │   └── billing/
│   │   │       ├── page.tsx          # Subscription management
│   │   │       └── usage/page.tsx    # Event volume usage meter
│   │   └── api/
│   │       ├── auth/[...auth0]/route.ts
│   │       ├── ingest/
│   │       │   ├── route.ts          # POST — batch event ingestion endpoint
│   │       │   └── sdk/route.ts      # GET — returns JS SDK snippet
│   │       ├── events/
│   │       │   ├── route.ts          # GET — query events with filters
│   │       │   └── aggregate/route.ts # POST — aggregation queries
│   │       ├── funnels/route.ts
│   │       ├── retention/route.ts
│   │       ├── experiments/
│   │       │   ├── route.ts          # CRUD for experiments
│   │       │   └── [id]/results/route.ts  # Statistical analysis endpoint
│   │       ├── users/
│   │       │   ├── route.ts          # Segmented user queries
│   │       │   └── [id]/route.ts
│   │       ├── billing/
│   │       │   ├── checkout/route.ts # Stripe checkout session
│   │       │   ├── portal/route.ts   # Stripe billing portal
│   │       │   ├── webhook/route.ts  # Stripe webhook handler
│   │       │   └── usage/route.ts    # Track event volume for billing
│   │       └── sdk/
│   │           └── route.ts          # Public SDK download endpoint
│   ├── lib/
│   │   ├── prisma.ts
│   │   ├── auth0.ts
│   │   ├── stripe.ts
│   │   ├── redis.ts                  # ioredis — caching + rate limiting
│   │   ├── clickhouse.ts             # ClickHouse client for analytics queries
│   │   ├── posthog.ts                # PostHog for InsightBoard's own product analytics
│   │   ├── statistics.ts             # Chi-squared, z-test for A/B experiments
│   │   └── utils.ts
│   ├── components/
│   │   ├── ui/                       # ~24 shared UI components (shadcn/ui based)
│   │   ├── charts/
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   ├── FunnelChart.tsx
│   │   │   └── RetentionGrid.tsx
│   │   ├── EventExplorer.tsx
│   │   ├── FunnelBuilder.tsx
│   │   ├── ExperimentSetup.tsx
│   │   └── UsageMeter.tsx
│   ├── hooks/
│   │   ├── useAnalytics.ts           # Analytics data fetching hooks
│   │   ├── useRealtime.ts            # SSE-based real-time event stream
│   │   └── useAuth.ts
│   ├── sdk/
│   │   └── insightboard.js           # Client-side JS SDK (~4KB gzipped)
│   └── types/
│       └── index.ts
├── tests/
│   ├── api/
│   │   ├── ingest.test.ts            # 15 tests
│   │   ├── events.test.ts            # 12 tests
│   │   ├── funnels.test.ts           # 8 tests
│   │   ├── experiments.test.ts       # 10 tests
│   │   └── billing.test.ts           # 7 tests
│   └── components/
│       ├── FunnelBuilder.test.tsx     # 6 tests
│       └── EventExplorer.test.tsx     # 5 tests
├── .env.example
├── README.md
└── tsconfig.json
```

**package.json dependencies:**

```json
{
  "name": "insightboard",
  "version": "0.12.4",
  "dependencies": {
    "next": "14.2.3",
    "@auth0/nextjs-auth0": "3.5.0",
    "stripe": "15.1.0",
    "@prisma/client": "5.12.1",
    "prisma": "5.12.1",
    "ioredis": "5.3.2",
    "@clickhouse/client": "0.2.10",
    "posthog-js": "1.105.0",
    "posthog-node": "3.6.0",
    "swr": "2.2.5",
    "zod": "3.23.4",
    "date-fns": "3.6.0",
    "nanoid": "5.0.7",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "tailwindcss": "3.4.3",
    "@radix-ui/react-dialog": "1.0.5",
    "@radix-ui/react-dropdown-menu": "2.0.6",
    "@radix-ui/react-tabs": "1.0.4",
    "@radix-ui/react-tooltip": "1.0.7",
    "recharts": "2.12.2",
    "lucide-react": "0.372.0",
    "class-variance-authority": "0.7.0",
    "clsx": "2.1.0",
    "jstat": "1.9.6",
    "react-hot-toast": "2.4.1"
  },
  "devDependencies": {
    "typescript": "5.4.5",
    "jest": "29.7.0",
    "@testing-library/react": "15.0.2",
    "@types/node": "20.12.7",
    "@types/react": "18.3.1",
    "eslint": "8.57.0",
    "eslint-config-next": "14.2.3"
  }
}
```

**Prisma Schema (key models):**

```prisma
model Workspace {
  id           String   @id @default(cuid())
  name         String
  slug         String   @unique
  createdAt    DateTime @default(now())
  members      WorkspaceMember[]
  projects     Project[]
  subscription Subscription?
  apiKeys      ApiKey[]
  events       Event[]
}

model Event {
  id          String   @id @default(cuid())
  name        String
  properties  Json
  userId      String?
  sessionId   String?
  timestamp   DateTime
  workspace   Workspace @relation(fields: [workspaceId], references: [id])
  workspaceId String
  @@index([workspaceId, name, timestamp])
  @@index([workspaceId, userId])
}

model Experiment {
  id          String   @id @default(cuid())
  name        String
  hypothesis  String?
  status      String   @default("draft") // draft, running, paused, completed
  variants    Json     // [{name: "control", weight: 50}, {name: "variant_a", weight: 50}]
  goalEvent   String
  sampleSize  Int?
  workspace   Workspace @relation(fields: [workspaceId], references: [id])
  workspaceId String
  startedAt   DateTime?
  endedAt     DateTime?
  createdAt   DateTime @default(now())
}

model Subscription {
  id               String   @id @default(cuid())
  stripeCustomerId String   @unique
  stripeSubId      String   @unique
  plan             String   @default("starter") // starter, growth, scale
  status           String   // active, canceled, past_due
  eventLimit       Int      // monthly event cap: 10K, 100K, 1M
  workspace        Workspace @relation(fields: [workspaceId], references: [id])
  workspaceId      String   @unique
  currentPeriodEnd DateTime
}

model ApiKey {
  id          String   @id @default(cuid())
  key         String   @unique
  name        String
  lastUsedAt  DateTime?
  workspace   Workspace @relation(fields: [workspaceId], references: [id])
  workspaceId String
  createdAt   DateTime @default(now())
}
```

**Pricing tiers (from pricing/page.tsx):**

| Feature | Starter ($29/mo) | Growth ($79/mo) | Scale ($199/mo) |
|---------|-------------------|-----------------|-----------------|
| Events/month | 10,000 | 100,000 | 1,000,000 |
| Team members | 3 | 10 | Unlimited |
| Funnels | 5 | 20 | Unlimited |
| Retention cohorts | Basic | Advanced | Advanced |
| A/B Testing | No | Yes | Yes |
| Data retention | 3 months | 12 months | 24 months |
| Support | Community | Email | Priority |

**Environment variables (.env.example):**

```bash
DATABASE_URL="postgresql://insightboard:password@localhost:5432/insightboard"
REDIS_URL="redis://localhost:6379"
CLICKHOUSE_URL="http://localhost:8123"
AUTH0_SECRET="..."
AUTH0_BASE_URL="http://localhost:3000"
AUTH0_ISSUER_BASE_URL="https://insightboard-dev.us.auth0.com"
AUTH0_CLIENT_ID="..."
AUTH0_CLIENT_SECRET="..."
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
NEXT_PUBLIC_POSTHOG_KEY="phc_..."
NEXT_PUBLIC_POSTHOG_HOST="https://app.posthog.com"
```

**Key Technical Details:**
- ClickHouse used as the analytics data store for high-volume event queries (separate from Postgres for metadata)
- JS SDK (~4KB) can be embedded via script tag or npm package for event collection
- Server-Sent Events (SSE) used for real-time event stream (not WebSockets)
- Usage-based billing gating: events beyond plan limit return 429 on ingest endpoint
- Basic rate limiting implemented via Redis on the ingest endpoint (1000 events/sec per API key)

## Expected Behaviors

- Produces a Market Opportunity Score in the 6-8/10 range (attractive market, but crowded)
- Estimates TAM for the product analytics market at $5-15B with clear methodology
- Narrows SAM to mid-market product teams with data-driven culture
- Identifies and names specific competitors: Mixpanel, Amplitude, Heap, PostHog, Google Analytics 4, Pendo, FullStory
- Recognizes PostHog as the closest competitor (open-source, similar positioning, lower price point)
- Identifies competitive moat as Weak to Moderate (price differentiation + no-code setup + integrated A/B testing, but easily replicable)
- Notes the pricing strategy is aggressive and below market, discusses sustainability
- Identifies usage-based event volume gating as a smart monetization lever
- Recognizes the client-side SDK as a distribution advantage (lightweight, embeddable)
- Produces a 90-day GTM plan with specific milestones
- Provides bear/base/bull revenue projections
- References specific files and code patterns in analysis (e.g., pricing page, Stripe webhook, ClickHouse queries, SDK)

## Success Criteria

- [ ] TAM/SAM/SOM estimates provided with clear methodology and reasoning
- [ ] At least 4 competitors named with specific differentiation analysis for each
- [ ] Pricing analysis discusses the tradeoff between aggressive pricing and margin sustainability
- [ ] Product-Market Fit assessment references code evidence (event models, A/B testing, SDK, pricing tiers)
- [ ] Go-to-Market plan includes specific channels and a 90-day timeline
- [ ] Revenue projections include at least two scenarios (bear/base or base/bull)
- [ ] Moat assessment is honest (not inflated) and discusses defensibility risks
- [ ] ClickHouse architecture recognized as a technical differentiator for query performance
- [ ] Risk section identifies at least 3 specific business risks with mitigations

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT rate Market Opportunity Score as 9/10 or 10/10 — the market is attractive but crowded with well-funded competitors
- [ ] Should NOT present market size numbers without explaining the estimation methodology
- [ ] Should NOT ignore PostHog as a competitor (it is the most directly comparable open-source alternative)
- [ ] Should NOT claim strong moat — price advantage and no-code setup are replicable
- [ ] Should NOT produce analysis that could be written without reading the codebase (must reference specific files, routes, models)
- [ ] Should NOT skip A/B testing as a differentiating feature (not all competitors include it natively)
- [ ] Should NOT provide a single-point revenue forecast without bear/base/bull range
