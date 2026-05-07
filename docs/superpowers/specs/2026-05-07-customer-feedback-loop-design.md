# Customer Feedback Loop — Revised Design

> **Product:** Visual Studio Code (microsoft/vscode)
> **Live URL (target):** https://shayalpatel.github.io/CustomerFeedback
> **Status:** Design — supersedes FEEDBACKPLAN.md v1.0
> **Date:** 2026-05-07

---

## 1. What we're building

A demo dashboard that takes customer feedback from multiple sources, sorts each item into **Bug**, **Feature Request**, or **UX Issue**, and shows the results in a public web page. The user triggers a refresh by asking Claude conversationally:

> "Refresh the feedback page"

Claude reads new items, classifies them, updates the dashboard, and pushes to GitHub Pages. The user can then ask follow-up questions like "any sidebar bugs?" — Claude answers from the processed data.

This is a portfolio / demo project. Mock data is acceptable for non-GitHub sources.

---

## 2. What changed from the original plan

The original plan (FEEDBACKPLAN.md) had four critical problems:

1. **Context window overflow** — the Claude skill tried to classify all ~2,800 items in one conversation. Won't fit.
2. **Two classifiers writing the same files** — a daily Python cron would erase Claude's higher-quality work overnight.
3. **`dashboard/index.html` was never actually created** — referenced everywhere, defined nowhere.
4. **TF-IDF clustering had a greedy assignment bug** — items locked to the first matching cluster, not the best one.

This design fixes all four by **simplifying to a single classifier (Claude only) running on user-triggered, incremental refreshes.**

What was removed:

- Python `SmartFeedbackClassifier` regex engine
- `SimpleClustering` TF-IDF code
- GitHub Actions daily cron
- `needs_review.json` coordination file
- The two-layer classification model entirely

What was added:

- Incremental ID-based classification (only process new items)
- Batched processing inside one skill run (~100 items per batch, loop as needed)
- An explicit phase to build the dashboard HTML template

---

## 3. Architecture overview

```
                ┌─────────────────────────────────────────────┐
                │  data/raw/*.json    (mock data + GH issues) │
                └──────────────────┬──────────────────────────┘
                                   │
                  User says "Refresh the feedback page"
                                   │
                                   ▼
                ┌─────────────────────────────────────────────┐
                │   Claude Code skill: refresh-feedback       │
                │                                             │
                │   1. Find new items (ID-based diff)         │
                │   2. Classify in batches of ~100            │
                │   3. Append to feedback_classified.json     │
                │   4. Rebuild feedback_summary.json          │
                │   5. Inject data into dashboard/index.html  │
                │   6. git commit + push                      │
                └──────────────────┬──────────────────────────┘
                                   │
                                   ▼
              https://shayalpatel.github.io/CustomerFeedback
                                   │
                                   ▼
                  User asks: "any sidebar bugs?"
                  Claude reads feedback_summary.json → answers
```

**One classifier. One source of truth. No cron. No coordination.**

---

## 4. Components

### 4.1 Raw data files (`data/raw/`)

Static mock JSON files plus a live GitHub issues fetcher. Every item has a unique `id` field.

| File | Source | Lifecycle |
|---|---|---|
| `github_issues.json` | Live: `microsoft/vscode` GitHub API | Refreshed by `fetch_feedback.py` |
| `mock_surveys.json` | Mock: NPS/CSAT/email | Static |
| `mock_support_tickets.json` | Mock: support tickets | Static |
| `mock_in_app.json` | Mock: in-app widget | Static |
| `mock_community.json` | Mock: Reddit / Stack Overflow / Tech Community | Static |
| `mock_reviews.json` | Mock: G2 / Capterra | Static |

**Raw item schema** (unchanged from original plan):

```json
{
  "id": "gh-12847",
  "source": "github_issues",
  "source_type": "external",
  "timestamp": "2026-05-05T07:23:00Z",
  "raw_text": "Extension host keeps crashing when I open my monorepo...",
  "author_id": "user_a3f9b",
  "rating": null,
  "version": "1.89.1",
  "url": "https://github.com/microsoft/vscode/issues/12847"
}
```

### 4.2 Fetcher script (`scripts/fetch_feedback.py`)

A small Python script the user runs manually before triggering the skill (or as part of the skill itself). Its only job: pull live GitHub issues into `data/raw/github_issues.json`. No classification logic. No external dependencies.

### 4.3 Processed data files (`data/processed/`)

| File | Purpose |
|---|---|
| `feedback_classified.json` | Every classified item, append-only across runs |
| `feedback_summary.json` | Aggregate stats and top clusters (rebuilt fully each run) |
| `clusters.json` | Cluster definitions with member IDs (rebuilt fully each run) |

**Classified item schema:**

```json
{
  "id": "gh-12847",
  "source": "github_issues",
  "timestamp": "2026-05-05T07:23:00Z",
  "raw_text": "Extension host keeps crashing...",
  "category": "bug",
  "sub_category": "crash",
  "sentiment": "negative",
  "urgency": "critical",
  "product_area": "extensions",
  "one_line_summary": "Extension host crashes on large monorepos",
  "cluster_id": "cluster-001",
  "classified_at": "2026-05-07T09:00:12Z"
}
```

(No `confidence` field. No `classified_by` field. Single classifier means single quality bar.)

### 4.4 Dashboard (`dashboard/index.html`)

A self-contained HTML file with embedded CSS and JavaScript. Built once during Phase 0; never regenerated from scratch. Contains data-injection markers Claude finds and replaces:

```html
<script>
/* DATA_START */
const LIVE_DATA = { /* placeholder */ };
/* DATA_END */
</script>
```

