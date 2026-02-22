---
agent: technical-architecture
type: edge-case
description: 10-year-old PHP 5.6 codebase with SQL injection risks and no dependency management
expected_outcome: partial
---

# Task: Legacy PHP 5.6 Codebase with Critical Security Gaps

## Context

A regional insurance brokerage has been running a client management and quoting system called "BrokerDesk" for 10 years. The system was originally built by a now-departed developer and has been maintained by a series of contractors. The PHP 5.6 codebase uses no framework, no namespaces, heavy global state, SQL queries mixed into view files, jQuery on the frontend, and is deployed via FTP to a shared hosting provider. The system is business-critical: 15 insurance brokers use it daily to manage ~8,000 client records and generate ~500 insurance quotes/month. The company wants to know if they should modernize or replace it.

## Input

**Project**: BrokerDesk
**Type**: Internal B2B Insurance Client Management + Quoting System
**Stage**: Legacy production (10 years old, no active development, maintenance-only)
**Team**: 0 dedicated developers (occasional contractor for bug fixes)
**Users**: 15 internal brokers, ~8,000 client records

### Simulated Codebase Structure

```
brokerdesk/
├── index.php                          # Front controller (giant switch statement)
├── config.php                         # DB credentials in plain PHP file
├── db.php                             # mysqli connection, no PDO
├── functions.php                      # ~2,000 lines of utility functions
├── auth.php                           # Session-based auth, MD5 password hashing
├── pages/
│   ├── dashboard.php                  # HTML + PHP + SQL mixed together
│   ├── clients/
│   │   ├── list.php                   # Client listing with inline SQL queries
│   │   ├── add.php                    # Client creation form + processing
│   │   ├── edit.php                   # Client edit with raw $_POST usage
│   │   └── view.php                   # Client detail with joined SQL
│   ├── quotes/
│   │   ├── list.php                   # Quote listing
│   │   ├── create.php                 # Multi-step quote wizard
│   │   ├── edit.php                   # Quote editing
│   │   └── pdf.php                    # Quote PDF generation (FPDF library)
│   ├── policies/
│   │   ├── list.php                   # Active policies listing
│   │   └── renew.php                  # Policy renewal processing
│   ├── reports/
│   │   ├── monthly.php                # Monthly revenue report
│   │   └── commissions.php            # Broker commission calculations
│   └── admin/
│       ├── users.php                  # User management
│       └── settings.php               # System settings
├── includes/
│   ├── header.php                     # HTML header with inline CSS/JS
│   ├── footer.php                     # HTML footer
│   ├── sidebar.php                    # Navigation sidebar
│   └── helpers.php                    # More utility functions
├── assets/
│   ├── css/
│   │   └── style.css                  # Single CSS file, ~3,000 lines
│   ├── js/
│   │   ├── jquery-1.11.3.min.js       # jQuery 1.11.3 (2015, known vulnerabilities)
│   │   └── app.js                     # ~1,500 lines of jQuery DOM manipulation
│   └── images/
├── uploads/                           # Client document uploads (no validation)
├── lib/
│   ├── fpdf/                          # FPDF library (copy-pasted, not managed)
│   └── phpmailer/                     # PHPMailer (old version, copy-pasted)
├── composer.json                      # Minimal, dependencies use "*" versions
├── cron/
│   ├── policy_reminders.php           # Cron job: email upcoming renewals
│   └── backup.php                     # Cron job: mysqldump to local directory
└── .htaccess                          # Apache rewrite rules
```

### Key Configuration Details

**config.php**:
```php
<?php
// Database configuration
$db_host = 'localhost';
$db_user = 'brokerdesk';
$db_pass = 'Br0k3r2015!';
$db_name = 'brokerdesk_prod';

// Email settings
$smtp_host = 'mail.brokerage.com';
$smtp_user = 'system@brokerage.com';
$smtp_pass = 'EmailPass123';

// Application settings
$upload_dir = '/var/www/brokerdesk/uploads/';
$max_upload_size = 10485760; // 10MB
$session_timeout = 3600; // 1 hour

// No HTTPS enforcement
// No CSRF token configuration
// No Content Security Policy headers
```

**auth.php (authentication)**:
```php
<?php
session_start();

function login($username, $password) {
    global $db;
    $query = "SELECT * FROM users WHERE username = '$username' AND password = '" . md5($password) . "'";
    $result = mysqli_query($db, $query);
    if ($row = mysqli_fetch_assoc($result)) {
        $_SESSION['user_id'] = $row['id'];
        $_SESSION['user_name'] = $row['name'];
        $_SESSION['user_role'] = $row['role'];
        return true;
    }
    return false;
}

function isLoggedIn() {
    return isset($_SESSION['user_id']);
}

function isAdmin() {
    return isset($_SESSION['user_role']) && $_SESSION['user_role'] == 'admin';
}
```

