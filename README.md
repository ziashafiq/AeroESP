# AeroESP

AeroESP is a proprietary web-based platform for Aerospace English learning, assessment, adaptive practice, examination workflows, learning analytics, and AI-assisted educational research.

The platform is designed to support both General English foundations and Aerospace English for Specific Purposes (ESP), with dedicated workflows for students, teachers, assessment, adaptive learning, examination integrity, and AI-assisted content development.

> **Status:** Private Beta
> **Current beta line:** `v0.9.0-beta.x`

---

## Core Capabilities

### Aerospace English

- Aerospace-specific English learning
- Domain and topic taxonomy
- General English and Aerospace ESP question banks
- Topic-oriented practice
- Aerospace terminology support
- Aerospace-domain learning pathways

### Learning Platform

- Student learning dashboard
- Course and module structure
- Daily practice
- Adaptive practice
- Weak-topic identification
- Review scheduling
- Learning paths
- Mastery tracking
- Error journal
- Recommendations
- Placement assessment

### Assessment

- Question-bank management
- General English and Aerospace-specific questions
- Teacher-managed questions
- Topic proposals
- Question taxonomy
- Import and bootstrap utilities

### Examination Engine

- Teacher examination workflows
- Student examination runner
- Exam publishing
- Question-bank assignment
- Exam structure configuration
- Attempt tracking
- Result management
- Integrity-event collection
- Integrity review workflows

### AI and Research Layer

AeroESP includes an AI-assisted research and educational intelligence layer supporting:

- Question generation
- Generated-question review
- AI quality assessment
- AI feedback
- Human feedback
- Prompt analytics
- Cost analytics
- Model comparison
- Provider configuration
- Experimental datasets
- Evaluation protocols
- AI experiments
- Experiment reporting
- Recommendation generation

The AI subsystem is designed around explicit provider configuration and human oversight.

Supported provider architecture currently includes:

- Baseline provider
- OpenAI provider
- DeepSeek provider

External AI providers require separately configured credentials and are not enabled by default.

---

## Architecture

AeroESP is implemented primarily with:

- Python
- Django
- PostgreSQL
- HTML
- CSS
- JavaScript

Primary Django applications:

```text
accounts/
assessment/
exams/
intelligence/
learning/
```

Supporting infrastructure:

```text
config/
content_import/
deployment/
static/
templates/
```

---

## Security

AeroESP uses environment-based configuration for production-sensitive settings.

Production credentials and secrets must never be committed to source control.

Sensitive configuration includes:

```text
DJANGO_SECRET_KEY
AEROESP_SECRET_KEY
AEROESP_DB_PASSWORD
```

Example environment files contain placeholders only.

The actual `.env` file is intentionally excluded from Git.

AI-provider credentials are stored separately from source code and protected by the application's credential-storage mechanism.

---

## Testing

AeroESP includes automated tests covering major platform components.

Current beta baseline:

```text
75 automated tests
```

Run the isolated test suite with:

```bash
python manage.py test --settings=config.test_settings
```

The isolated test configuration uses an in-memory test database and is independent of the development PostgreSQL database.

---

## Production Deployment

Production deployment is designed for a Linux-based stack using:

- Django
- Gunicorn
- PostgreSQL
- Nginx
- systemd
- HTTPS

Deployment assets are located in:

```text
deployment/
```

Production environment validation is provided by:

```text
config/production_check.py
```

---

## Repository Policy

This repository contains proprietary source code.

The repository is intended only for authorized development, testing, deployment, academic research, and evaluation related to the AeroESP project.

No permission is granted to copy, redistribute, publish, sublicense, sell, commercially exploit, or create derivative works from this software without explicit written authorization from the copyright holder.

---

## Beta Notice

AeroESP is currently under active development and evaluation.

The current beta should not be treated as a final production release.

Features, schemas, APIs, security controls, AI-provider integrations, and research instrumentation may change before the first stable release.

---

## Copyright

Copyright © 2026 AeroESP Project.

All rights reserved.

See [LICENSE](LICENSE) for the applicable proprietary license terms.
