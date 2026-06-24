# TECH_SPEC.md  

**Project:** ideaweb – Simple Web Analytics Platform  
**Owner:** Axentx OS – Product Engineering Team  
**Version:** 1.0.0  
**Last Updated:** 2026‑06‑24  

---  

## 1. Overview  

ideaweb is a lightweight, privacy‑first analytics system that tracks **page views**, **click events**, and **conversion actions** for any web property. Collected data is stored in a time‑series store and exposed via a real‑time dashboard that shows:

| Metric | Definition |
|--------|------------|
| **Daily Active Users (DAU)** | Unique visitors (by cookie‑derived ID) per calendar day |
| **Page Views** | Total number of page‑load events |
| **Clicks** | Total number of click events (configurable selector) |
| **Conversions** | Custom conversion events (e.g., form submit, purchase) |
| **Conversion Rate** | `Conversions / Clicks` (percentage) |

The system is designed for **fast ingestion**, **low latency queries**, and **easy embedding** into any static or dynamic site via a single JavaScript snippet.

---  

## 2. Architecture Overview  

```
+-------------------+       +-------------------+       +-------------------+
|   Front‑end UI    | <---> |   API Gateway     | <---> |   Ingestion Service|
| (React Dashboard) |       | (FastAPI + Auth) |       | (Python/uvicorn) |
+-------------------+       +-------------------+       +-------------------+
                                   |                         |
                                   v                         v
                           +-------------------+   +-------------------+
                           |  Event Queue      |   |  ClickHouse DB    |
                           |  (Kafka)          |   |  (columnar TS)    |
                           +-------------------+   +-------------------+
                                   ^                         ^
                                   |                         |
                           +-------------------+   +-------------------+
                           |  Tracker Script   |   |  Exporter Service |
                           |  (JS snippet)     |   | (CSV/JSON API)    |
                           +-------------------+   +-------------------+
```

* **Tracker Script** – Small (~5 KB) JavaScript snippet that captures events and posts them to the **Ingestion Service** via `fetch`.  
* **Ingestion Service** – Stateless FastAPI app that validates payloads, enriches with IP‑derived geo data, and pushes events to **Kafka**.  
* **Kafka** – High‑throughput durable queue; partitions by `site_id` for horizontal scaling.  
* **ClickHouse** – Columnar time‑series DB optimized for analytical queries (INSERTs via native HTTP interface).  
* **API Gateway** – FastAPI layer exposing authenticated REST endpoints for the dashboard and data export. Handles rate‑limiting, JWT auth, and request validation.  
* **Front‑end UI** – React + Vite SPA that queries the API for aggregated metrics and renders charts (Chart.js).  
* **Exporter Service** – Optional microservice that streams aggregated data to external sinks (e.g., S3, BigQuery) on a nightly schedule.

---  

## 3. Components & Responsibilities  

| Component | Language / Framework | Key Responsibilities |
|-----------|----------------------|-----------------------|
| **Tracker Script** | JavaScript (ES6) | - Capture `pageview`, `click`, `conversion` events<br>- Debounce rapid clicks<br>- Send batched payloads (max 20 events / 2 s) |
| **Ingestion Service** | Python 3.11, FastAPI, Pydantic | - Validate schema<br>- Add `event_id` (UUIDv7), `timestamp` (UTC), `user_id` (cookie hash)<br>- Geo‑enrich via MaxMind DB<br>- Publish to Kafka |
| **Kafka Cluster** | Apache Kafka 3.5 | - Durable event log<br>- Topic: `ideaweb.events` (partitioned by `site_id`) |
| **ClickHouse** | ClickHouse 24.3 | - Store raw events in `events` table (MergeTree)<br>- Materialized view `daily_aggregates` for fast dashboard queries |
| **API Gateway** | Python 3.11, FastAPI, JWT (PyJWT) | - Auth & RBAC (admin, read‑only)<br>- Expose `/metrics`, `/sites`, `/export` endpoints<br>- Rate limiting (100 req/s per token) |
| **Front‑end UI** | React 18, Vite, TypeScript, Chart.js | - Login (OAuth2 via Axentx SSO)<br>- Site selector, date range picker<br>- Render DAU, PV, Clicks, Conversions, Conversion Rate |
| **Exporter Service** | Python 3.11, Airflow DAG (optional) | - Nightly roll‑up to CSV/JSON<br>- Push to configured external bucket |
| **Observability** | Prometheus + Grafana, Loki | - Export metrics (`ingest_latency_ms`, `queue_depth`)<br>- Centralized logs for all services |

---  

## 4. Data Model  

### 4.1 Raw Event Table (`events`)  

| Column | Type | Description |
|--------|------|-------------|
| `event_id` | UUID | Unique identifier (UUIDv7) |
| `site_id` | String | Customer‑provided site identifier |
| `user_id` | String | Hashed cookie value (`sha256`) |
| `event_type` | Enum(`pageview`,`click`,`conversion`) | Type of event |
| `event_timestamp` | DateTime64(3) | UTC timestamp (ms precision) |
| `url` | String | Full page URL |
| `referrer` | String | HTTP referrer |
| `user_agent` | String | Raw UA string |
| `geo_country` | String | ISO‑3166‑1 alpha‑2 (from MaxMind) |
| `geo_city` | String | City name |
| `metadata` | JSON | Optional key‑value payload (e.g., product_id) |

