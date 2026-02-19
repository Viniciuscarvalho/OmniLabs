Use the technical-architecture agent to perform a comprehensive technical architecture review of this project.

Read the entire codebase in depth: directory structure, framework choices, data models, API design, authentication flows, background job systems, caching strategies, deployment configuration, test coverage, and dependency manifests. Your review must be evidence-based — every finding must cite specific files, functions, patterns, or configurations from the actual code.

Score the architecture across the following six dimensions, each on a scale of 1–10, with a detailed justification and supporting evidence for the score:

---

**1. Scalability (1–10)**
- Can the system handle 10x its current implied load without a rewrite?
- Evaluate: horizontal vs. vertical scaling strategies, statelessness of services, database bottlenecks, caching layers, async processing, and queue usage.
- Identify specific bottlenecks that would break first under load.

**2. Reliability & Fault Tolerance (1–10)**
- How resilient is the system to partial failures?
- Evaluate: error handling patterns, retry logic, circuit breakers, graceful degradation, database transaction handling, and idempotency guarantees.
- Identify single points of failure and assess their blast radius.

**3. Maintainability & Code Quality (1–10)**
- How easy is it for a new engineer to understand, modify, and extend this codebase safely?
- Evaluate: separation of concerns, abstraction quality, code duplication, naming conventions, test coverage (unit, integration, e2e), documentation, and adherence to established patterns.
- Flag any areas of high cognitive complexity or technical debt that will slow the team down.

**4. Security Posture (1–10)**
- How resistant is the system to common attack vectors?
- Evaluate: authentication and authorization implementation, input validation and sanitization, secret management, dependency vulnerabilities, API security (rate limiting, CORS, CSRF), data encryption at rest and in transit, and least privilege principles.
- Call out any critical vulnerabilities that require immediate attention.

**5. Observability (1–10)**
- How well can engineers understand system behavior in production?
- Evaluate: logging strategy (structured vs. unstructured, log levels, PII in logs), metrics instrumentation (RED metrics: Rate, Errors, Duration), distributed tracing, alerting configuration, and dashboards.
- Identify what would be invisible or ambiguous during a production incident.

**6. Operability & Developer Experience (1–10)**
- How easy is it to deploy, operate, debug, and iterate on this system?
- Evaluate: local development setup, CI/CD pipeline maturity, environment configuration management, migration strategies, feature flag usage, rollback capabilities, and on-call ergonomics.
- Identify operational toil that is likely to become painful as the team and system grow.

---

**Architecture Summary**
After the six dimensions, provide:
- An overall architectural pattern classification (e.g., monolith, modular monolith, microservices, serverless, event-driven) and whether this is the right pattern for the product's current stage.
- A **Top 5 Priority Issues** list — the specific architectural problems that carry the highest risk or debt and should be addressed first.
- A **Quick Wins** list — changes that could be made in under a week that would meaningfully improve the architecture score.
- A **6-Month Architecture Roadmap** — the architectural investments that will matter most as the product scales.