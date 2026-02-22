---
agent: financial-cost
type: edge-case
description: Python Flask app with no infrastructure configuration — tests analysis under infrastructure uncertainty
expected_outcome: partial
---

# Task: Flask App Without Infrastructure — Hypothetical Cost Modeling

## Context

DataPipe is a Python Flask application for data pipeline orchestration. It allows users to define ETL pipelines via a web UI, schedule them, and monitor execution. The codebase has the application logic (Flask routes, SQLAlchemy models, Celery workers) but has absolutely NO deployment or infrastructure configuration. There is no Dockerfile, no Terraform, no docker-compose, no CI/CD pipeline, no Kubernetes manifests, no Procfile, no deployment scripts. The application is being developed and tested entirely on the developer's local machine.

This scenario tests whether the financial-cost agent can honestly acknowledge the missing infrastructure information, provide hypothetical cost models with clearly labeled assumptions, and recommend an infrastructure setup rather than guessing at what does not exist.

## Input

**Simulated Codebase Structure:**

```
datapipe/
├── app/
│   ├── __init__.py                    # Flask app factory
│   ├── config.py                      # Config from environment variables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                    # User model (Flask-Login)
│   │   ├── pipeline.py               # Pipeline definition model
│   │   ├── step.py                    # Pipeline step model (extract, transform, load)
│   │   ├── schedule.py               # Cron schedule model
│   │   ├── execution.py              # Pipeline execution history
│   │   └── connection.py             # External data source connections
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                    # Login, logout, register
│   │   ├── pipelines.py              # Pipeline CRUD
│   │   ├── steps.py                  # Step CRUD within pipelines
│   │   ├── executions.py             # Execution history and logs
│   │   ├── connections.py            # Data source connection management
│   │   ├── schedules.py              # Schedule CRUD
│   │   └── api.py                    # REST API for programmatic access
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py             # Celery configuration
│   │   ├── pipeline_runner.py        # Main pipeline execution worker
│   │   ├── scheduler.py              # Celery Beat schedule sync
│   │   └── connectors/
│   │       ├── postgres.py           # PostgreSQL source/destination
│   │       ├── mysql.py              # MySQL source/destination
│   │       ├── s3.py                 # S3 file source/destination
│   │       ├── bigquery.py           # BigQuery source/destination
│   │       └── api.py                # HTTP API source
│   ├── templates/
│   │   ├── base.html                 # Jinja2 base template
│   │   ├── dashboard.html
│   │   ├── pipeline_editor.html
│   │   ├── execution_detail.html
│   │   └── connections.html
│   └── static/
│       ├── css/
│       │   └── main.css
│       └── js/
│           ├── pipeline-editor.js     # Drag-and-drop pipeline builder
│           └── execution-logs.js      # Real-time log streaming via SSE
├── tests/
│   ├── test_models.py                 # 15 tests
│   ├── test_routes.py                 # 12 tests
│   ├── test_pipeline_runner.py        # 18 tests
│   └── test_connectors.py            # 10 tests
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
└── README.md
```

**requirements.txt:**

```
flask==3.0.2
flask-sqlalchemy==3.1.1
flask-login==0.6.3
flask-migrate==4.0.5
flask-wtf==1.2.1
sqlalchemy==2.0.27
psycopg2-binary==2.9.9
celery[redis]==5.3.6
redis==5.0.3
python-dotenv==1.0.1
gunicorn==21.2.0
requests==2.31.0
pandas==2.2.1
boto3==1.34.51
google-cloud-bigquery==3.17.2
pymysql==1.1.0
cryptography==42.0.5
APScheduler==3.10.4
```

**.env.example:**

```bash
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=change-me-in-production
DATABASE_URL=postgresql://datapipe:password@localhost:5432/datapipe
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

**app/config.py:**

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/datapipe')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    MAX_CONCURRENT_PIPELINES = int(os.environ.get('MAX_CONCURRENT_PIPELINES', '5'))
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', '30'))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

**app/models/pipeline.py:**

```python
from app import db
from datetime import datetime

class Pipeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, active, paused, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = db.relationship('Step', backref='pipeline', lazy='dynamic', cascade='all, delete-orphan')
    executions = db.relationship('Execution', backref='pipeline', lazy='dynamic')
    schedule = db.relationship('Schedule', backref='pipeline', uselist=False)

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.Integer, db.ForeignKey('pipeline.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    step_type = db.Column(db.String(20), nullable=False)  # extract, transform, load
    connector_type = db.Column(db.String(50))  # postgres, mysql, s3, bigquery, api
    config = db.Column(db.JSON)  # Connection params, query, file path, etc.
    position = db.Column(db.Integer, default=0)
    depends_on = db.Column(db.JSON, default=list)  # List of step IDs this depends on

class Execution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.Integer, db.ForeignKey('pipeline.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, running, success, failed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    logs = db.Column(db.Text)
    rows_processed = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
```

**Key observations about the codebase:**
- NO Dockerfile present
- NO docker-compose.yml
- NO Terraform, CloudFormation, or any IaC
- NO CI/CD pipeline configuration (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
- NO Kubernetes manifests
- NO Procfile (Heroku), app.yaml (GCP), or similar PaaS configs
- NO deployment scripts or Makefile
- gunicorn is in requirements.txt (production WSGI server) but no configuration for it
- Application requires: PostgreSQL, Redis (for Celery broker + result backend), and the Flask app + Celery workers
- Celery workers execute data pipelines that connect to external systems (Postgres, MySQL, S3, BigQuery)
- boto3 and google-cloud-bigquery suggest multi-cloud data source connectivity
- MAX_CONCURRENT_PIPELINES=5 is a config hint about resource requirements
- pandas is used for data transformation (memory-intensive for large datasets)

## Expected Behaviors

- Clearly states that no infrastructure configuration exists in the codebase
- Identifies the infrastructure requirements from code analysis: PostgreSQL, Redis, Flask app server (gunicorn), Celery workers, Celery Beat scheduler
- Provides HYPOTHETICAL cost models with assumptions EXPLICITLY labeled as hypothetical
- Offers multiple deployment scenarios (self-managed VPS, AWS managed services, GCP managed services, PaaS like Railway/Render)
- Considers Celery worker resource requirements (pandas data processing can be memory-intensive)
- Identifies that multi-source connectors (S3, BigQuery) imply data transfer costs
- Recommends Docker as the first step toward deployable infrastructure
- Provides CI/CD setup recommendations
- Flags the absence of infrastructure as a risk (no reproducibility, no disaster recovery)

## Success Criteria

- [ ] Explicitly acknowledges the absence of all infrastructure configuration (no Docker, no IaC, no CI/CD)
- [ ] Identifies infrastructure requirements from code: PostgreSQL, Redis, Flask/gunicorn, Celery workers, Celery Beat
- [ ] Provides at least 2 deployment scenario cost estimates (e.g., AWS managed vs VPS vs PaaS)
- [ ] All cost estimates are clearly marked as hypothetical/assumed (not presented as definitive)
- [ ] Celery worker resource needs analyzed (concurrent pipelines, pandas memory usage)
- [ ] Cross-cloud data transfer costs mentioned (connecting to BigQuery + S3 from a different provider)
- [ ] Recommends containerization (Docker) as the immediate infrastructure priority
- [ ] Recommends CI/CD pipeline setup as a near-term priority
- [ ] Financial Health Score is low (2-4/10) reflecting the infrastructure maturity gap

## Anti-Criteria (Agent Should NOT)

- [ ] Should NOT present hypothetical cost estimates as definitive or precise
- [ ] Should NOT assume a specific cloud provider without stating it as an assumption
- [ ] Should NOT skip the infrastructure gap entirely and jump to cost numbers
- [ ] Should NOT ignore Celery worker requirements (these are the most resource-intensive components)
- [ ] Should NOT miss the data transfer cost implications of multi-cloud connectors (S3 + BigQuery)
- [ ] Should NOT provide a cost breakdown formatted as if real infrastructure exists
- [ ] Should NOT skip the recommendation to containerize the application first
- [ ] Should NOT ignore the gunicorn dependency as a signal of production-readiness intent