#### 4.4.1 Layout (top to bottom)

The dashboard is ordered the way a PM or engineering manager actually scans it: pulse → search → focus areas → action items → real voices → trajectory → provenance.

**Row 1 — Pulse (stat cards):** Total, Bugs, Feature Requests, UX Issues. Clickable; filtering one filters the recent feedback feed below.

**Row 2 — Global search:** A single search bar that filters the clusters list and the recent feedback feed live as you type.

**Row 3 — Where's the heat:**
- Top Product Areas (horizontal bar chart): which VS Code areas are generating the most feedback (extensions, copilot, sidebar, terminal, etc.) — useful for sprint planning.
- Category mix (donut chart): proportional view of bug / feature / UX.

**Row 4 — What to act on (Top Issue Clusters):** The most important section. Each cluster card shows:
- Title (one-line summary of the issue)
- Category badge (BUG / FEATURE / UX)
- Item count and source mix
- Trend indicator (growing / stable / cooling)
- Urgency tag
Clicking a cluster opens a modal with sample texts and the full member list.

**Row 5 — Recent Feedback (real voices):** A filterable feed of the most recent classified items. Filter chips at the top: All / Bugs / Feature Requests / UX Issues. Each row shows the raw quote, source, time, and category. This section is the "human voice" complement to the abstract clusters above — industry-standard pattern in Productboard, Linear, UserVoice, etc., because clusters drive prioritization but verbatims drive empathy.

**Row 6 — Trajectory:** 30-day trend chart with three lines (bug / feature / UX) showing volume over time.

**Row 7 — Where it's coming from:** Compact source breakdown bar chart (GitHub Issues, In-App Widget, NPS Survey, Reddit, etc.).

#### 4.4.2 Interactions

- Stat card click → filters Row 5 (recent feedback) to that category.
- Search bar typing → filters Row 4 (clusters) and Row 5 (feedback) live.
- Cluster click → modal with cluster details and member items.

The search and filtering are pure client-side JavaScript over the data blob embedded in the page. No backend.

### 4.5 The skill (`.claude/skills/refresh-feedback.md`)

The brain. A markdown file with step-by-step instructions Claude follows:

```
1. Read feedback_classified.json → set of classified IDs (empty if file missing)
2. Read all data/raw/*.json → list of all raw items
3. new_items = items whose id is NOT in the classified set
4. If new_items is empty:
     → Skip to step 7
5. For each batch of 100 new items:
     → Classify each (category, sub_category, sentiment, urgency,
        product_area, one_line_summary)
     → Append to feedback_classified.json
6. Identify clusters: group items describing the same underlying issue
   (Claude uses its own judgment — no TF-IDF math)
7. Rebuild feedback_summary.json from the full classified file
8. Inject the new data into dashboard/index.html (between markers)
9. git add . && git commit && git push
10. Report to user: counts, top clusters, anything urgent
```

### 4.6 The trigger (`CLAUDE.md`)

Tells Claude that phrases like "refresh the feedback page", "update feedback", or "scan feedback" should invoke `.claude/skills/refresh-feedback.md`. Also tells Claude that follow-up questions about feedback should be answered from `data/processed/feedback_summary.json`.

---

## 5. How follow-up Q&A works

After a refresh, the user can ask things like:

- "Are there any sidebar bugs?"
- "What's the top feature request?"
- "Anything critical?"

Claude answers by reading `feedback_summary.json` (and `feedback_classified.json` if it needs individual items). It does **not** re-run the pipeline. The summary file is structured to make these questions easy to answer — totals by category, totals by product area, top clusters, critical items.

This works for items classified in any past run. Once an item is in `feedback_classified.json`, Claude can answer questions about it forever.

---

## 6. What this design intentionally does NOT include

- **No daily auto-refresh.** Refreshes happen when the user asks. This is a deliberate trade for simplicity, accuracy, and a better demo story.
- **No paid APIs.** Everything stays inside Claude Code's existing capabilities.
- **No real-time streaming.** Batch processing on user trigger only.
- **No multi-user support.** Single user, single repo, single dashboard.
- **No retroactive re-classification.** Once an item is classified, it stays that way. (If we ever want this, we can add a "re-examine" command later.)
- **No cluster status / resolution tracking.** Clusters do not have an `open` / `acknowledged` / `resolved` state, and the dashboard does not show a resolution-rate progress bar. This was considered and intentionally cut to keep the demo simple.

---

## 7. Implementation phases (high level)

The detailed implementation plan is the next step. At a high level:

1. **Phase 0** — Repo, GitHub Pages, build the static `dashboard/index.html` template with markers
2. **Phase 1** — Create mock data files and validate schemas
3. **Phase 2** — Write `fetch_feedback.py` (GitHub issues fetcher only)
4. **Phase 3** — Write `.claude/skills/refresh-feedback.md` and update `CLAUDE.md`
5. **Phase 4** — End-to-end test: trigger skill, verify dashboard updates, ask follow-up question

No Phase 5. No GitHub Actions. No Python classifier.

---

## 8. Success criteria

The project is done when all of these are true:

- [ ] Saying "Refresh the feedback page" triggers the skill and completes without errors
- [ ] `data/processed/feedback_classified.json` contains every raw item, classified
- [ ] Subsequent refreshes only classify NEW items (verified by checking timestamps)
- [ ] The dashboard at the public URL shows updated counts and clusters
- [ ] Asking "are there any sidebar bugs?" returns a specific, data-grounded answer
- [ ] Asking the same question two days later (with no new data) still works — Claude reads the summary file
