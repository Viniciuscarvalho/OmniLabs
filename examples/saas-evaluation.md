# Example: SaaS Product Evaluation

## Scenario

You're evaluating whether to invest engineering resources into a B2B SaaS analytics platform. The codebase exists but hasn't launched yet.

## Prompt

```
Run a full OmniLabs strategic analysis of this project.

Context: This is a B2B SaaS analytics platform targeting mid-market companies (50-500 employees). We've built an MVP and need to decide whether to go all-in on launch or pivot.

Key questions to address:
- Is there real product-market fit based on what the code actually delivers?
- What will it cost to operate at 10K and 100K users?
- Can the architecture handle enterprise customers with strict SLAs?
- What are we not seeing that could kill us?
```

## Expected Output

The OmniLabs Report will include:

- **Business**: TAM/SAM/SOM for B2B analytics, competitor map (Mixpanel, Amplitude, Heap), PMF assessment based on actual feature completeness
- **Financial**: Infrastructure costs modeled from the actual tech stack, scaling curves, enterprise pricing viability
- **Technical**: Architecture scores across 6 dimensions, bottlenecks for enterprise SLA compliance, security gaps for B2B
- **Devil's Advocate**: Challenges to market size assumptions, pre-mortem of launch failure scenarios, blind spots in the competitive analysis
- **Synthesis**: GO/NO-GO decision with conditions, 90-day roadmap prioritizing the highest-impact gaps
