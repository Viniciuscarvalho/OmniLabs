---
agent: business-product
type: edge-case
description: Nearly empty repository with minimal code — tests agent adaptability to sparse information
expected_outcome: partial
---

# Task: Empty Repository — Minimal Information Analysis

## Context

A developer has created a brand-new project repository with only boilerplate setup. There is a README with a vague one-line description, a package.json with minimal dependencies (express, cors, dotenv), and a single index.js file that serves a "Hello World" route. No database, no authentication, no business logic, no frontend, no tests, no deployment configuration. The README says "TaskMaster — a task management API" but the code contains nothing beyond the initial scaffold.

This scenario tests how the business-product agent handles extreme information scarcity. The agent should not fabricate analysis but should instead clearly state what it can and cannot determine, provide conditional assessments, and recommend what to build first from a business perspective.

## Input

**Simulated Codebase Structure:**

```
taskmaster/
├── package.json
├── index.js
├── .gitignore
├── .env.example
└── README.md
```

**package.json:**

```json
{
  "name": "taskmaster",
  "version": "0.1.0",
  "description": "A task management API",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "express": "4.18.2",
    "cors": "2.8.5",
    "dotenv": "16.4.1"
  },
  "devDependencies": {
    "nodemon": "3.0.3"
  }
}
```

**index.js:**

```javascript
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to TaskMaster API' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

**.env.example:**

```bash
PORT=3000
```

**README.md:**

```markdown
# TaskMaster

A task management API.

## Getting Started

npm install
npm run dev
```

**Key observations about the codebase:**
- Total lines of code: approximately 25 (index.js)
- No database dependency or ORM
- No authentication or authorization
- No task-related models, routes, or logic
- No tests
- No frontend
- No CI/CD
- No deployment configuration
- No Docker setup
- The name "TaskMaster" and description "task management API" are the only product clues
- Express + CORS + dotenv is the most generic Node.js starter possible

## Expected Behaviors

- Clearly acknowledges the repository is in its earliest stage with no meaningful business logic
- States explicitly what CANNOT be assessed (competitive positioning, revenue model, PMF indicators) due to lack of implementation
- Provides conditional analysis: "IF this becomes a task management tool, THEN the market looks like..."
- References the actual code to confirm the absence of features (no models, no auth, no task routes)
- Identifies the task management space broadly but qualifies that the product direction is unknown
- Recommends what to build first from a business-viability perspective
- Adjusts scoring and confidence levels significantly downward
- Does not abandon the analysis entirely — provides a useful framework for moving forward

## Success Criteria

- [ ] Explicitly states the repository contains no business logic beyond a health check
- [ ] Clearly distinguishes between what can and cannot be assessed
- [ ] Uses conditional language ("if targeting X, then..." rather than definitive claims)
- [ ] References actual code artifacts (index.js, package.json) to support the finding of minimal implementation
- [ ] Provides a high-level market overview of task management IF that is the intended direction
- [ ] Recommends a prioritized list of what to build first (from a business perspective, not just technical)
- [ ] Market Opportunity Score is very low (1-3/10) or explicitly marked as "insufficient data"
- [ ] Analysis is still useful — provides a framework or decision tree for the developer to follow

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT fabricate features, integrations, or capabilities that do not exist in the code
- [ ] Should NOT provide a detailed competitor analysis as if the product direction were confirmed
- [ ] Should NOT estimate TAM/SAM/SOM with any precision — there is no product to measure against
- [ ] Should NOT assign a Market Opportunity Score above 3/10 without heavy caveats
- [ ] Should NOT generate a 90-day GTM plan — there is no product to take to market
- [ ] Should NOT present pricing recommendations as if a billable product existed
- [ ] Should NOT ignore the emptiness and produce a generic task-management market report
- [ ] Should NOT produce analysis longer than the codebase warrants — brevity is appropriate here
