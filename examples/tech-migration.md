# Example: Technical Migration Decision

## Scenario

Your team is considering migrating from a monolithic Rails application to a microservices architecture with Go and Kubernetes. The monolith serves 50K users and is showing scaling pain.

## Prompt

```
Run a full OmniLabs strategic analysis of this project.

Context: We're considering migrating from our Rails monolith to Go microservices on Kubernetes. Current system serves 50K users with increasing latency issues. Team of 8 engineers, 3 of whom know Go.

Key questions to address:
- Is microservices the right architectural move, or are there simpler fixes?
- What's the true total cost of migration (not just infrastructure)?
- Will this migration create business risk during the transition?
- What are we likely underestimating about this migration?
```

## Expected Output

The OmniLabs Report will include:

- **Business**: Impact of migration on feature velocity, competitive risk during transition period, customer churn risk from potential instability
- **Financial**: Full migration TCO (team ramp-up, dual-running costs, K8s operational overhead), cost comparison: optimized monolith vs microservices at 50K/200K/1M users
- **Technical**: Current monolith bottleneck analysis (is it actually the architecture or just specific queries?), microservices readiness assessment, team capability gap analysis
- **Devil's Advocate**: "What if the scaling issue is a database problem, not an architecture problem?", pre-mortem of migration failure (team burnout, half-migrated state), Strangler Fig vs Big Bang risk comparison
- **Synthesis**: CONDITIONAL GO with specific prerequisites (team training, pilot service selection), phased roadmap starting with the least risky service extraction
