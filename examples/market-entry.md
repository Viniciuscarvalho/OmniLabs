# Example: New Market Entry

## Scenario

Your developer tools company (CLI-based code analysis tool) is considering expanding from individual developers to enterprise teams. The product exists and has 5K individual users.

## Prompt

```
Run a full OmniLabs strategic analysis of this project.

Context: We have a CLI code analysis tool with 5K individual developer users (freemium model). We're considering building enterprise features (team dashboards, SSO, audit logs, compliance reporting) to move upmarket.

Key questions to address:
- Is the enterprise market a natural extension or a different product entirely?
- What's the investment required to become enterprise-ready?
- Does our current architecture support multi-tenancy and enterprise requirements?
- What are the hidden costs and risks of going enterprise?
```

## Expected Output

The OmniLabs Report will include:

- **Business**: Enterprise developer tools TAM, competitive landscape (SonarQube, Snyk, etc.), PLG-to-enterprise conversion playbook, pricing strategy (per-seat vs per-repo vs usage)
- **Financial**: Engineering investment for enterprise features (SSO, RBAC, audit logs, SOC2), enterprise sales cycle cost (AE hire, SE support, legal/procurement), break-even analysis at different ACV tiers
- **Technical**: Multi-tenancy readiness assessment, SSO/SAML integration complexity, data isolation and compliance architecture gaps, API rate limiting for enterprise accounts
- **Devil's Advocate**: "Enterprise is a different business, not a feature set", risk of alienating individual users, opportunity cost of not doubling down on PLG, enterprise sales cycle length vs runway
- **Synthesis**: CONDITIONAL GO with phased approach — start with Team tier (5-50 seats) before full Enterprise, specific technical prerequisites, 90-day roadmap starting with the highest-leverage enterprise feature
