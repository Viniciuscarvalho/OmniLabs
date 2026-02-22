---
agent: technical-architecture
type: happy-path
description: Well-structured Rails monolith with strong testing and CI practices
expected_outcome: pass
---

# Task: Well-Structured Rails Monolith

## Context

A 2-year-old Ruby on Rails monolith serving a B2B invoicing platform called "InvoiceForge." The team of 4 engineers has maintained disciplined engineering practices since day one. The application handles ~3,000 active businesses generating ~50,000 invoices/month. The codebase follows conventional Rails patterns and the team has resisted premature optimization while keeping quality high.

## Input

**Project**: InvoiceForge
**Type**: B2B SaaS Invoicing Platform
**Stage**: Growth (2 years in production, ~3,000 paying customers)
**Team**: 4 full-stack engineers, 1 product manager

### Simulated Codebase Structure

```
invoiceforge/
├── .github/
│   └── workflows/
│       ├── ci.yml                     # GitHub Actions: RSpec, RuboCop, Brakeman
│       └── dependabot.yml             # Weekly dependency updates
├── Gemfile
├── Gemfile.lock
├── Dockerfile                         # Ruby 3.2, multi-stage build
├── docker-compose.yml                 # PostgreSQL 15, Redis 7, app, Sidekiq
├── config/
│   ├── database.yml                   # PostgreSQL with connection pooling (pgbouncer)
│   ├── routes.rb                      # RESTful routes, API namespace
│   ├── initializers/
│   │   ├── sidekiq.rb                 # Sidekiq config with retry policies
│   │   ├── lograge.rb                 # Structured JSON logging
│   │   ├── stripe.rb                  # Stripe SDK initialization
│   │   └── sentry.rb                  # Error tracking
│   └── environments/
│       ├── production.rb              # Force SSL, log level, caching
│       └── staging.rb
├── app/
│   ├── controllers/
│   │   ├── application_controller.rb  # Auth filters, error handling
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── invoices_controller.rb    # CRUD + PDF generation
│   │   │       ├── clients_controller.rb     # Client management
│   │   │       ├── payments_controller.rb    # Stripe payment processing
│   │   │       └── webhooks_controller.rb    # Stripe webhooks
│   │   └── dashboard_controller.rb           # Dashboard analytics
│   ├── models/
│   │   ├── user.rb                    # Devise auth, has_many :organizations
│   │   ├── organization.rb           # Multi-tenancy scope
│   │   ├── invoice.rb                # State machine (draft/sent/paid/overdue)
│   │   ├── client.rb                 # Belongs to organization
│   │   ├── payment.rb                # Stripe payment records
│   │   └── line_item.rb              # Invoice line items
│   ├── services/
│   │   ├── invoice_pdf_service.rb    # Prawn PDF generation
│   │   ├── payment_processor.rb      # Stripe charge logic
│   │   ├── overdue_notifier.rb       # Email notifications for overdue invoices
│   │   └── analytics_service.rb      # Revenue calculations
│   ├── jobs/
│   │   ├── send_invoice_job.rb       # Sidekiq: email invoice to client
│   │   ├── generate_pdf_job.rb       # Sidekiq: async PDF generation
│   │   ├── overdue_check_job.rb      # Sidekiq: daily overdue scan (cron)
│   │   └── stripe_sync_job.rb        # Sidekiq: sync Stripe state
│   ├── mailers/
│   │   ├── invoice_mailer.rb         # Invoice delivery emails
│   │   └── notification_mailer.rb    # System notifications
│   └── views/
│       ├── layouts/
│       └── api/                       # Jbuilder JSON templates
├── db/
│   ├── schema.rb
│   └── migrate/                       # 42 migration files
├── spec/
│   ├── rails_helper.rb
│   ├── spec_helper.rb
│   ├── models/
│   │   ├── invoice_spec.rb            # 28 tests
│   │   ├── user_spec.rb               # 15 tests
│   │   ├── organization_spec.rb       # 12 tests
│   │   ├── payment_spec.rb            # 18 tests
│   │   └── client_spec.rb             # 10 tests
│   ├── controllers/
│   │   ├── invoices_controller_spec.rb  # 22 tests
│   │   ├── payments_controller_spec.rb  # 16 tests
│   │   └── webhooks_controller_spec.rb  # 11 tests
│   ├── services/
│   │   ├── invoice_pdf_service_spec.rb  # 8 tests
│   │   ├── payment_processor_spec.rb    # 14 tests
│   │   └── overdue_notifier_spec.rb     # 9 tests
│   ├── jobs/
│   │   ├── send_invoice_job_spec.rb     # 6 tests
│   │   └── overdue_check_job_spec.rb    # 7 tests
│   ├── requests/
│   │   ├── invoices_request_spec.rb     # 18 tests (integration)
│   │   └── payments_request_spec.rb     # 12 tests (integration)
│   └── factories/                       # FactoryBot factories for all models
├── .rubocop.yml                         # Strict RuboCop config
├── .rspec
├── Brakeman config                      # Security static analysis
└── README.md
```

### Key Configuration Details

