# Phase 3 Plan — Modern Backend Engineering (Days 41-60)

## Goal
Transform TaskFlow AI from a CLI tool into a production-grade
REST API with authentication, caching, background jobs, and
cloud deployment.

## Architecture Change
CLI (current) → FastAPI REST API + CLI client

## Key Milestones

### Day 41-44: FastAPI Foundation
- Replace shell.py with a FastAPI application
- Expose all task operations as REST endpoints
- Pydantic models for request/response validation
- Auto-generated Swagger docs

### Day 45-46: Authentication
- JWT-based auth — register, login, protected routes
- Per-user task isolation (currently all tasks are "Udit's")

### Day 47-49: Scalability
- Redis caching for GET /tasks
- Celery background jobs for AI analysis (Phase 4)
- WebSocket for real-time task updates

### Day 50-52: Database
- SQLite → PostgreSQL migration
- SQLAlchemy ORM replaces json_store.py
- Alembic migrations for schema changes

### Day 53-55: Containerisation
- Dockerfile for the FastAPI app
- docker-compose.yml: app + PostgreSQL + Redis
- Environment-based configuration (.env in container)

### Day 56-58: CI/CD
- GitHub Actions: test → lint → build → deploy
- Staging environment on Railway/Render
- Health check endpoint

### Day 59-60: Observability
- Sentry error tracking
- Prometheus metrics
- Structured JSON logging

## Technical Debt to Resolve Before Phase 3
- TD-001: Split commands.py (medium effort)
- TD-002: Standardise on Task objects (medium effort)
- TD-003: Add test suite — Day 25 (high effort, started Day 25)