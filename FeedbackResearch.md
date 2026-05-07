# Customer Feedback Loop — Deep Research Report

> **Purpose:** Foundation document for building an AI agent that scans customer feedback, categorizes it into Feature Requests / Bugs / UX Issues, identifies product improvement opportunities, and surfaces insights in a team-facing web dashboard.

---

## Table of Contents

1. [What Is a Customer Feedback Loop](#1-what-is-a-customer-feedback-loop)
2. [How the Loop Works — The Full Cycle](#2-how-the-loop-works--the-full-cycle)
3. [Where Feedback Comes From — Sources & Channels](#3-where-feedback-comes-from--sources--channels)
4. [How to Acquire Feedback — Collection Methods](#4-how-to-acquire-feedback--collection-methods)
5. [Microsoft as a Case Study](#5-microsoft-as-a-case-study)
6. [Feedback Taxonomy — Feature Requests, Bugs, UX](#6-feedback-taxonomy--feature-requests-bugs-ux)
7. [AI Agent Architecture for Feedback Classification](#7-ai-agent-architecture-for-feedback-classification)
8. [Identifying Product Improvement Opportunities](#8-identifying-product-improvement-opportunities)
9. [The Dashboard — Centralizing Insights for Teams](#9-the-dashboard--centralizing-insights-for-teams)
10. [Recommended Tech Stack for the Full System](#10-recommended-tech-stack-for-the-full-system)
11. [Key Metrics to Track](#11-key-metrics-to-track)
12. [Summary & Next Steps](#12-summary--next-steps)

---

## 1. What Is a Customer Feedback Loop

A **customer feedback loop** is a structured, recurring process by which a company collects input from users, analyzes it, makes product or service changes based on what it learns, and then tells users what changed. The word "loop" is intentional: it never ends. Each change generates new behavior, which generates new feedback.

At a high level there are two kinds of loops:

| Type | Description | Example |
|------|-------------|---------|
| **Positive loop** | Feedback drives improvement → users engage more → more feedback flows in | A bug fix reduces churn; retained users submit richer feature ideas |
| **Negative loop** | Unaddressed feedback erodes trust → users disengage → feedback dries up | Ignored support tickets → users churn silently |

For a company like Microsoft selling a software product (Windows, Office, Azure, Copilot), closing the loop is business-critical at scale: millions of users, dozens of product areas, and feedback arriving 24/7 across many surfaces.

---

## 2. How the Loop Works — The Full Cycle

The canonical customer feedback loop has four stages. At enterprise scale each stage is a system, not a task.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   COLLECT ──► ANALYZE ──► PRIORITIZE & ACT ──► CLOSE THE LOOP  │
│      ▲                                               │          │
│      └───────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Stage 1 — Collect
Gather raw signals from every channel where users express opinions: app reviews, support tickets, NPS surveys, community forums, social mentions, telemetry, and more. The goal is breadth and volume with consistent metadata (timestamp, source, user segment, product area).

### Stage 2 — Analyze
Transform unstructured text into structured insight:
- **Classify** feedback by type (bug, feature request, UX complaint, praise)
- **Cluster** similar items to measure volume and trend
- **Score sentiment** (positive / neutral / negative)
- **Link** to product areas, versions, and user segments
- **Detect urgency** (a single crash report vs. 500 identical reports)

Without this stage the loop collapses under volume. This is exactly where an AI agent delivers leverage.

### Stage 3 — Prioritize & Act
Product and engineering teams review the processed insights, decide what to build or fix, and execute. Prioritization frameworks (RICE, MoSCoW, impact vs. effort) consume the structured output from Stage 2. Without structure from Stage 2, prioritization is political and slow.

### Stage 4 — Close the Loop
Communicating back to users: "We heard you. Here's what we changed." This is the most neglected stage at large companies. Closing the loop builds trust, increases future response rates, and turns critics into advocates. Methods include:
- In-app changelogs
- Email updates to users who submitted the feedback item
- Community forum responses ("This is now fixed in v2.3")
- Public roadmap updates

---

## 3. Where Feedback Comes From — Sources & Channels

Feedback sources split into **direct** (user deliberately sends feedback to you) and **indirect** (user expresses opinion in a venue you must monitor).

### Direct Sources

| Source | What It Captures | Typical Volume |
|--------|-----------------|----------------|
| **In-app surveys (NPS, CSAT, CES)** | Satisfaction scores + open text at a moment-in-use | Medium — triggered |
| **Support tickets / help desk** | Bugs, confusion, blockers — high pain signal | High — always on |
| **Feedback forms / widgets** | Explicit feature requests and bug reports | Low-Medium |
| **User interviews / usability tests** | Deep qualitative insight | Low — scheduled |
| **Beta / Insider programs** | Early adopter reports before GA release | Medium |
| **Advisory boards / councils** | Enterprise customer strategic input | Very Low |
| **Email surveys** | Post-interaction or periodic relationship NPS | Medium |

### Indirect Sources

| Source | What It Captures | Tools to Monitor |
|--------|-----------------|-----------------|
| **App Store / Google Play reviews** | Public sentiment, bugs discovered by many users | AppFollow, AppBot, Sensor Tower |
| **G2 / Capterra / Trustpilot** | Competitive comparisons, feature gaps, UX pain | Review scraping APIs |
| **Twitter/X, Reddit, LinkedIn** | Real-time reactions, viral bug reports | Sprinklr, Brandwatch, Mention |
| **Community / developer forums** | Deep technical feedback, workarounds users invented | Microsoft Tech Community, Stack Overflow |
| **Product telemetry / usage analytics** | Behavioral feedback — what users *do* not just what they *say* | Mixpanel, Amplitude, Azure Monitor |
| **Sales / CS call notes** | Verbatim objections and pain points from key accounts | Gong, Salesforce notes |
| **Churn surveys** | Why users cancelled — the most honest feedback | Wootric, Churnkey |

### The Microsoft-Specific Mix
For a product like Microsoft 365, the sources look like:
- **Feedback Hub** (Windows) and **in-app smiley/thumbs buttons** (Office, Teams, Edge)
- **Microsoft Feedback Portal** (feedbackportal.microsoft.com) — public upvoting
- **UserVoice / Azure Feedback** (feedback.azure.com) — developer community ideas
- **Microsoft Tech Community** forums
- **Dynamics 365 Customer Voice** — enterprise survey platform Microsoft uses internally and sells
- **Telemetry / Watson** crash reports with automatic diagnostic data
- **NPS surveys** deployed quarterly to M365 admin contacts
- **Customer Support tickets** via Microsoft's CSS (Customer Support Services) system

---

## 4. How to Acquire Feedback — Collection Methods

Getting feedback is harder than it looks. Low response rates, selection bias, and inactionable phrasing are the three classic failure modes.

### Design Principles for Effective Collection

**Trigger contextually.** The best moment to ask is immediately after a user completes (or fails) a task. An in-app nudge 30 seconds after the user finishes publishing a report outperforms an emailed survey two weeks later by 5–10x in response rate and specificity.

**Ask one question at a time.** NPS: "How likely are you to recommend [product] to a colleague?" Follow up with one open-text "why?" NPS alone is a lagging indicator; the open text is the signal.

**Make it optional, fast, and low-friction.** Feedback widgets that appear over a task interrupt flow. A persistent "Give feedback" button lets users initiate on their terms.

**Combine quantitative + qualitative.** Quantitative (star ratings, scores) gives you trend data. Qualitative (open text, recordings) gives you the "why" behind the number.

**Close the loop visibly.** Users submit more future feedback when they see evidence past feedback was acted on.

### Collection Playbook by Feedback Type

| Goal | Method | Timing |
|------|--------|--------|
| Measure overall satisfaction | NPS survey | Quarterly / after 90 days of use |
| Measure task success | CES (Customer Effort Score) | Immediately after completing a key task |
| Spot immediate frustration | In-app smiley widget | Persistent / always available |
| Catch bugs | In-app bug report with auto screenshot | Post-error / always available |
| Understand feature needs | Feature request board | Persistent / community |
| Understand churn reasons | Exit/churn survey | On cancel / uninstall |
| Deep qualitative insight | Moderated user interview | Monthly / on-demand |

---

## 5. Microsoft as a Case Study

Microsoft is one of the most instructive examples of enterprise-scale feedback management because they operate across multiple product lines (Windows, Office, Azure, Xbox, Surface, Copilot) each with distinct user types.

### Microsoft's Feedback Architecture

#### Layer 1 — In-Product Capture
Every major Microsoft product has embedded feedback mechanisms:
- **Feedback Hub** (Windows 10/11): A dedicated app pre-installed on Windows. Users submit bug reports or feature suggestions with optional diagnostic data (telemetry, screen recordings). The app links to user telemetry settings so Microsoft can correlate crash data with feedback text automatically.
- **Office in-app "Thumbs" and "Smiley" buttons**: Embedded in the ribbon/toolbar. Captures quick sentiment plus optional open text without pulling users out of flow.
- **"Help us improve" prompts**: Contextual prompts triggered by telemetry signals (e.g., user spent >30 seconds on an error state → prompt appears).

#### Layer 2 — Community & Portal
- **Microsoft Feedback Portal** (feedbackportal.microsoft.com): Users submit and upvote ideas publicly. Product teams monitor vote velocity, not just raw counts. A spike in votes on a previously static item signals a newly triggered pain point.
- **Azure Feedback** (feedback.azure.com): Separate portal for Azure services. Historically used UserVoice; migrated to the Microsoft-hosted portal.
- **Microsoft Tech Community**: Forums per product. Engineers actively participate. This is where power users and IT admins provide the deepest technical feedback.

#### Layer 3 — Enterprise & Commercial
- **Dynamics 365 Customer Voice**: Microsoft's own survey + feedback product, used internally. Sends NPS surveys to M365 commercial admins. Integrates with Dynamics 365 CRM so feedback is linked to account health scores.
- **TAM (Technical Account Manager) feedback**: TAMs for large enterprise accounts collect verbal feedback in QBRs (Quarterly Business Reviews) and log it structured in internal systems.
- **Customer Advisory Boards (CABs)**: Select enterprise customers participate in monthly product reviews. Their feedback has outsized weight.

#### Layer 4 — Telemetry (Behavioral Data)
Microsoft's **Watson** error reporting system and **Application Insights / Azure Monitor** collect crash dumps, error frequencies, feature usage rates, and performance data. This is *behavioral* feedback — what users do, not what they say. It is often more reliable than stated feedback because it is free from social desirability bias.

#### How Microsoft Closes the Loop
- **"Ideas in Progress" / "Completed" status tags** on the Feedback Portal
- **Blog posts and "What's New"** content linked from feedback items
- **In-product changelogs** in Office and Windows
- **Release notes** that reference UserVoice/Feedback Portal vote counts ("Top requested feature: now available")

### Key Lesson from Microsoft
At enterprise scale, the challenge is not collecting feedback — it is connecting feedback to decision-making. Microsoft's internal tooling links portal votes → product area backlog → engineering sprint. The human bottleneck is triaging the volume. An AI agent that pre-classifies and clusters before a PM ever sees the queue is the unlock.

---

## 6. Feedback Taxonomy — Feature Requests, Bugs, UX

For the agent to classify feedback, a precise taxonomy is needed. Here is the industry-standard three-category framework plus sub-dimensions.

### Category Definitions

#### Bug Report
> The product does not behave as expected based on its documentation, stated behavior, or previously working functionality.

**Signals in text:**
- "crashes," "error," "broken," "stopped working," "can't," "fails," "unexpected," "regression"
- Description of steps + unexpected outcome
- Version or environment details

**Required metadata for a useful bug:**
- Steps to reproduce
- Expected vs. actual behavior
- Frequency (always / sometimes / once)
- Environment (OS, version, browser)
- Severity (blocking workflow vs. minor annoyance)

**Examples:**
- "The app crashes every time I try to export to PDF on Windows 11."
- "After the last update, dark mode stopped working in the settings panel."

---

#### Feature Request
> The product works as intended, but the user wants a capability it does not currently have.

**Signals in text:**
- "wish," "would be great," "please add," "why can't," "need a way to," "should have," "missing feature"
- Comparison to a competitor ("like Notion does")
- Workaround description ("I have to manually do X every time")

**Required metadata:**
- The desired capability
- The user's underlying job-to-be-done (not just the solution they proposed)
- Frequency of the need
- Business impact if not available

**Examples:**
- "I wish I could bulk-archive projects instead of doing them one at a time."
- "It would be great to have a Slack integration so I get notified when a comment is left."

---

#### User Experience (UX) Issue
> The product works as intended but is confusing, inefficient, frustrating, or inaccessible to use.

**Signals in text:**
- "confusing," "hard to find," "took forever," "not intuitive," "too many clicks," "overwhelming," "can't figure out"
- Task abandonment implied in context
- Accessibility or localization complaints

**Required metadata:**
- The user's goal
- Where they got stuck or felt friction
- What they tried
- The outcome (gave up, found workaround, called support)

**Examples:**
- "I can never find the export button — it's buried under three menus."
- "The onboarding flow is overwhelming. I didn't understand what to do first."

---

### Extended Taxonomy (Optional Depth)

| Sub-Category | Parent | Description |
|---|---|---|
| Performance Issue | Bug | Slowness, lag, timeout — product works but is unacceptably slow |
| Reliability Issue | Bug | Intermittent failures, data loss |
| Integration Request | Feature Request | Connect with a third-party tool |
| New Feature | Feature Request | Net-new capability |
| Enhancement | Feature Request | Improve an existing feature |
| Navigation UX | UX Issue | Can't find things |
| Cognitive Load UX | UX Issue | Too complex, too many steps |
| Visual Design UX | UX Issue | Layout, spacing, typography problems |
| Accessibility | UX Issue | Screen readers, keyboard nav, contrast |
| Praise | — | Positive reinforcement; tells you what to protect |
| Churn Signal | — | Indication user may leave; high urgency flag |

---

## 7. AI Agent Architecture for Feedback Classification

### Overview

The agent is a pipeline that runs continuously (or on a schedule), pulling raw feedback from multiple sources, classifying each item into the taxonomy, clustering similar items, scoring sentiment, and writing structured records to a database. It also surfaces emerging trends and high-urgency signals.

### System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FEEDBACK AI AGENT                               │
│                                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────────────┐   │
│  │  INGESTION   │    │  PROCESSING  │    │       STORAGE          │   │
│  │              │    │              │    │                        │   │
│  │ • App Store  │───►│ • Clean text │───►│  PostgreSQL / Supabase │   │
│  │ • Support    │    │ • Classify   │    │  (structured records)  │   │
│  │   tickets    │    │   category   │    │                        │   │
│  │ • Surveys    │    │ • Sentiment  │    │  Pinecone / pgvector   │   │
│  │ • Reviews    │    │   scoring    │    │  (vector embeddings    │   │
│  │ • Community  │    │ • Embedding  │    │   for clustering)      │   │
│  │   forums     │    │ • Clustering │    │                        │   │
│  │ • Slack/CRM  │    │ • Urgency    │    └────────────────────────┘   │
│  └──────────────┘    │   detection  │              │                  │
│                      │ • Dedup      │              ▼                  │
│                      └──────────────┘    ┌─────────────────────┐     │
│                                          │    INSIGHT ENGINE   │     │
│                                          │                     │     │
│                                          │ • Trend detection   │     │
│                                          │ • Weekly digest     │     │
│                                          │ • Alert on spike    │     │
│                                          │ • Roadmap signal    │     │
│                                          └─────────────────────┘     │
│                                                     │                 │
└─────────────────────────────────────────────────────│─────────────────┘
                                                      │
                                                      ▼
                                           ┌────────────────────┐
                                           │   WEB DASHBOARD    │
                                           │   (Team Portal)    │
                                           └────────────────────┘
```

### Ingestion Layer

Each feedback source requires a **connector**:

| Source | Method |
|--------|--------|
| App Store (Apple) | App Store Connect API or scraping |
| Google Play | Google Play Developer API |
| G2 / Capterra | Review APIs or scraping |
| Zendesk / Freshdesk | REST API with pagination |
| Salesforce / CRM notes | Salesforce API |
| Intercom | Intercom API (conversations, tickets) |
| Community forums | RSS / web scraping / forum APIs |
| Email surveys | SurveyMonkey / Typeform API |
| CSV upload | For one-off batches from partners |

Each item ingested should carry: `source`, `timestamp`, `user_id` (hashed for privacy), `product_area` (if known), `raw_text`, `rating` (if applicable), `version` (if known).

### Processing Layer — Classification with LLM

The classification step is the heart of the agent. A modern LLM (Claude, GPT-4o) with a well-designed system prompt achieves >95% accuracy on the Bug / Feature Request / UX taxonomy when given a few examples (few-shot prompting).

**System prompt design principles:**
- Define each category with precise language (see Section 6)
- Include 2–3 labeled examples per category in the prompt
- Ask the model to return structured JSON: `{category, sub_category, sentiment, urgency, product_area, summary, confidence}`
- Use temperature = 0 for deterministic, consistent classification
- Run human review on items with confidence < 0.7

**Example classification prompt structure:**
```
You are a product feedback analyst. Classify the following customer feedback item.

Categories:
- "bug": product behaves unexpectedly or is broken
- "feature_request": user wants a capability that doesn't exist
- "ux_issue": product works but is confusing/frustrating to use
- "praise": positive feedback
- "churn_signal": user expresses intent to leave

Return JSON only:
{
  "category": "<category>",
  "sub_category": "<sub_category>",
  "sentiment": "positive|neutral|negative",
  "urgency": "low|medium|high|critical",
  "product_area": "<inferred area or null>",
  "one_line_summary": "<10-word summary>",
  "confidence": 0.0-1.0
}

Feedback: "{raw_text}"
```

### Clustering & Deduplication

After classification, similar items need to be grouped. Approach:
1. Generate **text embeddings** for each classified item (OpenAI `text-embedding-3-small`, Claude Embeddings, or Voyage)
2. Store embeddings in a **vector database** (Pinecone, pgvector extension in PostgreSQL, Supabase Vector)
3. Run **cosine similarity** clustering to group items with similarity > 0.85
4. Each cluster gets a **canonical issue** record with: representative summary, item count, trend (growing/stable/shrinking), source distribution

This transforms 10,000 individual complaints about "the export button" into one cluster with `count: 847, trend: +23% this week`.

### Urgency & Trend Detection

Beyond per-item classification, the insight engine runs aggregate analysis:
- **Spike detection**: if a cluster grows >50% week-over-week → alert
- **New cluster emergence**: a topic that didn't exist last month → alert
- **Negative sentiment shift**: NPS or per-area sentiment drops 10+ points → alert
- **Cross-source correlation**: same bug appearing in support tickets AND app store reviews → higher urgency

---

## 8. Identifying Product Improvement Opportunities

The agent should not just report feedback volume — it should generate **actionable opportunity signals**.

### Opportunity Identification Framework

| Signal | Meaning | Action |
|--------|---------|--------|
| High-volume bug cluster with critical urgency | Widespread broken experience | Escalate to on-call engineering |
| Feature request cluster growing fast + mentioned by high-value accounts | High-ROI roadmap candidate | Flag for PM review / roadmap |
| UX issue cluster tied to high churn rate | Friction killing retention | Prioritize UX sprint |
| Drop in praise around a specific feature after a release | Release regression | Engineering investigation |
| Competitor mentioned in >5% of feature requests | Market positioning gap | Flag for product strategy |

### Linking Feedback to Performance Data

The agent becomes significantly more powerful when feedback is joined with product telemetry:

```
Feedback cluster: "Search is slow" (823 reports this month, +40% WoW)
  +
Telemetry: p99 search latency = 4.2s (was 1.1s before the v4.2 deploy)
  =
Root cause hypothesis: v4.2 deploy introduced search regression
  →
Auto-create: P1 engineering ticket with linked feedback cluster + latency chart
```

This correlation between qualitative feedback and quantitative telemetry is the difference between a feedback dashboard and a product intelligence system.

---

## 9. The Dashboard — Centralizing Insights for Teams

### What the Dashboard Needs to Do

Different teams need different views of the same underlying data:

| Team | What They Need | Dashboard View |
|------|---------------|----------------|
| **Product Management** | Roadmap prioritization signals | Feature request clusters ranked by volume + growth + customer segment |
| **Engineering** | Bug triage queue | Bug list with severity, reproducibility, affected versions |
| **UX/Design** | Friction patterns | UX issue clusters with user journey mapping |
| **Customer Success** | Account-specific feedback | Filter by company/segment to prep for QBR |
| **Executive / VP** | Health metrics | NPS trend, sentiment by product area, open critical issues |
| **Support** | Ticket patterns | Emerging support topics before they become crises |

### Core Dashboard Features

**1. Overview / Home**
- Total feedback received this period vs. last period
- Category breakdown donut chart (Bug / Feature / UX / Praise)
- Sentiment trend line (30/60/90 days)
- Top 5 fastest-growing clusters
- Critical alerts (spike detected, regression suspected)

**2. Feedback Feed**
- Searchable, filterable list of all feedback items
- Filters: category, sentiment, source, product area, date range, urgency
- Each item shows: source icon, date, raw text, AI-assigned category badge, sentiment color, cluster membership
- Click into an item to see full text and similar items

**3. Cluster / Theme Explorer**
- Visual grid or list of all active clusters
- Each cluster card: title, item count, trend arrow, top sources, sentiment
- Click into a cluster to see all constituent items
- "Mark as roadmap candidate" / "Create Jira ticket" action buttons

**4. Trends & Analytics**
- Sentiment over time by product area (line charts)
- Volume by source (bar chart — where is feedback coming from?)
- Category mix over time (stacked area chart)
- NPS / CSAT score trends
- Word cloud of most frequent terms per category

**5. Action Board**
- PM-curated list of opportunities being considered or in progress
- Status: `Reviewing` / `On Roadmap` / `In Development` / `Shipped` / `Declined`
- Link back to the cluster it came from

**6. Alerts & Digest**
- Configurable alerts: "Notify me when Bug cluster X exceeds 100 items"
- Weekly digest email: top 5 insights, one-sentence each, with links

### Dashboard Design Principles

- **Single source of truth**: all feedback, regardless of original source, lives here
- **Searchable**: full-text search across all feedback text
- **Actionable**: every insight has a next-step affordance (create ticket, mark roadmap, dismiss)
- **Role-aware**: PM view vs. engineering view vs. exec view — same data, different emphasis
- **Real-time or near-real-time**: refresh at most every few hours; daily is acceptable
- **Shareable**: individual cluster pages have stable URLs for linking in Slack or Notion

---

## 10. Recommended Tech Stack for the Full System

### Agent Backend (Data Pipeline)

| Component | Recommended Tool | Why |
|-----------|-----------------|-----|
| Orchestration / scheduling | **Python + Celery** or **n8n** or **Apache Airflow** | Runs connectors on schedule, handles retries |
| LLM classification | **Claude API (claude-sonnet-4-6)** | High accuracy, structured JSON output, cost-effective |
| Embeddings | **OpenAI text-embedding-3-small** or **voyage-3** | Fast, cheap, high quality for clustering |
| Vector store | **pgvector** (in Postgres) or **Pinecone** | pgvector is simpler if already using Postgres; Pinecone for scale |
| Primary database | **PostgreSQL** (via Supabase) | Structured storage, SQL for analytics, free tier available |
| API layer | **FastAPI** (Python) | Fast, typed, auto-docs |
| Queue | **Redis + Celery** or **BullMQ** (Node) | Async processing of ingested items |

### Web Dashboard (Frontend)

| Component | Recommended Tool | Why |
|-----------|-----------------|-----|
| Framework | **Next.js 14+ (App Router)** | Server components for performance, excellent TypeScript support |
| UI library | **shadcn/ui + Tailwind CSS** | Composable, design-system-ready components |
| Charts | **Recharts** or **Tremor** | Tremor is built for dashboards; Recharts more flexible |
| State | **React Query (TanStack Query)** | Auto-caching, background refetch for live data |
| Auth | **NextAuth.js** or **Clerk** | Team authentication with Google SSO |
| Data fetching | REST from FastAPI or **tRPC** if full TypeScript | Type-safe end-to-end |

### Deployment

| Component | Option |
|-----------|--------|
| Backend API | **Render**, **Railway**, or **AWS ECS** |
| Database | **Supabase** (managed Postgres + pgvector built-in) |
| Frontend | **Vercel** (native Next.js deployment) |
| Cron jobs | **Render Cron Jobs** or **GitHub Actions** scheduled workflows |

### Infrastructure Simplicity Note
For an MVP, the entire stack can run as:
- **Supabase** = database + pgvector + auth + storage
- **Vercel** = Next.js frontend + API routes (replaces FastAPI for simpler cases)
- **Claude API** = classification
- **GitHub Actions** = scheduled ingestion runs

This keeps operational overhead minimal while being fully production-capable.

---

## 11. Key Metrics to Track

### Feedback Health Metrics

| Metric | Description | Good Signal |
|--------|-------------|------------|
| **NPS (Net Promoter Score)** | % promoters minus % detractors | Trending up; >40 for software |
| **CSAT** | % satisfied on recent interaction | >85% |
| **CES** | Effort to complete a task | Lower is better |
| **Feedback volume by category** | Mix of Bug/Feature/UX over time | Bugs declining; Feature requests growing |
| **Time to close loop** | How long from feedback to response | <2 weeks for bugs; <1 quarter for features |
| **Cluster resolution rate** | % of top clusters with a roadmap response | >70% of top-20 clusters acknowledged |

### Agent Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Classification accuracy** | % of items correctly categorized (vs. human spot-check) | >92% |
| **Coverage** | % of incoming feedback processed within 24h | >99% |
| **Cluster coherence** | Are clustered items actually about the same thing? | Spot-check weekly |
| **False positive alerts** | Spike alerts that turned out to be noise | <10% of alerts |

---

## 12. Summary & Next Steps

### What We Now Know

1. **A customer feedback loop** is a permanent organizational system, not a project. It must be automated at scale because human triage of volume is the bottleneck.

2. **Feedback comes from many sources** simultaneously: in-product widgets, app store reviews, support tickets, surveys, community forums, sales notes, and telemetry. A useful system aggregates all of them.

3. **Microsoft's model** shows that multi-layer collection (in-product → portal → enterprise → telemetry) combined with public community voting, active engineer participation in forums, and status tags on feedback items is the gold standard for enterprise software.

4. **The three-category taxonomy** (Bug / Feature Request / UX Issue) is the right starting point. It is simple enough to explain in 5 minutes, specific enough to drive different team actions, and extensible with sub-categories as the system matures.

5. **An LLM-based classification agent** (Claude API with few-shot prompting + JSON mode) can achieve >92% accuracy and processes thousands of items per hour. Clustering via vector embeddings turns individual items into trend-level insight.

6. **The dashboard** is the team-facing layer. Different roles (PM, Engineering, UX, Exec, CS) need different views, but all consume the same underlying structured data. Next.js + shadcn/ui + Supabase is a strong, minimal-ops stack.

### Recommended Implementation Sequence

```
Phase 1 — Foundation
  └─ Build ingestion connectors for top 2-3 sources (support tickets + app reviews)
  └─ LLM classification pipeline with Claude API
  └─ PostgreSQL schema for classified feedback items

Phase 2 — Intelligence
  └─ Add vector embeddings + clustering
  └─ Trend detection + spike alerts
  └─ Weekly digest email

Phase 3 — Dashboard
  └─ Next.js web app with overview, feed, and cluster views
  └─ Role-based access (PM / Eng / Exec views)
  └─ Action board (roadmap candidate tracking)

Phase 4 — Closing the Loop
  └─ Jira / Linear integration to create tickets from clusters
  └─ Status updates pushed back to feedback portal
  └─ Performance data (telemetry) joined with feedback clusters
```

---

*Report compiled: May 2, 2026*
*Working directory: Customer Feedback Loop*
