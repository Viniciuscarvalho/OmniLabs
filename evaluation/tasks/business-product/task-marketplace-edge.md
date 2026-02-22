---
agent: business-product
type: edge-case
description: Two-sided marketplace for freelance designers with missing payment flow and cold-start challenges
expected_outcome: partial
---

# Task: Two-Sided Designer Marketplace — Incomplete Transaction Layer

## Context

DesignBridge is a two-sided marketplace connecting freelance graphic designers with small businesses that need design work (logos, social media assets, presentations, packaging). The platform has been in development for 3 months by a solo founder/developer. Seller (designer) profiles and buyer (business) browsing are functional, but there is NO payment or transaction flow built yet. The product has 45 designer profiles created during a manual onboarding campaign, and roughly 120 registered business accounts from a waitlist, but zero completed transactions.

This scenario specifically tests the agent's ability to recognize two-sided marketplace dynamics, identify the chicken-and-egg cold-start problem, and adapt its analysis when a critical business component (payments/transactions) is entirely absent from the codebase.

## Input

**Simulated Codebase Structure:**

```
designbridge/
├── .github/
│   └── workflows/
│       └── ci.yml                     # Lint + test only
├── docker-compose.yml                 # PostgreSQL 15, app
├── Dockerfile                         # Node 20 Alpine
├── package.json
├── next.config.js
├── prisma/
│   ├── schema.prisma                  # 8 models, 15 relations
│   └── migrations/                    # 9 migration files
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                   # Landing page with "Coming Soon" pricing section
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx        # Signup with role selection (designer | business)
│   │   ├── (marketplace)/
│   │   │   ├── layout.tsx
│   │   │   ├── browse/page.tsx        # Browse designers with filters (style, price range, rating)
│   │   │   ├── designers/
│   │   │   │   ├── page.tsx           # Designer directory
│   │   │   │   └── [slug]/page.tsx    # Individual designer portfolio page
│   │   │   ├── categories/
│   │   │   │   └── [category]/page.tsx # Category-filtered browse
│   │   │   └── search/page.tsx        # Full-text search across designers
│   │   ├── (dashboard)/
│   │   │   ├── designer/
│   │   │   │   ├── profile/page.tsx   # Designer profile editor
│   │   │   │   ├── portfolio/page.tsx # Upload and manage portfolio pieces
│   │   │   │   ├── services/page.tsx  # Define offered services and pricing
│   │   │   │   └── analytics/page.tsx # Profile views, saves (no revenue analytics)
│   │   │   └── business/
│   │   │       ├── saved/page.tsx     # Saved/favorited designers
│   │   │       ├── projects/page.tsx  # Draft project briefs (no submission flow)
│   │   │       └── messages/page.tsx  # Direct messages to designers
│   │   └── api/
│   │       ├── auth/[...nextauth]/route.ts  # NextAuth.js credentials + Google OAuth
│   │       ├── designers/
│   │       │   ├── route.ts           # GET (list with filters), POST (create profile)
│   │       │   └── [id]/
│   │       │       ├── route.ts       # GET, PUT designer profile
│   │       │       └── portfolio/route.ts  # GET, POST portfolio items
│   │       ├── categories/route.ts    # GET categories
│   │       ├── search/route.ts        # Full-text search
│   │       ├── messages/
│   │       │   ├── route.ts           # GET conversations, POST new message
│   │       │   └── [id]/route.ts      # GET conversation thread
│   │       ├── projects/
│   │       │   └── route.ts           # GET, POST draft project briefs
│   │       └── favorites/route.ts     # POST toggle favorite designer
│   ├── lib/
│   │   ├── prisma.ts
│   │   ├── auth.ts                    # NextAuth config
│   │   ├── upload.ts                  # S3 upload for portfolio images
│   │   └── utils.ts
│   ├── components/
│   │   ├── ui/                        # ~14 shared UI components
│   │   ├── DesignerCard.tsx
│   │   ├── PortfolioGrid.tsx
│   │   ├── ServicePriceList.tsx
│   │   ├── MessageThread.tsx
│   │   ├── CategoryFilter.tsx
│   │   └── SearchBar.tsx
│   └── types/
│       └── index.ts
├── tests/
│   ├── api/
│   │   ├── designers.test.ts          # 8 tests
│   │   ├── search.test.ts             # 5 tests
│   │   └── messages.test.ts           # 4 tests
│   └── components/
│       └── DesignerCard.test.tsx       # 3 tests
├── .env.example
└── README.md
```

**package.json dependencies:**

```json
{
  "name": "designbridge",
  "version": "0.4.1",
  "dependencies": {
    "next": "14.1.4",
    "next-auth": "4.24.6",
    "@prisma/client": "5.10.2",
    "prisma": "5.10.2",
    "@aws-sdk/client-s3": "3.525.0",
    "@aws-sdk/s3-request-presigner": "3.525.0",
    "swr": "2.2.4",
    "zod": "3.22.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "tailwindcss": "3.4.1",
    "lucide-react": "0.344.0",
    "clsx": "2.1.0",
    "react-hot-toast": "2.4.1",
    "react-dropzone": "14.2.3",
    "sharp": "0.33.2"
  }
}
```

**Prisma Schema (key models):**

