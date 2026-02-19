Use the financial-cost agent to perform a detailed financial and cost modeling analysis of this project.

Begin by reading the entire codebase with a focus on: infrastructure configuration files (Dockerfiles, Kubernetes manifests, cloud configs), third-party service integrations (APIs, SaaS tools, databases, queues, CDNs), backend logic that implies compute or data intensity, and any existing billing or usage-tracking code. Your goal is to build a rigorous cost model from first principles.

Your analysis must cover:

**Infrastructure Inventory**
- Catalog every infrastructure component present or implied in the codebase: compute (servers, containers, serverless functions), storage (databases, object storage, caches), networking (CDN, egress, load balancers), and managed services.
- For each component, identify the pricing model (per-request, per-GB, per-hour, flat fee) and the primary cost driver.

**Third-Party & API Cost Mapping**
- List every external service integration found in the code (payment processors, AI APIs, email/SMS providers, auth, monitoring, etc.).
- Estimate the cost per unit of usage for each, and identify which services are likely to become cost-dominant at scale.

**Total Cost of Ownership (TCO) Modeling**
Build a detailed TCO model at four scales: **1K users, 10K users, 100K users, and 1M users**.

For each scale, calculate:
- Infrastructure costs (broken down by component)
- Third-party service costs (broken down by provider)
- Engineering and operational headcount costs (estimate based on system complexity)
- Support and tooling costs
- Total monthly and annual cost
- Cost per user (CPU — Cost Per User)
- Cost per transaction or core action (if identifiable from the code)

**Unit Economics Analysis**
- What is the estimated Cost of Goods Sold (COGS) per user or per transaction?
- What minimum price point would be required to achieve 50%, 60%, and 70% gross margins at each scale?
- At what scale does the unit economics become favorable, and what are the key inflection points?

**Cost Optimization Opportunities**
- Identify the top 3–5 highest-leverage cost reduction opportunities with specific architectural or vendor changes.
- Estimate the potential savings for each optimization.
- Highlight any architectural decisions in the code that are unnecessarily expensive and could be rearchitected.

**Financial Risk Assessment**
- Which cost components have the highest variance or unpredictability (e.g., AI API costs, egress fees, per-seat SaaS)?
- What is the worst-case monthly burn scenario at each scale if usage spikes unexpectedly?
- Are there any vendor lock-in risks that could create pricing leverage against the company in the future?

**Funding & Runway Implications**
- Based on the cost model, how much runway would a $500K, $1M, and $2M seed raise provide at each user scale?
- What are the key cost milestones the team should plan for?

All cost estimates must reference specific files, services, or patterns observed in the codebase. State your assumptions explicitly and flag where estimates carry high uncertainty.