**Engine:** `ReplacingMergeTree` on (`site_id`, `event_timestamp`) with `event_id` as version column.

### 4.2 Materialized View – Daily Aggregates  

```sql
CREATE MATERIALIZED VIEW daily_aggregates TO daily_metrics AS
SELECT
    toDate(event_timestamp) AS day,
    site_id,
    uniqExact(user_id) AS dau,
    countIf(event_type = 'pageview') AS page_views,
    countIf(event_type = 'click') AS clicks,
    countIf(event_type = 'conversion') AS conversions,
    (conversions / clicks) AS conversion_rate
FROM events
GROUP BY day, site_id;
```

### 4.3 API Response Schemas  

* **GET /metrics?site_id=&start=&end=**  

```json
{
  "site_id": "example.com",
  "period": { "start": "2026-06-01", "end": "2026-06-30" },
  "daily": [
    {
      "date": "2026-06-01",
      "dau": 1243,
      "page_views": 5432,
      "clicks": 312,
      "conversions": 27,
      "conversion_rate": 0.0865
    },
    …
  ]
}
```

---  

## 5. Key APIs / Interfaces  

| Method | Path | Auth | Description | Request Body | Response |
|--------|------|------|-------------|--------------|----------|
| `POST` | `/ingest` | None (rate‑limited) | Receive batched events from tracker | `{ events: [Event] }` | `{ received: 20 }` |
| `GET` | `/metrics` | JWT (role: `viewer`) | Query aggregated metrics | Query params: `site_id`, `start`, `end` | `MetricsResponse` |
| `GET` | `/sites` | JWT (role: `admin`) | List sites the token can access | – | `{ sites: ["example.com","demo.io"] }` |
| `GET` | `/export` | JWT (role: `admin`) | Download raw or aggregated CSV/JSON | Params: `format`, `site_id`, `start`, `end` | File stream |
| `POST` | `/auth/login` | – | Exchange Axentx SSO code for JWT | `{ code: "sso‑code" }` | `{ access_token, expires_in }` |

All endpoints return standard HTTP status codes; errors follow the **Problem Details** RFC 7807 format.

---  

## 6. Tech Stack  

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Front‑end | React 18, Vite, TypeScript 5, Chart.js 4 | Latest stable | Fast dev, tree‑shaking, small bundle |
| Tracker | Vanilla JS (ES2022) | – | No framework, works on any site |
| API / Services | Python 3.11, FastAPI 0.115, Pydantic 2 | Latest | High performance, automatic OpenAPI |
| Queue | Apache Kafka 3.5 | – | Proven durability, horizontal scaling |
| Storage | ClickHouse 24.3 | – | Columnar, sub‑second aggregation on billions of rows |
| Auth | Axentx SSO (OAuth2) + PyJWT | – | Centralized identity, RBAC |
| Observability | Prometheus 2.53, Grafana 10, Loki 3 | – | Cloud‑native metrics & logs |
| CI/CD | GitHub Actions, Docker, Helm (K8s) | – | Automated builds, can be deployed to any K8s cluster |
| Infra | Kubernetes 1.28, Helm charts, Terraform (AWS/EKS) | – | Cloud‑agnostic, auto‑scaling |

---  

## 7. Dependencies  

| Dependency | License | Usage |
|------------|---------|-------|
| `fastapi` | MIT | API layer |
| `uvicorn[standard]` | BSD‑3 | ASGI server |
| `pydantic` | MIT | Data validation |
| `aiokafka` | Apache‑2.0 | Async Kafka producer |
| `clickhouse-driver` | Apache‑2.0 | ClickHouse client |
| `maxminddb-geolite2` | CC‑BY‑4.0 | Geo enrichment |
| `react`, `react-dom` | MIT | UI |
| `chart.js` | MIT | Charts |
| `jwt` (`pyjwt`) | MIT | Token handling |
| `prometheus-client` | Apache‑2.0 | Metrics |
| `docker` | Apache‑2.0 | Containerisation |

All third‑party libraries are vetted for compatibility with Axentx’s security policy.

---  

## 8. Deployment Architecture  

### 8.1 Containerisation  

Each service is packaged as an independent Docker image:

| Service | Dockerfile Base | Port |
|---------|----------------|------|
| Tracker (served via CDN) | `node:20-alpine` (build) → static assets | N/A |
| Ingestion Service | `python:3.11-slim` | 8000 |
| API Gateway | `python:3.11-slim` | 8080 |
| Exporter Service | `python:3.11-slim` | 8090 |
| Front‑end UI | `node:20-alpine` (build) → `nginx:alpine` | 80 |
| Kafka & Zookeeper | Confluent images | 9092 / 2181 |
| ClickHouse | `clickhouse/clickhouse-server` | 8123 |