```prisma
model User {
  id            String   @id @default(cuid())
  email         String   @unique
  name          String
  role          String   // "designer" | "business"
  avatarUrl     String?
  createdAt     DateTime @default(now())
  designerProfile DesignerProfile?
  businessProfile BusinessProfile?
  sentMessages    Message[] @relation("sender")
  receivedMessages Message[] @relation("receiver")
}

model DesignerProfile {
  id          String   @id @default(cuid())
  slug        String   @unique
  bio         String?
  tagline     String?
  location    String?
  styles      String[] // ["minimalist", "bold", "retro", "corporate"]
  hourlyRate  Decimal?
  available   Boolean  @default(true)
  portfolio   PortfolioItem[]
  services    Service[]
  favorites   Favorite[]
  user        User     @relation(fields: [userId], references: [id])
  userId      String   @unique
  categories  Category[]
  @@index([available])
}

model Service {
  id          String   @id @default(cuid())
  name        String   // "Logo Design", "Social Media Pack", etc.
  description String?
  price       Decimal  // Listed price (not enforced anywhere)
  turnaround  Int      // days
  designer    DesignerProfile @relation(fields: [designerId], references: [id])
  designerId  String
}

model PortfolioItem {
  id          String   @id @default(cuid())
  title       String
  description String?
  imageUrl    String   // S3 URL
  category    String?
  designer    DesignerProfile @relation(fields: [designerId], references: [id])
  designerId  String
  createdAt   DateTime @default(now())
}

model Message {
  id          String   @id @default(cuid())
  content     String
  sender      User     @relation("sender", fields: [senderId], references: [id])
  senderId    String
  receiver    User     @relation("receiver", fields: [receiverId], references: [id])
  receiverId  String
  read        Boolean  @default(false)
  createdAt   DateTime @default(now())
}

model ProjectBrief {
  id          String   @id @default(cuid())
  title       String
  description String
  budget      Decimal?
  deadline    DateTime?
  status      String   @default("draft") // only "draft" — no "submitted", "accepted", "in_progress"
  business    BusinessProfile @relation(fields: [businessId], references: [id])
  businessId  String
  createdAt   DateTime @default(now())
  // NOTE: No relation to Designer — briefs cannot be assigned/sent
}

model Favorite {
  id         String   @id @default(cuid())
  business   BusinessProfile @relation(fields: [businessId], references: [id])
  businessId String
  designer   DesignerProfile @relation(fields: [designerId], references: [id])
  designerId String
  createdAt  DateTime @default(now())
  @@unique([businessId, designerId])
}
```

**Key observations about the codebase:**
- NO Stripe, PayPal, or any payment library in dependencies
- NO Order, Transaction, Payment, or Invoice model in the schema
- ProjectBrief has only "draft" status — no submission or acceptance flow
- Service model has a `price` field but it is purely informational (no checkout flow)
- Messages exist between users but there is no project-scoped communication
- Landing page has a "Coming Soon" pricing section (no actual pricing tiers)
- designer/analytics page shows profile views and saves only — no revenue data

## Expected Behaviors

- Immediately identifies the absence of a payment/transaction layer as the critical gap
- Frames analysis around two-sided marketplace dynamics (not standard SaaS)
- Identifies the chicken-and-egg / cold-start problem explicitly
- Recommends a supply-side-first strategy (designers are the scarce resource)
- Discusses marketplace economics: take rate, GMV, network effects, liquidity
- Recognizes that the Service price field is cosmetic without an actual checkout flow
- Notes that ProjectBrief is a dead-end (draft status only, no assignment to designers)
- Discusses trust/safety mechanisms needed (escrow, dispute resolution, reviews)
- Identifies relevant marketplace competitors: Fiverr, 99designs, Dribbble Pro, Toptal, DesignCrowd
- Provides a phased roadmap prioritizing transaction flow above all else
- Adjusts Market Opportunity Score downward due to incomplete core functionality

## Success Criteria

- [ ] Explicitly identifies missing payment/transaction infrastructure as the primary blocker
- [ ] Analyzes the platform as a marketplace (not a SaaS) and discusses two-sided dynamics
- [ ] Names the cold-start / chicken-and-egg problem and recommends a strategy to solve it
- [ ] Discusses marketplace-specific metrics: GMV, take rate, liquidity, supply/demand ratio
- [ ] Identifies competitors in the design marketplace space (Fiverr, 99designs, Dribbble, etc.)
- [ ] References specific code gaps: no payment dependency, ProjectBrief dead-end, Service.price is unenforced
- [ ] Recommends trust mechanisms (escrow, reviews, dispute resolution) as requirements
- [ ] Market Opportunity Score is tempered (not above 6/10) given missing transaction layer

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT treat this as a standard SaaS product with subscription revenue
- [ ] Should NOT ignore the two-sided marketplace dynamics (network effects, take rate, liquidity)
- [ ] Should NOT assume a payment flow exists just because Service has a price field
- [ ] Should NOT provide revenue projections based on subscription pricing (there is no subscription)
- [ ] Should NOT score Market Opportunity above 7/10 without acknowledging the massive gap in core functionality
- [ ] Should NOT skip the cold-start problem — it is the defining challenge for any marketplace
- [ ] Should NOT recommend a go-to-market strategy that ignores supply acquisition (designer recruitment)
