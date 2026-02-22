---
agent: technical-architecture
type: negative
description: Node.js Express app with zero tests, no CI, and custom JWT auth
expected_outcome: flag-issues
---

# Task: Node.js Express App with Zero Tests and No CI

## Context

A solo developer built an e-commerce API called "QuickShop" over 3 months as a freelance project. The API powers a React Native mobile app for a small retail business. The codebase has zero test files, no testing dependencies, no CI/CD pipeline, no Docker configuration, and uses a custom JWT implementation instead of a vetted authentication library. The application is deployed manually via FTP-style upload to a shared hosting environment. There are 15 API routes handling products, orders, users, and payments.

## Input

**Project**: QuickShop API
**Type**: E-commerce REST API
**Stage**: MVP launched 2 months ago, ~200 active users
**Team**: 1 freelance developer (part-time)

### Simulated Codebase Structure

```
quickshop-api/
├── package.json
├── .eslintrc.json                     # Basic ESLint config (extends recommended)
├── .env                               # CONTAINS ACTUAL SECRETS (committed to repo)
├── src/
│   ├── index.js                       # Express app entry point, all middleware here
│   ├── routes/
│   │   ├── auth.js                    # POST /register, POST /login, POST /forgot-password
│   │   ├── products.js                # CRUD products (5 routes)
│   │   ├── orders.js                  # Create order, list orders, order detail (3 routes)
│   │   ├── users.js                   # Get profile, update profile (2 routes)
│   │   └── payments.js                # Process payment via Stripe (2 routes)
│   ├── middleware/
│   │   └── auth.js                    # Custom JWT verification middleware
│   ├── models/
│   │   ├── User.js                    # Mongoose schema, password stored as bcrypt hash
│   │   ├── Product.js                 # Mongoose schema
│   │   ├── Order.js                   # Mongoose schema with refs to User, Products
│   │   └── Payment.js                 # Mongoose schema
│   ├── utils/
│   │   ├── jwt.js                     # Custom JWT sign/verify with HS256
│   │   ├── email.js                   # Nodemailer for password reset
│   │   └── helpers.js                 # Misc utility functions
│   └── config/
│       └── db.js                      # MongoDB connection (mongoose.connect)
├── uploads/                           # Product images stored on filesystem
└── README.md                          # Minimal: "Run `npm start`"
```

### Key Configuration Details

**package.json**:
```json
{
  "name": "quickshop-api",
  "version": "1.0.0",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "mongoose": "^8.1.1",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "stripe": "^14.14.0",
    "nodemailer": "^6.9.8",
    "dotenv": "^16.3.1",
    "cors": "^2.8.5",
    "multer": "^1.4.5-lts.1",
    "express-validator": "^7.0.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.3",
    "eslint": "^8.56.0"
  }
}
```

Note: No test framework (jest, mocha, vitest), no test runner, no assertion library, no mocking library. No `"test"` script in package.json.

**Custom JWT implementation (src/utils/jwt.js)**:
```javascript
const jwt = require('jsonwebtoken');

const SECRET = process.env.JWT_SECRET || 'default-secret-change-me';

const signToken = (userId) => {
  return jwt.sign({ id: userId }, SECRET, { expiresIn: '30d' });
};

const verifyToken = (token) => {
  try {
    return jwt.verify(token, SECRET);
  } catch (err) {
    return null;
  }
};

module.exports = { signToken, verifyToken };
```

**Auth middleware (src/middleware/auth.js)**:
```javascript
const { verifyToken } = require('../utils/jwt');

const protect = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Not authorized' });

  const decoded = verifyToken(token);
  if (!decoded) return res.status(401).json({ error: 'Invalid token' });

  req.userId = decoded.id;
  next();
};

module.exports = { protect };
```

**.env file (COMMITTED TO REPO)**:
```bash
PORT=3000
MONGODB_URI=mongodb+srv://quickshop:P@ssw0rd123@cluster0.abc123.mongodb.net/quickshop
JWT_SECRET=my-super-secret-jwt-key-2024
STRIPE_SECRET_KEY=sk_live_51ABC...actual_key_here
STRIPE_WEBHOOK_SECRET=whsec_actual...
SMTP_HOST=smtp.gmail.com
SMTP_USER=quickshop.noreply@gmail.com
SMTP_PASS=app-password-here
```

**Database connection (src/config/db.js)**:
```javascript
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('MongoDB connected');
  } catch (err) {
    console.log('DB connection error:', err.message);
    process.exit(1);
  }
};

module.exports = connectDB;
```

**Express entry point (src/index.js, partial)**:
```javascript
const express = require('express');
const cors = require('cors');
require('dotenv').config();
const connectDB = require('./config/db');

const app = express();

app.use(cors());  // Allow all origins
app.use(express.json());
app.use('/uploads', express.static('uploads'));

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/products', require('./routes/products'));
app.use('/api/orders', require('./routes/orders'));
app.use('/api/users', require('./routes/users'));
app.use('/api/payments', require('./routes/payments'));

// No error handling middleware

connectDB();

app.listen(process.env.PORT || 3000, () => {
  console.log(`Server running on port ${process.env.PORT || 3000}`);
});
```

**No .github/ directory. No Dockerfile. No docker-compose.yml. No .gitignore for .env files.**

## Expected Behaviors

- Assigns low scores across most dimensions, with specific evidence for each low score
- Flags the complete absence of tests as a CRITICAL finding for Maintainability
- Identifies the committed .env file with live secrets (Stripe live key, MongoDB credentials, JWT secret) as a CRITICAL security finding
- Notes the hardcoded fallback JWT secret (`'default-secret-change-me'`) as a security vulnerability
- Flags the 30-day token expiration with no refresh token mechanism as a security concern
- Identifies the `cors()` with no origin restriction as a security issue
- Notes the absence of CI/CD pipeline and its impact on Operability
- Identifies console.log as the only logging mechanism (no structured logging)
- Flags the lack of error handling middleware in Express
- Notes that product images stored on local filesystem will not survive server replacement
- Identifies the absence of rate limiting on authentication endpoints
- Provides constructive recommendations despite the many issues

## Success Criteria

- [ ] Maintainability score is between 1-4/10, reflecting zero tests and no testing infrastructure
- [ ] Security score is between 1-3/10, reflecting committed secrets, open CORS, no rate limiting, and custom JWT with fallback secret
- [ ] Observability score is between 1-2/10, reflecting only console.log with no structured logging, monitoring, or error tracking
- [ ] Operability score is between 1-3/10, reflecting no CI/CD, no Docker, no IaC, manual deployment
- [ ] The committed .env file with live production secrets is flagged as CRITICAL severity
- [ ] The custom JWT implementation is questioned (why not use a vetted auth library like Passport.js or express-jwt with proper configuration)
- [ ] The lack of input validation on all routes (express-validator is installed but is it used consistently?) is investigated
- [ ] The architecture evolution roadmap provides actionable first steps, not a rewrite recommendation

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT score Maintainability above 4/10 given zero test files and no testing dependencies
- [ ] Should NOT overlook the security risk of committed production secrets (.env with live Stripe keys)
- [ ] Should NOT fail to identify the custom JWT fallback secret as a critical vulnerability
- [ ] Should NOT give a passing Observability score when the only logging is console.log
- [ ] Should NOT recommend a complete rewrite as the first step; should provide incremental improvement path
- [ ] Should NOT ignore that express-validator is a dependency but may not be consistently applied across all routes
- [ ] Should NOT overlook the open CORS policy allowing all origins