All images are pushed to the internal Axentx ECR registry.

### 8.2 Helm Chart Overview  

```
ideaweb/
├─ charts/
│  ├─ tracker/          # CDN‑hosted static assets
│  ├─ ingestion/
│  ├─ api-gateway/
│  ├─ frontend/
│  └─ exporter/
├─ values.yaml          # Global defaults (replicas, resources, env)
└─ Chart.yaml
```

Key values:

```yaml
global:
  imageRegistry: 123456789012.dkr.ecr.us-east-1.amazonaws.com
  environment: prod

ingestion:
  replicaCount: 3
  resources:
    limits:
      cpu: "500m"
      memory: "512Mi"
    requests:
      cpu: "250m"
      memory: "256Mi"
  kafka:
    brokers: ["kafka-0:9092","kafka-1:9092","kafka-2:9092"]
  clickhouse:
    host: clickhouse.default.svc.cluster.local
    port: 8123
```

### 8.3 Scaling & Resilience  

* **Ingestion Service** – Horizontal pod autoscaler (HPA) based on `request_latency_ms` and Kafka lag.  
* **Kafka** – 3‑node cluster with replication factor 3; ISR monitoring alerts on under‑replicated partitions.  
* **ClickHouse** – Distributed table across 2 shards, each with 2 replicas; automatic data sharding by `site_id`.  
* **API Gateway** – Stateless; can be scaled behind an external load balancer (AWS ALB).  
* **Front‑end** – Served via CDN (CloudFront) for global low‑latency access.

---  

## 9. Security & Privacy  

| Aspect | Implementation |
|--------|----------------|
| **Data Minimisation** | Only `user_id` (hashed), no raw IP stored; Geo data derived from IP then discarded. |
| **Transport Security** | All endpoints enforce TLS 1.3; tracker uses `https://` endpoint. |
| **Auth** | JWT signed with RSA‑2048; short‑lived access tokens (15 min) + refresh token flow. |
| **CORS** | Tracker endpoint allows only origins listed in site configuration. |
| **Rate Limiting** | Token‑based bucket algorithm (100 req/s). |
| **Audit** | All ingestion requests logged to Loki with request ID for traceability. |
| **GDPR** | `user_id` can be deleted on request; raw events are retained for 90 days then purged. |

---  

## 10. Observability  

* **Metrics** (Prometheus) – `ingest_requests_total`, `ingest_latency_ms`, `kafka_lag`, `clickhouse_query_time_ms`.  
* **Dashboards** – Grafana dashboards for system health, per‑site traffic spikes, error rates.  
* **Logging** – Structured JSON logs (timestamp, level, request_id, service) shipped to Loki.  
* **Alerting** – PagerDuty alerts on:  
  * Kafka lag > 5 min  
  * ClickHouse query latency > 2 s  
  * Ingestion error rate > 0.5 %  

---  

## 11. Testing Strategy  

| Layer | Tool | Scope |
|-------|------|-------|
| Unit | `pytest`, `pytest‑asyncio` | All pure‑Python functions, Pydantic models |
| Integration | `testcontainers` (Kafka, ClickHouse) | End‑to‑end ingestion → DB → API |
| Contract | `schemathesis` against OpenAPI spec | API compliance |
| UI | `cypress` | Dashboard flows, auth, chart rendering |
| Load | `k6` | 10k req/s ingestion burst, 1k req/s dashboard queries |
| Security | `bandit`, `OWASP ZAP` | Code scanning, penetration testing |

CI pipeline runs unit → integration → contract → UI on every PR; load & security tests run nightly.

---  

## 12. Release & Roll‑out Plan  

| Phase | Activities |
|-------|------------|
| **Alpha** | Deploy to internal staging; enable tracker on a single test site; collect ingestion latency metrics. |
| **Beta** | Open to 5 pilot customers; add site‑level RBAC, export feature. |
| **General Availability** | Autoscaling enabled, SLA 99.9 % uptime, documentation published. |
| **Post‑GA** | Nightly roll‑up to S3, optional BI connector (Looker). |

Versioning follows **Semantic Versioning** (MAJOR.MINOR.PATCH).  

---  

## 13. Risks & Mitigations  

| Risk | Impact | Mitigation |
|------|--------|------------|
| **High ingestion volume spikes** | Service degradation | Autoscaling, back‑pressure via Kafka, circuit‑breaker in tracker (fallback to local storage). |
| **Privacy compliance** | Legal exposure | Hashing of user identifiers, data retention policy, easy GDPR delete endpoint. |
| **ClickHouse schema drift** | Query failures | Migration scripts versioned in Git, CI validates schema compatibility. |
| **Third‑party library vulnerabilities** | Security breach | Dependabot alerts, weekly `pip-audit` scans, fast patch cycle. |

---  

## 14. Glossary  

* **DAU** – Daily Active Users.  
* **TTL** – Time‑to‑Live (used for cache and token expiry).  
* **UUIDv7** – Time‑ordered UUID, provides monotonic ordering for event streams.  

---  

*Prepared by the Axentx Product Engineering Team – Senior Lead*  

---
