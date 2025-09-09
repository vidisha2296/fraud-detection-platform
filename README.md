Here’s an updated README incorporating your partitioned transactions table and other details:

---

# Fraud Detection Platform

## Overview

This platform detects, evaluates, and monitors fraudulent transactions using a modular backend and interactive frontend. It leverages PostgreSQL for data storage, Redis for caching and real-time notifications, and a set of intelligent agents for fraud and insights evaluations.

---

## Backend (BE)

**Framework:** FastAPI (async endpoints)

**Database:** PostgreSQL

* **Transactions Table:** Partitioned to store data from the **last 90 days** for optimized queries.
* Stores transactions, customers, fraud alerts, insights, evaluations, and KB entries.

**Caching:** Redis

* Used for fast lookups and **Server-Sent Events (SSE)** notifications.

**Agents & Orchestrator:**

* Fraud, Insights, KB, and Compliance agents.
* Orchestrator manages agents with **circuit breakers** to prevent cascading failures.
* Implements fallback and retry strategies for failed agent calls.

**Fraud Assessment:**

* Single and batch assessment endpoints.
* Validates transactions before fraud evaluation.

**System Monitoring & Metrics:**

* `/fraud/system/status` returns agent states and overall system health.
* Shows circuit breaker states, failure counts, and last failure timestamps.

**Rate Limiting:**

* Prevents abuse on sensitive endpoints such as fraud assessment and system reset.

**Evaluation Framework:**

* Tracks execution of evaluation cases with pass/fail status, execution time, and outputs.
* Seed data available in `/fixtures`.

**Scripts:**

* `/scripts` includes database seeding, data setup, and utility scripts.

---

## Frontend (FE)

**Framework:** React + TypeScript

**Pages & Components:**

* **Dashboard:**

  * Search by customer ID → shows KPI widgets, recent fraud alerts, insights, metrics, and monitoring.
  * System monitoring panel with agent states and failures.
* **Transactions, Fraud, Insights, KB, Evaluations:** Separate pages accessible via dashboard navigation.
* **Fraud Alerts Page:** Trigger single or batch assessments, contact customers, and fetch fraud scores.

**API Integration:**

* Fetch KPIs, fraud alerts, insights, agent/system status, and evaluations via backend APIs.
* Handles errors, including rate limiting (429) and service unavailability gracefully.

**UI/UX Features:**

* Navigation links for all modules.
* Alerts preview, metrics cards, insights charts, and monitoring.
* Responsive and interactive dashboard components.

---

## Docker Setup

1. Build and start all services:

```bash
docker-compose up -d --build
```

2. **Note:** Make sure **Redis and PostgreSQL are not running locally** on conflicting ports (6379 for Redis, 5432 for PostgreSQL).

3. Stop local services if needed:

```bash
brew services stop redis
brew services stop postgresql
```

---

## Key Highlights

* **Partitioned transactions table** ensures queries are optimized for recent 90 days of data.
* **Async FastAPI backend** for scalable, high-performance endpoints.
* **Redis caching and SSE** for real-time notifications.
* **Robust fraud & insights agents** managed by an orchestrator with circuit breakers.
* **React frontend** for interactive, responsive dashboards and monitoring.


