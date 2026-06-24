# STORIES.md

## Project: **ideaweb**  
**Goal:** Deliver a lightweight, self‑hosted analytics platform that records page views, clicks, and conversions, and surfaces daily active users (DAU) and conversion rates on an intuitive dashboard.

---

## Epics & Backlog

| Epic | Description | Priority (MVP → Future) |
|------|-------------|------------------------|
| **E1 – Data Collection** | Capture core interaction events from client pages. | 1 |
| **E2 – Event Storage & Processing** | Persist events, aggregate daily metrics, and compute conversion funnels. | 1 |
| **E3 – Dashboard UI** | Visualize DAU, page‑view trends, click counts, and conversion rates. | 2 |
| **E4 – Configuration & Integration** | Provide easy SDK/API for developers to embed analytics. | 2 |
| **E5 – Security & Privacy** | Ensure data is stored securely and respect GDPR‑style opt‑out. | 3 |
| **E6 – Export & Alerting** | Allow CSV/JSON export and configure threshold alerts. | 4 |

---

## User Stories

### **Epic E1 – Data Collection**

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E1‑01** | **As a front‑end developer, I want a tiny JavaScript snippet to embed on my site, so that page views are automatically recorded.** | • Snippet size ≤ 8 KB gzipped.<br>• Loads asynchronously without blocking page render.<br>• Sends a `page_view` event with URL, referrer, timestamp, and a generated anonymous visitor ID.<br>• Returns a 200 OK response on the server. |
| **E1‑02** | **As a product manager, I want click events on elements with `data-ideaweb-click` attribute to be captured, so that we can measure user engagement.** | • Clicking any element with the attribute triggers a `click` event containing element selector, page URL, visitor ID, and timestamp.<br>• No duplicate events for the same click (debounce 300 ms). |
| **E1‑03** | **As a marketer, I want to fire a `conversion` event from my own code, so that we can track sign‑ups or purchases.** | • Public `ideaweb.trackConversion(payload)` API accepts arbitrary key/value pairs.<br>• Event stored with `conversion` type, visitor ID, and payload.<br>• Returns a promise that resolves when the server acknowledges receipt. |
| **E1‑04** | **As a privacy‑concerned user, I want to opt‑out of tracking, so that my activity is not recorded.** | • Global `ideaweb.optOut()` disables all future event sends for the current visitor ID.<br>• Existing pending events are discarded.<br>• Opt‑out status persisted in `localStorage` and respected across page loads. |

### **Epic E2 – Event Storage & Processing**

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E2‑01** | **As a backend engineer, I want events stored in a time‑series table, so that we can efficiently query daily aggregates.** | • PostgreSQL (or SQLite for dev) table `events(id, visitor_id, type, payload JSONB, ts TIMESTAMP)`.<br>• Index on `ts` and `type`.<br>• Insert latency < 20 ms per event under 1 k RPS load test. |
| **E2‑02** | **As a data analyst, I want a nightly job that computes DAU, total page views, clicks, and conversion counts per day, so that the dashboard can display them instantly.** | • Cron job runs at 02:00 UTC.<br>• Writes aggregated rows to `daily_metrics(date, dau, page_views, clicks, conversions, conversion_rate)`.<br>• `conversion_rate = conversions / page_views` (rounded to 2 dp). |
| **E2‑03** | **As a product owner, I want the system to deduplicate multiple page‑view events from the same visitor within a 5‑second window, so that bounce traffic isn’t over‑counted.** | • Deduplication logic applied during aggregation (GROUP BY visitor_id, date, MIN(ts)).<br>• Verified by unit test with simulated rapid refreshes. |

### **Epic E3 – Dashboard UI**

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E3‑01** | **As a business stakeholder, I want a login‑protected web dashboard, so that only authorized users can view analytics.** | • Simple username/password auth (bcrypt hashed).<br>• Session cookie with HttpOnly & Secure flags.<br>• Unauthorized requests redirected to `/login`. |
| **E3‑02** | **As a data‑driven marketer, I want a line chart of daily page views for the last 30 days, so that I can spot trends.** | • Chart rendered with a lightweight library (e.g., Chart.js).<br>• Data fetched via `/api/metrics?metric=page_views&days=30`.<br>• Hover tooltip shows exact count per day. |
| **E3‑03** | **As a growth manager, I want to see the daily conversion rate as a percentage, so that I can evaluate campaign performance.** | • KPI card displays latest `conversion_rate` with up/down arrow indicating change vs. previous day.<br>• Color‑coded (green for ↑, red for ↓). |
| **E3‑04** | **As an executive, I want a table summarizing DAU, page views, clicks, and conversions for a selectable date range, so that I can export reports.** | • Date‑range picker (max 90 days).<br>• Table updates instantly via API.<br>• “Export CSV” button triggers download of the displayed rows. |

### **Epic E4 – Configuration & Integration**

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E4‑01** | **As a DevOps engineer, I want a Dockerfile and docker‑compose setup, so that the whole stack can be deployed with a single command.** | • `docker-compose.yml` defines `frontend`, `backend`, `db` services.<br>• `docker compose up -d` builds and runs all containers.<br>• Health‑check endpoint `/healthz` returns 200 when ready. |
| **E4‑02** | **As a third‑party developer, I want API keys to be generated per client, so that I can control usage and revoke access if needed.** | • `/api/keys` endpoint (admin only) creates a UUID key linked to a client name.<br>• All event POSTs must include `X-API-Key` header; invalid keys return 401.<br>• Usage count stored per key for future rate‑limiting. |

### **Epic E5 – Security & Privacy**

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E5‑01** | **As a compliance officer, I want all stored personal identifiers to be hashed, so that raw PII never resides in the database.** | • Visitor IDs are SHA‑256 hashes of a random UUID generated client‑side.<br>• No plain‑text IP addresses or user agents stored (optional anonymized aggregates only). |
| **E5‑02** | **As a security engineer, I want rate limiting on the ingest endpoint, so that abusive traffic cannot overwhelm the service.** | • 100 requests per minute per API key.<br>• Exceeding limit returns 429 with `Retry-After` header. |
| **E5‑03** | **As a GDPR‑focused user, I want a “Delete My Data” endpoint, so that I can request removal of my analytics record.** | • POST `/api/delete` with visitor hash and valid API key.<br>• All events for that visitor are permanently removed.<br>• Returns 200 on success. |

### **Epic E6 – Export & Alerting**

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E6‑01** | **As a data scientist, I want to export raw events for a given day as JSON, so that I can run offline analyses.** | • `/api/export?date=YYYY-MM-DD` returns a streamed JSON array of events.<br>• Authenticated admin only.<br>• Response size limited to 100 k rows per request (pagination available). |
| **E6‑02** | **As a product owner, I want to configure a daily email alert when conversion rate drops below 1 %, so that we can react quickly.** | • Alert rule UI under “Settings → Alerts”.<br>• Email sent via configurable SMTP when condition met.<br>• Alert includes date, current rate, and trend chart. |

---

## MVP Scope (Stories to ship in first release)

1. **E1‑01**, **E1‑02**, **E1‑03**, **E1‑04** – Core client SDK.  
2. **E2‑01**, **E2‑02** – Event persistence & daily aggregation.  
3. **E3‑01**, **E3‑02**, **E3‑03**, **E3‑04** – Secure dashboard with key visualizations and export.  
4. **E4‑01**, **E4‑02** – Docker deployment and API‑key authentication.  

*All other stories are slated for post‑MVP iterations.*

--- 

*Prepared by the senior product/engineering lead, 2026‑06‑24.*
