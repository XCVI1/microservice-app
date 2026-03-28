![Auth Service CI](https://github.com/XCVI1/microservice-app/actions/workflows/auth-service.yml/badge.svg)
![Core Service CI](https://github.com/XCVI1/microservice-app/actions/workflows/core-service.yml/badge.svg)

# Microservice App

## Overview

Microservice App is a production-oriented backend system designed with a strong emphasis on DevOps automation, reliability, and scalability.

The project implements a full CI/CD lifecycle, enabling automated testing, containerization, security scanning, and zero-downtime deployments with rollback capabilities.

---

## Architecture

The system follows a microservices architecture:

* **auth-service** — authentication and authorization (JWT)
* **core-service** — business logic layer
* **api-gateway** — Nginx-based reverse proxy
* **postgres** — relational database

### Key Design Decisions

* Single entry point via API Gateway
* Internal service communication over Docker network
* Environment-driven configuration
* Stateless services for scalability

---

## Project Structure

```bash
microservice-app/
│
├── auth-service/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   └── Dockerfile
│
├── core-service/
│   ├── app/
│   ├── alembic/
│   └── Dockerfile
│
├── api-gateway/
│   └── nginx.conf
│
├── ansible/
│   ├── inventories/
│   ├── playbooks/
│   ├── roles/
│   └── ansible.cfg
│ 
├── monitoring
│   ├── configs/
│   └── docker-compose.monitoring.yml
│ 
├── docker-compose.yml
└── .env
```
---

## Containerization

All services are fully containerized and orchestrated via `docker-compose`.

```bash
docker compose up -d
```

### Features

* Isolated service environments
* Shared internal network
* Centralized configuration via environment variables
* Reproducible local and remote environments

---

## Configuration Management

* Environment variables injected via `.env`
* Strict validation using Pydantic Settings
* No hardcoded secrets in codebase

---
# Infrastructure Automation (Ansible)

The project includes a fully automated deployment system built with **Ansible**, enabling reproducible environments and consistent service rollout.

## Features

- Automated environment provisioning
- Docker & Docker Compose installation
- Template-based configuration generation (`docker-compose.yml`, `.env`, `nginx.conf`)
- Idempotent deployment (only changed components are restarted)
- Zero-touch local setup via `ansible-playbook setup.yml`
- Automated service rollout via `ansible-playbook deploy.yml`

## Directory Structure

```bash
ansible/
├── ansible.cfg
├── inventories/
│   ├── production/
│       └── group_vars/
│   ├── staging/
│       └── group_vars/
│   └── local/
│       └── group_vars/
├── playbooks/
│   ├── setup.yml
│   └── deploy.yml
└── roles/
    ├── setup/
    │   └── tasks/
    └── deploy/
    │  ├── tasks/
    │  └── templates/
    └── rollback/
        ├── defaults/
        └── tasks/

```
## Usage
```bash
ansible-playbook -i inventories/staging/hosts.ini playbooks/rollback.yml -e "service=core-service"
ansible-playbook playbooks/setup.yml -K
ansible-playbook playbooks/deploy.yml -K

```

---

## CI/CD Pipeline

Implemented using GitHub Actions with a multi-stage pipeline.

### CI Pipeline

**Code Quality & Security**

* Ruff (linting & formatting)
* MyPy (static typing)
* Bandit (security analysis)

**Testing**

* pytest with async support
* multi-version testing (Python 3.11 / 3.12)

---

### Build & Delivery

* Docker image build using BuildKit
* Layer caching for faster builds
* Image tagging strategy:

  * `latest` for main branch
  * commit SHA for traceability

---

### Security

* Container scanning via Trivy
* Static code security analysis
* Secrets managed via GitHub Secrets and environment variables

---

## Continuous Deployment

### Staging Deployment

* Trigger: push to `main`
* Automated deployment via SSH
* Zero-downtime service update
* Database migrations executed automatically (Alembic)
* Healthcheck with retry strategy
* Automatic rollback on failure

### Production Deployment

* Trigger: git tags (`auth-v*`)
* Same deployment strategy as staging
* Release creation in GitHub
* Telegram notifications for deployment status

---

## Reliability & Rollback Strategy

* Healthcheck-based deployment validation
* Retry mechanism for service readiness
* Automatic rollback to previous Docker image on failure
* Version traceability via image tags

---

## Testing Strategy

* Async API testing with httpx
* Endpoint-level validation:

  * authentication
  * registration
  * healthchecks

---

## Key DevOps Features

* Fully automated CI/CD pipeline
* Environment-based configuration management
* Containerized architecture
* Zero-downtime deployments
* Automated rollback mechanism
* Security scanning integrated into pipeline
* Multi-environment deployment (staging / production)

---

## Implemented

* [x] Microservices architecture
* [x] API Gateway (Nginx)
* [x] Docker & docker-compose orchestration
* [x] PostgreSQL integration
* [x] JWT authentication
* [x] Alembic migrations
* [x] CI pipeline (lint, type-checking, tests)
* [x] CD pipeline (staging & production)
* [x] Docker image build & push
* [x] Container security scanning (Trivy)
* [x] Static security analysis (Bandit)
* [x] Healthcheck-based deployment validation
* [x] Automated rollback strategy
* [x] Telegram deployment notifications
* [x] GitHub Releases automation
* [X] Ansible automation

---

## Roadmap

* [ ] Redis (caching, rate limiting)
* [ ] Observability stack (Prometheus + Grafana)
* [ ] Centralized logging (ELK / Loki)
* [ ] Kubernetes deployment