**Example page with inline SQL (pages/clients/list.php)**:
```php
<?php
include '../../auth.php';
if (!isLoggedIn()) { header('Location: /index.php'); exit; }
include '../../db.php';
include '../../includes/header.php';

$search = isset($_GET['q']) ? $_GET['q'] : '';
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$limit = 25;
$offset = ($page - 1) * $limit;

// SQL INJECTION: $search is not escaped or parameterized
$query = "SELECT c.*, COUNT(q.id) as quote_count
          FROM clients c
          LEFT JOIN quotes q ON q.client_id = c.id
          WHERE c.name LIKE '%$search%' OR c.email LIKE '%$search%'
          GROUP BY c.id
          ORDER BY c.name ASC
          LIMIT $limit OFFSET $offset";

$result = mysqli_query($db, $query);
?>

<div class="container">
    <h1>Clients</h1>
    <form method="GET">
        <input type="text" name="q" value="<?php echo $search; ?>" placeholder="Search clients...">
        <!-- XSS: $search echoed without htmlspecialchars -->
        <button type="submit">Search</button>
    </form>
    <table class="table">
        <tr><th>Name</th><th>Email</th><th>Phone</th><th>Quotes</th><th>Actions</th></tr>
        <?php while ($row = mysqli_fetch_assoc($result)): ?>
        <tr>
            <td><a href="view.php?id=<?php echo $row['id']; ?>"><?php echo $row['name']; ?></a></td>
            <!-- XSS: $row['name'] and $row['email'] not escaped -->
            <td><?php echo $row['email']; ?></td>
            <td><?php echo $row['phone']; ?></td>
            <td><?php echo $row['quote_count']; ?></td>
            <td>
                <a href="edit.php?id=<?php echo $row['id']; ?>">Edit</a>
                <a href="view.php?id=<?php echo $row['id']; ?>">View</a>
            </td>
        </tr>
        <?php endwhile; ?>
    </table>
</div>

<?php include '../../includes/footer.php'; ?>
```

**composer.json**:
```json
{
    "name": "brokerage/brokerdesk",
    "require": {
        "php": ">=5.6",
        "setasign/fpdf": "*",
        "phpmailer/phpmailer": "*"
    }
}
```

**backup.php (cron job)**:
```php
<?php
// Runs daily via crontab
$backup_dir = '/var/www/brokerdesk/backups/';
$filename = 'backup_' . date('Y-m-d') . '.sql';

// Credentials in plain text, backup stored on same server
exec("mysqldump -u brokerdesk -pBr0k3r2015! brokerdesk_prod > $backup_dir$filename");

// Keep only last 7 days
exec("find $backup_dir -name '*.sql' -mtime +7 -delete");
```

**No test files. No testing framework. No CI/CD. No Docker. No .gitignore (if even using git). No version control evident from structure.**

## Expected Behaviors

- Assigns low scores across most dimensions, with specific code evidence for each
- Identifies SQL injection in the login function and client list page as CRITICAL severity with specific code references
- Identifies MD5 password hashing as CRITICAL (unsalted MD5, broken cryptographic hash)
- Flags XSS vulnerabilities from unescaped output in view files
- Notes the lack of CSRF protection on forms
- Identifies the `composer.json` with `"*"` version constraints as a supply chain risk
- Recognizes that database credentials are hardcoded in config.php and backup.php
- Notes that backups are stored on the same server as the application (no offsite backup)
- Identifies the jQuery 1.11.3 version as having known security vulnerabilities
- Provides a constructive, incremental modernization path rather than demanding a full rewrite
- Acknowledges the business context: this system works for 15 users and handles real client data
- Suggests a phased approach: security fixes first, then gradual modernization

## Success Criteria

- [ ] Overall Architecture Health Score is 2-3/10
- [ ] Scalability score is 1-3/10, reflecting no caching, no horizontal scaling capability, shared hosting
- [ ] Reliability score is 1-3/10, reflecting no error handling, no health checks, backups on same server
- [ ] Maintainability score is 1-2/10, reflecting no tests, no framework, 2000-line functions.php, mixed concerns
- [ ] Security score is 1/10, reflecting SQL injection, MD5 passwords, XSS, no CSRF, hardcoded credentials, no HTTPS
- [ ] Observability score is 1/10, reflecting no logging infrastructure at all
- [ ] Operability score is 1-2/10, reflecting FTP deployment, no CI/CD, no IaC, cron jobs with hardcoded credentials
- [ ] SQL injection is identified as CRITICAL with specific code reference to the login function and client list query
- [ ] MD5 password hashing is identified as CRITICAL
- [ ] Provides a phased modernization roadmap: Phase 1 security patches, Phase 2 framework migration, Phase 3 infrastructure
- [ ] Suggests starting with parameterized queries and password rehashing before any other modernization

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT simply say "rewrite everything in a modern framework" as the primary recommendation
- [ ] Should NOT provide only criticism without a constructive, incremental migration path
- [ ] Should NOT ignore the business reality that this system is critical for daily operations and cannot go offline for a rewrite
- [ ] Should NOT overlook the client data sensitivity (insurance records contain PII) when assessing security impact
- [ ] Should NOT assume that the current state is intentional; should frame findings as accumulated technical debt
- [ ] Should NOT score any dimension above 4/10 given the pervasive issues across the codebase
- [ ] Should NOT fail to mention that the PHP 5.6 runtime itself is end-of-life and no longer receives security patches