**Gemfile (key dependencies)**:
```ruby
gem 'rails', '~> 7.1.2'
gem 'pg', '~> 1.5'
gem 'redis', '~> 5.0'
gem 'sidekiq', '~> 7.2'
gem 'devise', '~> 4.9'
gem 'stripe', '~> 10.0'
gem 'prawn', '~> 2.4'         # PDF generation
gem 'lograge', '~> 0.14'      # Structured logging
gem 'sentry-ruby', '~> 5.15'  # Error tracking
gem 'rack-attack', '~> 6.7'   # Rate limiting
gem 'pundit', '~> 2.3'        # Authorization
gem 'jbuilder', '~> 2.11'

group :test do
  gem 'rspec-rails', '~> 6.1'
  gem 'factory_bot_rails'
  gem 'shoulda-matchers'
  gem 'simplecov', require: false
  gem 'webmock'
  gem 'vcr'
end
```

**CI Configuration (.github/workflows/ci.yml)**:
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
      redis:
        image: redis:7
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.2
          bundler-cache: true
      - run: bundle exec rails db:create db:schema:load
      - run: bundle exec rspec --format documentation
      - run: bundle exec rubocop --parallel
      - run: bundle exec brakeman --no-pager -q
```

**Database schema highlights**:
```ruby
# Proper indexes on foreign keys and commonly queried columns
add_index :invoices, :organization_id
add_index :invoices, :client_id
add_index :invoices, :status
add_index :invoices, [:organization_id, :status]
add_index :invoices, [:organization_id, :created_at]
add_index :payments, :stripe_payment_intent_id, unique: true
add_index :organizations, :stripe_customer_id, unique: true
```

**Lograge configuration**:
```ruby
# config/initializers/lograge.rb
Rails.application.configure do
  config.lograge.enabled = true
  config.lograge.formatter = Lograge::Formatters::Json.new
  config.lograge.custom_payload do |controller|
    {
      user_id: controller.current_user&.id,
      organization_id: controller.current_organization&.id,
      request_id: controller.request.request_id
    }
  end
end
```

**Rack::Attack configuration**:
```ruby
# config/initializers/rack_attack.rb
Rack::Attack.throttle("api/ip", limit: 300, period: 5.minutes) do |req|
  req.ip if req.path.start_with?("/api/")
end
Rack::Attack.throttle("login/ip", limit: 5, period: 20.seconds) do |req|
  req.ip if req.path == "/users/sign_in" && req.post?
end
```

**Test coverage**: 80% line coverage (SimpleCov), 206 total specs. Coverage breakdown: Models 92%, Controllers 78%, Services 85%, Jobs 70%.

**Deployment**: Docker + docker-compose on a single DigitalOcean droplet (8GB RAM, 4 vCPU). Manual deploys via SSH + `docker-compose pull && docker-compose up -d`.

## Expected Behaviors

- Assigns balanced scores across 6 dimensions, with no dimension receiving a perfect 10/10
- Recognizes the monolith architecture as appropriate for the current team size (4 engineers) and scale (~3,000 customers)
- Praises the high test coverage (80%) and comprehensive RSpec suite with proper factories
- Acknowledges the CI pipeline quality (RSpec + RuboCop + Brakeman)
- Identifies structured logging (Lograge) and error tracking (Sentry) as positive signals for observability
- Flags the single-server deployment as a vertical scaling limitation
- Notes the absence of horizontal scaling, load balancing, or auto-scaling
- Identifies that Docker Compose on a single droplet is not production-grade for growth stage
- Calls out the lack of a CD pipeline (manual SSH deploys)
- Recognizes Rack::Attack rate limiting and Pundit authorization as security strengths

## Success Criteria

- [ ] Scalability score is in the 4-6/10 range, reflecting single-server limitation with clean architecture that could be scaled
- [ ] Reliability score is in the 5-7/10 range, acknowledging Sidekiq retry logic but noting no health checks or circuit breakers
- [ ] Maintainability score is in the 7-8/10 range, reflecting strong test coverage, clean MVC, and good tooling
- [ ] Security score is in the 6-8/10 range, reflecting Devise + Pundit + Rack::Attack + Brakeman but noting shared DB multi-tenancy
- [ ] Observability score is in the 5-7/10 range, reflecting Lograge + Sentry but noting no metrics collection or dashboards
- [ ] Operability score is in the 4-6/10 range, reflecting CI pipeline but noting manual deploys and no IaC
- [ ] Architecture evolution roadmap suggests incremental improvements, not a rewrite
- [ ] Identifies specific scaling bottleneck: single PostgreSQL instance with connection pooling limits
- [ ] Mentions the lack of database read replicas as a future scaling concern

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT recommend microservices migration for a well-built monolith at this scale
- [ ] Should NOT give all-10 scores or all-high scores across every dimension
- [ ] Should NOT ignore the manual deployment process as a risk
- [ ] Should NOT overlook the single-server SPOF (single point of failure)
- [ ] Should NOT dismiss the architecture as "legacy" or "outdated" just because it is a monolith
- [ ] Should NOT recommend Kubernetes for a 4-person team with 3,000 customers
