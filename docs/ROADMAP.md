# ROADMAP.md – ideaweb

## Vision
Create a lightweight, privacy‑first analytics platform that lets small‑to‑medium web teams instantly instrument pages, capture core user actions (page views, clicks, conversions), and visualize daily active users (DAU) and conversion rates on an intuitive dashboard. The product will be hosted as a SaaS service with a simple embed script, no‑SQL backend, and real‑time reporting.

---

## MVP (Minimum Viable Product) – **Launch‑Ready** *(Critical Path)*

| Milestone | Description | Success Criteria |
|-----------|-------------|------------------|
| **M1: Core Data Capture** | • Publish a single‑line JavaScript snippet (`<script src="https://cdn.ideaweb.io/track.js"></script>`) <br>• Capture **page view**, **click** (auto‑detect on elements with `data-ideaweb-click`), and **conversion** events (custom `trackConversion()` API). | • >95 % of events received in backend <br>• < 100 ms latency from client to API |
| **M2: Secure, Scalable Ingestion API** | • HTTP POST endpoint (`/api/collect`) <br>• Validate payload, dedupe by client‑generated UUID, store in **PostgreSQL** (or managed columnar store) <br>• Rate‑limit per origin | • 99.9 % uptime in staging <br>• Able to ingest 10 k events/sec (burst) |
| **M3: Daily Aggregation Engine** | • Nightly Spark/SQL job (or db materialized view) that computes **DAU**, **unique clicks**, **conversion counts**, and **conversion rate** per project. | • Aggregations complete < 5 min after midnight UTC |
| **M4: Dashboard UI (MVP)** | • React SPA with: <br>  • Project selector <br>  • Line chart for DAU (last 30 days) <br>  • Bar chart for conversions vs clicks <br>  • Export CSV button | • 5‑minute onboarding flow <br>• No JS console errors on major browsers |
| **M5: Billing & Access Control** | • Stripe integration for **free tier (≤5 k events/mo)** and **paid tier** <br>• API keys per project, role‑based read‑only dashboard access | • 100 % of paid accounts can access data within 5 min of payment |
| **M6: GDPR / Privacy Controls** | • IP anonymization toggle <br>• Data retention policy (30 days default, configurable) <br>• Simple “Delete my data” endpoint | • Pass internal privacy audit; opt‑out works end‑to‑end |

**MVP Launch Target:** **8 weeks** from roadmap start.

---

## Post‑MVP Roadmap

### Phase 1 – v1.0 (Weeks 9‑20)

| Theme | Feature | Description | Ship Date |
|-------|---------|-------------|-----------|
| **Real‑time Reporting** | Live Dashboard | Push updates via WebSocket so metrics refresh within seconds of event arrival. | Week 12 |
| **Advanced Event Taxonomy** | Custom Event Types | SDK method `track(eventName, payload)`; UI for defining event schemas. | Week 14 |
| **Segmentation & Funnels** | Funnel Builder | Drag‑and‑drop funnel steps (e.g., page → click → conversion) with drop‑off visualization. | Week 16 |
| **Export & Integration** | Webhooks & Zapier | Outbound webhook for each conversion; Zapier connector for popular tools. | Week 18 |
| **Performance & Scaling** | Horizontal Ingestion | Deploy ingestion workers behind a load balancer; auto‑scale on Cloud Run / ECS. | Week 20 |

### Phase 2 – v2.0 (Weeks 21‑36)

| Theme | Feature | Description | Ship Date |
|-------|---------|-------------|-----------|
| **User‑level Analytics** | Session Replay (opt‑in) | Record anonymized session flows for paid tier; playback in dashboard. | Week 24 |
| **Privacy‑First Enhancements** | Consent Management | Built‑in CMP integration (IAB TCF) with per‑event consent flag. | Week 26 |
| **Data Warehouse Export** | Snowflake / BigQuery Connectors | Scheduled export of raw events to external warehouses. | Week 30 |
| **AI‑Powered Insights** | Anomaly Detection | ML model flags sudden DAU spikes or conversion drops; alerts via Slack/email. | Week 34 |
| **White‑Label Branding** | Custom Dashboard Themes | SaaS customers can brand the dashboard with their logo & colors. | Week 36 |

### Phase 3 – Long‑Term (Beyond Week 36)

| Theme | Potential Features |
|-------|--------------------|
| **Cross‑Domain Tracking** | Unified user IDs across multiple domains/subdomains. |
| **Mobile SDK** | Native iOS/Android libraries for in‑app analytics. |
| **Marketplace** | Community‑built plugins (e.g., heatmaps, A/B test integration). |
| **Self‑Hosted Option** | Docker‑compose bundle for on‑prem deployments (enterprise). |

---

## Milestone Tracking & Success Metrics

| Metric | Target |
|--------|--------|
| **Time‑to‑Value** (from embed to first dashboard view) | ≤5 min |
| **Event Capture Accuracy** | ≥95 % |
| **Customer Churn (first 90 days)** | ≤5 % |
| **Paid Conversion Rate** (free → paid) | ≥12 % |
| **System Availability** | 99.9 % SLA |

All milestones will be tracked in the **Axentx BRAIN** vector store for continuous validation against market signals and revenue impact.

--- 

*Prepared by the senior product/engineering lead, aligned with Axentx OS chain‑playbook (2026‑06‑21).*
