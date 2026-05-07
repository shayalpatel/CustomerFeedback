# Customer Feedback Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude-powered feedback classification system that reads customer feedback from JSON files, classifies each item, and displays results in a live GitHub Pages dashboard.

**Architecture:** Single Claude classifier triggered by saying "Refresh the feedback page." Incremental processing — only new items get classified (ID-based diff). Dashboard is a static HTML template with data injected between markers. No Python classifier, no GitHub Actions cron.

**Tech Stack:** Python 3 (stdlib only) for data fetching, HTML/CSS/JS with Chart.js for dashboard, Claude Code skill (Markdown) for classification.

**Design spec:** `docs/superpowers/specs/2026-05-07-customer-feedback-loop-design.md`

---

## File Structure

```
Customer Feedback Loop/
├── CLAUDE.md                              # Modified — add skill trigger
├── dashboard/
│   └── index.html                         # Modified — restructure layout, add search/product-areas chart, data markers
├── data/
│   ├── raw/
│   │   ├── github_issues.json             # Create — 15 mock GitHub issues
│   │   ├── mock_surveys.json              # Create — 10 mock NPS/CSAT/email
│   │   ├── mock_support_tickets.json      # Create — 8 mock support tickets
│   │   ├── mock_in_app.json               # Create — 8 mock in-app widget
│   │   ├── mock_community.json            # Create — 10 mock Reddit/SO/TC
│   │   └── mock_reviews.json              # Create — 6 mock G2/Capterra
│   └── processed/
│       └── .gitkeep                       # Exists — skill writes here
├── scripts/
│   └── fetch_feedback.py                  # Create — GitHub issues fetcher
└── .claude/
    └── skills/
        └── refresh-feedback.md            # Create — the Claude skill
```

---

## Task 1: Create mock data files

Create 6 JSON files in `data/raw/` with realistic VS Code feedback. These are the raw inputs the Claude skill will classify.

**Files:**
- Create: `data/raw/github_issues.json`
- Create: `data/raw/mock_surveys.json`
- Create: `data/raw/mock_support_tickets.json`
- Create: `data/raw/mock_in_app.json`
- Create: `data/raw/mock_community.json`
- Create: `data/raw/mock_reviews.json`

Every item in every file must follow this schema:

```json
{
  "id": "string — unique across ALL files (prefix with source: gh-, nps-, csat-, email-, st-, iaw-, reddit-, so-, tc-, g2-, cap-)",
  "source": "github_issues | nps_survey | csat_survey | email_survey | support_ticket | in_app_widget | reddit | stack_overflow | tech_community | g2_review | capterra_review",
  "source_type": "external | survey | internal | social",
  "timestamp": "ISO 8601 — dates between 2026-04-06 and 2026-05-06",
  "raw_text": "string — 1-3 sentences of realistic feedback text",
  "author_id": "string — anonymized user ID",
  "rating": "number | null — only for surveys/reviews (NPS 0-10, CSAT 1-5, G2 1-5)",
  "version": "string | null — VS Code version like 1.89.0 or 1.89.1",
  "url": "string | null — link for external sources, null for internal/survey"
}
```

- [ ] **Step 1: Create `data/raw/github_issues.json`**

15 items. Source: `github_issues`, source_type: `external`. Distribution: 6 bugs (2 crashes, 2 performance, 2 unexpected behavior), 5 feature requests, 4 UX issues. Product areas to cover: extensions, copilot, terminal, sidebar, editor, git, debugging. Include items that naturally cluster (e.g., 3 about extension host crashes, 2 about copilot latency).

Example items to follow as a pattern:

```json
[
  {
    "id": "gh-12847",
    "source": "github_issues",
    "source_type": "external",
    "timestamp": "2026-05-05T07:23:00Z",
    "raw_text": "Extension host keeps crashing when I open my monorepo with 40+ packages. Happens every time after about 5 minutes.",
    "author_id": "gh_user_38291",
    "rating": null,
    "version": "1.89.1",
    "url": "https://github.com/microsoft/vscode/issues/12847"
  },
  {
    "id": "gh-12831",
    "source": "github_issues",
    "source_type": "external",
    "timestamp": "2026-05-04T14:10:00Z",
    "raw_text": "The sidebar panels can't be resized independently — they all move together. Frustrating when I want a large file explorer but a small outline panel.",
    "author_id": "gh_user_55102",
    "rating": null,
    "version": "1.89.0",
    "url": "https://github.com/microsoft/vscode/issues/12831"
  },
  {
    "id": "gh-12756",
    "source": "github_issues",
    "source_type": "external",
    "timestamp": "2026-04-28T09:45:00Z",
    "raw_text": "Please add multi-cursor support to Find and Replace. Sublime Text has this and it saves a ton of time for bulk edits.",
    "author_id": "gh_user_71044",
    "rating": null,
    "version": null,
    "url": "https://github.com/microsoft/vscode/issues/12756"
  }
]
```

Generate 12 more items following this pattern. Ensure IDs are unique and increment (gh-12xxx range).

- [ ] **Step 2: Create `data/raw/mock_surveys.json`**

10 items. Mix of sources: 4 `nps_survey` (rating 0-10), 3 `csat_survey` (rating 1-5), 3 `email_survey` (rating null). Source_type: `survey`. Distribution: 3 feature requests, 3 bugs, 2 UX issues, 2 praise. Product areas: copilot, search, settings, workspaces, editor.

Example:

```json
{
  "id": "nps-4821",
  "source": "nps_survey",
  "source_type": "survey",
  "timestamp": "2026-05-04T11:30:00Z",
  "raw_text": "NPS Score: 8/10. Would love multi-cursor support in Find and Replace. Currently I have to run multiple searches which is slow.",
  "author_id": "user_U4821",
  "rating": 8,
  "version": "1.89.1",
  "url": null
}
```

- [ ] **Step 3: Create `data/raw/mock_support_tickets.json`**

8 items. Source: `support_ticket`, source_type: `internal`. Distribution: 5 bugs (skewed toward bugs — support tickets are mostly problems), 2 feature requests, 1 UX issue. Include urgency indicators in the text ("blocking my work", "data loss", "every time").

Example:

```json
{
  "id": "st-4421",
  "source": "support_ticket",
  "source_type": "internal",
  "timestamp": "2026-05-04T16:45:00Z",
  "raw_text": "Copilot suggestions have a noticeable 3-4 second delay on my home internet. Same code completes instantly at the office. This is blocking my workflow.",
  "author_id": "user_E8832",
  "rating": null,
  "version": "1.89.1",
  "url": null
}
```

- [ ] **Step 4: Create `data/raw/mock_in_app.json`**

8 items. Source: `in_app_widget`, source_type: `internal`. Distribution: 3 bugs, 2 feature requests, 2 UX issues, 1 praise. Short, casual text (these come from a quick feedback widget).

Example:

```json
{
  "id": "iaw-1001",
  "source": "in_app_widget",
  "source_type": "internal",
  "timestamp": "2026-05-05T09:12:00Z",
  "raw_text": "Extension host crashed again mid-session. Third time this week on my work repo.",
  "author_id": "user_W2910",
  "rating": null,
  "version": "1.89.1",
  "url": null
}
```

- [ ] **Step 5: Create `data/raw/mock_community.json`**

10 items. Mix: 4 `reddit` (source_type: `social`), 3 `stack_overflow` (source_type: `external`), 3 `tech_community` (source_type: `external`). Distribution: 3 bugs, 4 feature requests, 3 UX issues. Reddit posts are informal/opinionated, SO posts are technical/precise, Tech Community posts are moderate.

Example:

```json
{
  "id": "reddit-8821",
  "source": "reddit",
  "source_type": "social",
  "timestamp": "2026-05-03T20:15:00Z",
  "raw_text": "Please add a way to pin specific terminals so they don't get buried when I open new ones. This would save me so much time daily.",
  "author_id": "reddit_user_41002",
  "rating": null,
  "version": null,
  "url": "https://reddit.com/r/vscode/comments/abc123"
}
```

- [ ] **Step 6: Create `data/raw/mock_reviews.json`**

6 items. Mix: 4 `g2_review`, 2 `capterra_review`. Source_type: `external`. All have ratings (1-5). Distribution: 2 bugs, 2 feature requests, 2 UX issues. Review-style text with "pros/cons" framing.

Example:

```json
{
  "id": "g2-301",
  "source": "g2_review",
  "source_type": "external",
  "timestamp": "2026-05-02T13:00:00Z",
  "raw_text": "Great editor overall (4/5 stars). Only real complaint is that the Git diff view is nearly unreadable in dark mode. The added/removed line colors are too similar.",
  "author_id": "g2_user_8810",
  "rating": 4,
  "version": null,
  "url": "https://www.g2.com/products/vscode/reviews/12345"
}
```

- [ ] **Step 7: Validate all JSON files**

Run:

```bash
for f in data/raw/*.json; do python3 -c "
import json, sys
with open('$f') as fh:
    items = json.load(fh)
    assert isinstance(items, list), 'Root must be array'
    for i, item in enumerate(items):
        for key in ['id','source','source_type','timestamp','raw_text','author_id']:
            assert key in item, f'Item {i} missing {key}'
    print(f'$f: {len(items)} items, all valid')
"; done
```

Expected: all 6 files pass, total of 57 items.

- [ ] **Step 8: Commit**

```bash
git add data/raw/github_issues.json data/raw/mock_surveys.json data/raw/mock_support_tickets.json data/raw/mock_in_app.json data/raw/mock_community.json data/raw/mock_reviews.json
git commit -m "feat: add mock feedback data for 6 sources (57 items)"
```

---

## Task 2: Update dashboard layout and add new components

The existing `dashboard/index.html` is a polished 800-line file with hardcoded data. This task makes three changes: adds a search bar, adds a product areas bar chart, and reorders sections to match the approved spec layout.

**Files:**
- Modify: `dashboard/index.html`

**Target layout order (top to bottom):**
1. Header (unchanged)
2. Stat cards — Row 1 (unchanged)
3. **Search bar — Row 2 (NEW)**
4. **Product areas bar chart + category donut — Row 3 (NEW chart + existing donut)**
5. **Clusters — Row 4 (moved up from after sources)**
6. **Recent Feedback feed — Row 5 (moved up, was at bottom)**
7. Trend chart — Row 6 (moved down, was in charts-row)
8. Source breakdown — Row 7 (moved down)
9. Footer (unchanged, but update text to remove "Auto-refreshed daily via GitHub Actions")

- [ ] **Step 1: Add search bar CSS**

Add this CSS block after the `.stat-trend` styles (around line 95) in the `<style>` tag:

```css
/* ─── SEARCH ─── */
.search-wrap {
  margin-bottom: 28px;
}
.search-input {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 16px 12px 40px;
  font-size: 13px;
  color: var(--text);
  font-family: inherit;
  outline: none;
  transition: border-color .2s, box-shadow .2s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23858585' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85zm-5.242.656a5 5 0 1 1 0-10 5 5 0 0 1 0 10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: 14px center;
}
.search-input:focus {
  border-color: var(--blue);
  box-shadow: 0 0 0 2px rgba(0,122,204,.25);
}
.search-input::placeholder { color: var(--dim); }

/* ─── PRODUCT AREAS ─── */
.area-bar-wrap { position: relative; }
.area-bar-row {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 6px; font-size: 11px;
}
.area-bar-label { width: 80px; text-align: right; color: var(--dim); flex-shrink: 0; }
.area-bar-track { flex: 1; background: var(--border); border-radius: 3px; height: 18px; overflow: hidden; }
.area-bar-fill { height: 100%; border-radius: 3px; transition: width .4s ease; }
.area-bar-count { width: 36px; font-size: 11px; color: var(--dim); font-variant-numeric: tabular-nums; }
```

- [ ] **Step 2: Add search bar HTML**

Add this HTML immediately after the stat cards `</div>` (after the closing `</div>` of `stat-grid`, around line 277):

```html
  <!-- ── SEARCH ── -->
  <div class="search-wrap">
    <input type="text" class="search-input" id="globalSearch" placeholder="Search across all feedback — e.g. 'sidebar', 'crash', 'copilot'" oninput="handleSearch(this.value)">
  </div>
```

- [ ] **Step 3: Update charts row — add product areas chart**

Replace the current `charts-row` div (the one containing the donut chart and trend chart) with:

```html
  <!-- ── CHARTS: Product Areas + Category Donut ── -->
  <div class="section-row">
    <span class="section-title">Where's the Heat</span>
    <span class="section-note">Feedback volume by product area and category</span>
  </div>
  <div class="charts-row">
    <div class="card">
      <div class="card-header">
        <div class="card-title">Top Product Areas</div>
        <div class="card-sub">By feedback volume · last 30 days</div>
      </div>
      <div class="area-bar-wrap" id="productAreaBars">
        <div class="area-bar-row"><span class="area-bar-label">extensions</span><div class="area-bar-track"><div class="area-bar-fill" style="width:100%;background:var(--red)"></div></div><span class="area-bar-count">312</span></div>
        <div class="area-bar-row"><span class="area-bar-label">copilot</span><div class="area-bar-track"><div class="area-bar-fill" style="width:92%;background:var(--red)"></div></div><span class="area-bar-count">287</span></div>
        <div class="area-bar-row"><span class="area-bar-label">sidebar</span><div class="area-bar-track"><div class="area-bar-fill" style="width:64%;background:var(--orange)"></div></div><span class="area-bar-count">201</span></div>
        <div class="area-bar-row"><span class="area-bar-label">terminal</span><div class="area-bar-track"><div class="area-bar-fill" style="width:60%;background:var(--orange)"></div></div><span class="area-bar-count">188</span></div>
        <div class="area-bar-row"><span class="area-bar-label">git</span><div class="area-bar-track"><div class="area-bar-fill" style="width:46%;background:var(--yellow)"></div></div><span class="area-bar-count">143</span></div>
        <div class="area-bar-row"><span class="area-bar-label">editor</span><div class="area-bar-track"><div class="area-bar-fill" style="width:43%;background:var(--yellow)"></div></div><span class="area-bar-count">134</span></div>
        <div class="area-bar-row"><span class="area-bar-label">settings</span><div class="area-bar-track"><div class="area-bar-fill" style="width:31%;background:var(--dim)"></div></div><span class="area-bar-count">98</span></div>
        <div class="area-bar-row"><span class="area-bar-label">debugging</span><div class="area-bar-track"><div class="area-bar-fill" style="width:24%;background:var(--dim)"></div></div><span class="area-bar-count">76</span></div>
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <div class="card-title">Category Breakdown</div>
        <div class="card-sub">All sources · last 30 days · click to filter</div>
      </div>
      <div class="chart-wrap" style="height:220px">
        <canvas id="donutChart"></canvas>
        <div class="donut-center">
          <div class="donut-center-num">2,847</div>
          <div class="donut-center-lbl">Total</div>
        </div>
      </div>
      <div class="chart-hint">↑ Click a segment to filter the whole dashboard</div>
    </div>
  </div>
```

Update `charts-row` CSS to swap column order (product areas on left, donut on right):

```css
.charts-row { display: grid; grid-template-columns: 1fr 300px; gap: 14px; margin-bottom: 28px; align-items: start; }
```

- [ ] **Step 4: Reorder HTML sections**

Move the sections in the `<main>` tag to this order:

1. Stat cards section (stays where it is)
2. Search bar (just added in Step 2)
3. Charts row — product areas + donut (just replaced in Step 3)
4. **Clusters section** — move this ABOVE the feed card (cut the `<!-- ── CLUSTERS ── -->` section-row + clusters div and paste here)
5. **Feed card** — move this right after clusters (cut the `<!-- ── FEED ── -->` card and paste here)
6. **Trend chart** — extract the trend chart from the old charts-row into its own card:

```html
  <!-- ── TREND ── -->
  <div class="section-row">
    <span class="section-title">Trajectory</span>
    <span class="section-note">Daily feedback volume · last 30 days</span>
  </div>
  <div class="card" style="margin-bottom:28px">
    <div class="chart-wrap" style="height:240px">
      <canvas id="trendChart"></canvas>
    </div>
  </div>
```

7. **Source breakdown** — stays last (before footer)

- [ ] **Step 5: Add search JavaScript**

Add this function to the `<script>` block, after the existing `syncFilter` function:

```javascript
function handleSearch(query) {
  const q = query.toLowerCase().trim();

  // Filter clusters
  document.querySelectorAll('.cluster').forEach(c => {
    if (!q) { c.classList.remove('dimmed'); c.style.display = ''; return; }
    const text = c.textContent.toLowerCase();
    const match = text.includes(q);
    c.classList.toggle('dimmed', !match);
  });

  // Filter feed items
  const items = document.querySelectorAll('.feed-item');
  let visible = 0;
  items.forEach(item => {
    if (!q) { item.style.display = 'grid'; visible++; return; }
    const text = item.textContent.toLowerCase();
    const match = text.includes(q);
    item.style.display = match ? 'grid' : 'none';
    if (match) visible++;
  });
  document.getElementById('feedCount').textContent = visible;
}
```

- [ ] **Step 6: Update footer text**

In the `<footer>`, replace:

```
Auto-refreshed daily via GitHub Actions ·
```

with:

```
Refreshed on demand via Claude AI ·
```

- [ ] **Step 7: Verify in browser**

Run:

```bash
open dashboard/index.html
```

Verify:
- Search bar appears between stat cards and charts
- Product areas horizontal bars render on the left, donut on the right
- Clusters appear above Recent Feedback
- Trend chart appears below Recent Feedback in its own row
- Source breakdown is last
- Typing "crash" in search filters clusters and feed to matching items
- Footer says "Refreshed on demand via Claude AI"

- [ ] **Step 8: Commit**

```bash
git add dashboard/index.html
git commit -m "feat: dashboard layout — add search bar, product areas chart, reorder sections"
```

---

## Task 3: Add data injection markers to dashboard

Convert the dashboard from hardcoded HTML to reading from a `LIVE_DATA` JavaScript object. This is what the Claude skill will update on each refresh.

**Files:**
- Modify: `dashboard/index.html`

- [ ] **Step 1: Add LIVE_DATA object with markers**

At the very top of the `<script>` block (before the `CLUSTERS` object), add:

```javascript
/* DATA_START */
const LIVE_DATA = {
  generated_at: "2026-05-05T09:00:00Z",
  totals: { bug: 1203, feature_request: 1081, ux_issue: 563 },
  by_source: {
    github_issues: 1142, in_app_widget: 487, nps_survey: 374,
    reddit: 268, support_ticket: 211, tech_community: 163,
    g2_review: 128, stack_overflow: 74
  },
  by_product_area: {
    extensions: 312, copilot: 287, sidebar: 201, terminal: 188,
    git: 143, editor: 134, settings: 98, debugging: 76
  },
  clusters: [
    {
      title: "Extension host crashes on large workspaces",
      category: "bug",
      item_count: 127,
      sources: "GitHub Issues + In-App Widget",
      growth: "+43%",
      urgency: "critical",
      signal: "spike detected",
      sample_texts: [
        { text: "Extension host keeps crashing when I open my monorepo with 40+ packages.", meta: "GitHub Issues #12847 · 2h ago" },
        { text: "Crashed again mid-session. Third time this week on my work repo.", meta: "In-App Widget · 1h ago" },
        { text: "Extension host process died. My workspace has ~60 packages.", meta: "GitHub Issues #12801 · 1d ago" }
      ]
    },
    {
      title: "Copilot inline suggestions lag on slow connections",
      category: "bug",
      item_count: 98,
      sources: "GitHub Issues + Support Tickets",
      growth: "stable",
      urgency: "medium",
      signal: "2 weeks open",
      sample_texts: [
        { text: "Copilot suggestions take 3-4 seconds on my home internet.", meta: "Support Ticket #4421 · 12h ago" },
        { text: "Inline completions are unusable on any connection under 50Mbps.", meta: "GitHub Issues #12799 · 2d ago" }
      ]
    },
    {
      title: "Add multi-cursor support to Find & Replace",
      category: "feature_request",
      item_count: 91,
      sources: "GitHub Issues + NPS Survey",
      growth: "+12%",
      urgency: "low",
      signal: "roadmap candidate",
      sample_texts: [
        { text: "Would love multi-cursor in Find & Replace. Currently I run multiple searches.", meta: "NPS Survey · 3h ago" },
        { text: "Sublime Text has this. Please add it.", meta: "GitHub Issues #12756 · 4d ago" }
      ]
    },
    {
      title: "Sidebar panels can't be resized independently",
      category: "ux_issue",
      item_count: 74,
      sources: "Reddit + In-App Widget + G2",
      growth: "+28%",
      urgency: "medium",
      signal: "layout issue",
      sample_texts: [
        { text: "Sidebar panels all resize together. I want independent sizing.", meta: "GitHub Issues #12831 · 8h ago" },
        { text: "The lack of independent panel resizing is driving me crazy.", meta: "Reddit r/vscode · 1d ago" }
      ]
    },
    {
      title: "Terminal font rendering broken on HiDPI displays",
      category: "bug",
      item_count: 68,
      sources: "GitHub Issues + Tech Community",
      growth: "stable",
      urgency: "medium",
      signal: "platform-specific",
      sample_texts: [
        { text: "Terminal font is blurry on my 4K display. Editor fonts look fine.", meta: "GitHub Issues #12788 · 3d ago" },
        { text: "Terminal font rendering broken at 200% scaling on Windows 11.", meta: "Stack Overflow · 2d ago" }
      ]
    },
    {
      title: "Git diff view hard to read in dark theme",
      category: "ux_issue",
      item_count: 52,
      sources: "GitHub Issues + G2",
      growth: "new",
      urgency: "low",
      signal: "watch this week",
      sample_texts: [
        { text: "The diff view contrast is too low in dark mode.", meta: "GitHub Issues #12841 · 1d ago" },
        { text: "Git diff is nearly unreadable in dark mode. Colors are too similar.", meta: "G2 Review · 2d ago" }
      ]
    }
  ],
  recent: [
    { text: "Extension host crashed again mid-session. Third time this week on my work repo.", source: "In-App Widget", time: "1 hour ago", source_type: "internal", category: "bug", urgency: "critical", icon: "📱" },
    { text: "Extension host keeps crashing when I open my monorepo with 40+ packages. Happens every time after about 5 minutes.", source: "GitHub Issues #12847", time: "2 hours ago", source_type: "external", category: "bug", urgency: "critical", icon: "🐙" },
    { text: "NPS Score: 8/10. Would love multi-cursor support in Find and Replace. Currently I have to run multiple searches which is slow.", source: "NPS Survey · User #U-4821", time: "3 hours ago", source_type: "survey", category: "feature_request", urgency: "medium", icon: "📊" },
    { text: "The sidebar panels can't be resized independently — they all move together.", source: "GitHub Issues #12831", time: "8 hours ago", source_type: "external", category: "ux_issue", urgency: "medium", icon: "🐙" },
    { text: "Copilot suggestions have a noticeable 3-4 second delay on my home internet.", source: "Support Ticket #4421", time: "12 hours ago", source_type: "internal", category: "bug", urgency: "medium", icon: "🎫" },
    { text: "Please add a way to pin specific terminals so they don't get buried.", source: "Reddit r/vscode", time: "Yesterday", source_type: "social", category: "feature_request", urgency: "low", icon: "💬" },
    { text: "Settings search ranking feels off. Searching 'font size' shows wrong result first.", source: "Microsoft Tech Community", time: "Yesterday", source_type: "external", category: "ux_issue", urgency: "low", icon: "🏢" },
    { text: "Great editor overall (4/5 stars). Git diff view is nearly unreadable in dark mode.", source: "G2 Review · ★★★★☆", time: "2 days ago", source_type: "external", category: "ux_issue", urgency: "low", icon: "⭐" },
    { text: "Terminal font rendering is completely broken at 200% display scaling on Windows 11.", source: "Stack Overflow", time: "2 days ago", source_type: "external", category: "bug", urgency: "medium", icon: "📚" },
    { text: "CSAT: 3/5. Wish VS Code had a built-in HTTP client like JetBrains.", source: "Post-Support Email Survey", time: "3 days ago", source_type: "survey", category: "feature_request", urgency: "low", icon: "📧" },
    { text: "Love the editor but really need AI-powered rename across files.", source: "In-App Widget", time: "3 days ago", source_type: "internal", category: "feature_request", urgency: "low", icon: "📱" },
    { text: "After updating to v1.89.1, Jupyter notebook integration stopped working.", source: "Microsoft Tech Community", time: "4 days ago", source_type: "external", category: "bug", urgency: "high", icon: "🏢" }
  ]
};
/* DATA_END */
```

- [ ] **Step 2: Replace hardcoded stat card values with LIVE_DATA rendering**

Replace the hardcoded stat values in the stat card HTML with `id` attributes, then add a render function that populates them from LIVE_DATA:

Update the stat cards HTML: give each `.stat-value` an id:
- Total card: `id="statTotal"`
- Bug card: `id="statBug"`
- Feature card: `id="statFeature"`
- UX card: `id="statUx"`

Add this function at the end of the `<script>` block:

```javascript
function renderFromData() {
  const d = LIVE_DATA;
  const total = d.totals.bug + d.totals.feature_request + d.totals.ux_issue;

  // Stat cards
  document.getElementById('statTotal').textContent = total.toLocaleString();
  document.getElementById('statBug').textContent = d.totals.bug.toLocaleString();
  document.getElementById('statFeature').textContent = d.totals.feature_request.toLocaleString();
  document.getElementById('statUx').textContent = d.totals.ux_issue.toLocaleString();
  document.querySelector('.donut-center-num').textContent = total.toLocaleString();

  // Timestamp
  if (d.generated_at) {
    const ts = new Date(d.generated_at);
    document.querySelector('.header-ts').textContent =
      'Last refreshed: ' + ts.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
      ' · ' + ts.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC', timeZoneName: 'short' });
  }

  // Product area bars
  const areaContainer = document.getElementById('productAreaBars');
  if (areaContainer && d.by_product_area) {
    const areas = Object.entries(d.by_product_area).sort((a, b) => b[1] - a[1]);
    const maxVal = areas[0]?.[1] || 1;
    areaContainer.innerHTML = areas.map(([area, count]) => {
      const pct = Math.round((count / maxVal) * 100);
      const color = pct > 80 ? 'var(--red)' : pct > 50 ? 'var(--orange)' : pct > 30 ? 'var(--yellow)' : 'var(--dim)';
      return `<div class="area-bar-row"><span class="area-bar-label">${area}</span><div class="area-bar-track"><div class="area-bar-fill" style="width:${pct}%;background:${color}"></div></div><span class="area-bar-count">${count}</span></div>`;
    }).join('');
  }

  // Source chips
  const sourceGrid = document.querySelector('.source-grid');
  if (sourceGrid && d.by_source) {
    const sourceIcons = { github_issues:'🐙', in_app_widget:'📱', nps_survey:'📊', reddit:'💬', support_ticket:'🎫', tech_community:'🏢', g2_review:'⭐', stack_overflow:'📚', csat_survey:'📊', email_survey:'📧', capterra_review:'⭐' };
    const sourceNames = { github_issues:'GitHub Issues', in_app_widget:'In-App Widget', nps_survey:'NPS / CSAT Survey', reddit:'Reddit r/vscode', support_ticket:'Support Tickets', tech_community:'Tech Community', g2_review:'G2 / Capterra', stack_overflow:'Stack Overflow', csat_survey:'CSAT Survey', email_survey:'Email Survey', capterra_review:'Capterra' };
    const sourceTypes = { github_issues:'external', in_app_widget:'internal', nps_survey:'survey', reddit:'social', support_ticket:'internal', tech_community:'external', g2_review:'external', stack_overflow:'external', csat_survey:'survey', email_survey:'survey', capterra_review:'external' };
    const tagClasses = { internal:'tag-internal', external:'tag-external', social:'tag-social', survey:'tag-survey' };

    const sorted = Object.entries(d.by_source).sort((a, b) => b[1] - a[1]);
    sourceGrid.innerHTML = sorted.map(([src, count]) => {
      const st = sourceTypes[src] || 'external';
      return `<div class="source-chip"><span class="source-icon-sm">${sourceIcons[src]||'📄'}</span><div class="source-info"><div class="source-name">${sourceNames[src]||src}</div><div class="source-count">${count.toLocaleString()} items</div></div><span class="source-type-tag ${tagClasses[st]||'tag-external'}">${st}</span></div>`;
    }).join('');
  }

  // Clusters
  const clustersContainer = document.querySelector('.clusters');
  if (clustersContainer && d.clusters) {
    const catBadge = { bug: ['Bug','b-bug'], feature_request: ['Feature','b-feature'], ux_issue: ['UX','b-ux'] };
    const urgColors = { critical:'var(--red)', high:'var(--red)', medium:'var(--dim)', low:'var(--green)' };
    const maxCount = Math.max(...d.clusters.map(c => c.item_count));

    clustersContainer.innerHTML = d.clusters.map((c, i) => {
      const [badgeLabel, badgeClass] = catBadge[c.category] || ['Other','b-bug'];
      const barPct = Math.round((c.item_count / maxCount) * 100);
      const barColor = c.category === 'bug' ? 'var(--red)' : c.category === 'feature_request' ? 'var(--green)' : 'var(--orange)';
      const sigColor = c.urgency === 'critical' ? 'var(--red)' : c.urgency === 'high' ? 'var(--red)' : c.growth === 'new' ? 'var(--yellow)' : c.category === 'ux_issue' ? 'var(--orange)' : 'var(--dim)';
      const urgLabel = c.urgency === 'critical' ? '⚠ Critical' : c.urgency === 'high' ? 'High urgency' : c.urgency === 'medium' ? 'Medium urgency' : 'High demand';
      const catFilter = c.category === 'feature_request' ? 'feature' : c.category === 'ux_issue' ? 'ux' : 'bug';

      return `<div class="cluster" data-cat="${catFilter}" onclick="openClusterByIndex(${i})">
        <div class="cluster-top"><span class="cluster-name">${c.title}</span><span class="badge ${badgeClass}">${badgeLabel}</span></div>
        <div class="cluster-meta">${c.item_count} reports · ${c.sources} · ${c.growth === 'stable' ? 'stable' : c.growth === 'new' ? 'new' : c.growth + ' this week'}</div>
        <div class="bar-bg"><div class="bar" style="width:${barPct}%;background:${barColor}"></div></div>
        <div class="cluster-signal" style="color:${sigColor}">${urgLabel} · ${c.signal}</div>
      </div>`;
    }).join('');
  }

  // Recent feed
  const feedList = document.getElementById('feed');
  if (feedList && d.recent) {
    const catColors = { bug: 'rgba(241,76,76,.15)', feature_request: 'rgba(78,201,148,.15)', ux_issue: 'rgba(206,145,120,.15)' };
    const catTextColors = { bug: 'var(--red)', feature_request: 'var(--green)', ux_issue: 'var(--orange)' };
    const catLabels = { bug: 'Bug', feature_request: 'Feature Request', ux_issue: 'UX Issue' };
    const tagClasses = { internal:'tag-internal', external:'tag-external', social:'tag-social', survey:'tag-survey' };
    const urgDot = { critical:'u-high', high:'u-high', medium:'u-med', low:'u-low' };
    const catFilter = { bug:'bug', feature_request:'feature', ux_issue:'ux' };

    feedList.innerHTML = d.recent.map(item => {
      const urgLabel = item.urgency !== 'low' ? ' · ' + item.urgency.charAt(0).toUpperCase() + item.urgency.slice(1) : '';
      return `<div class="feed-item" data-cat="${catFilter[item.category] || item.category}">
        <div class="src-icon">${item.icon}</div>
        <div>
          <div class="feed-text">"${item.text}"</div>
          <div class="feed-meta">
            <span>${item.source}</span><span>${item.time}</span>
            <span class="feed-source-type ${tagClasses[item.source_type]||'tag-external'}">${item.source_type}</span>
            <span class="feed-cat-tag" style="background:${catColors[item.category]};color:${catTextColors[item.category]}">${catLabels[item.category]}${urgLabel}</span>
          </div>
        </div>
        <div class="u-dot ${urgDot[item.urgency]||'u-low'}"></div>
      </div>`;
    }).join('');
    document.getElementById('feedCount').textContent = d.recent.length;
  }

  // Update donut chart data
  if (typeof donutChart !== 'undefined') {
    donutChart.data.datasets[0].data = [d.totals.bug, d.totals.feature_request, d.totals.ux_issue];
    donutChart.update();
  }
}
```

- [ ] **Step 3: Replace hardcoded cluster/feed HTML with empty containers**

Replace the hardcoded cluster cards inside `<div class="clusters">` with just an empty container — the `renderFromData()` function will populate it:

```html
<div class="clusters" id="clustersContainer"></div>
```

Replace the hardcoded feed items inside `<div class="feed-list" id="feed">` with nothing — `renderFromData()` populates it:

```html
<div class="feed-list" id="feed"></div>
```

Replace the hardcoded source chips inside `<div class="source-grid">` with nothing — `renderFromData()` populates it:

```html
<div class="source-grid" id="sourceGrid"></div>
```

- [ ] **Step 4: Add cluster modal function for data-driven clusters**

Replace the old `openCluster(key)` function with:

```javascript
function openClusterByIndex(idx) {
  const c = LIVE_DATA.clusters[idx];
  if (!c) return;
  const catBadge = { bug: ['Bug','b-bug'], feature_request: ['Feature','b-feature'], ux_issue: ['UX','b-ux'] };
  const [badgeLabel, badgeClass] = catBadge[c.category] || ['Other','b-bug'];

  document.getElementById('modalTitle').textContent = c.title;
  document.getElementById('modalBody').innerHTML = `
    <div>
      <div class="modal-stat-row"><span class="modal-stat-label">Category</span><span class="modal-stat-value"><span class="badge ${badgeClass}">${badgeLabel}</span></span></div>
      <div class="modal-stat-row"><span class="modal-stat-label">Total Reports</span><span class="modal-stat-value">${c.item_count}</span></div>
      <div class="modal-stat-row"><span class="modal-stat-label">Trend</span><span class="modal-stat-value">${c.growth}</span></div>
      <div class="modal-stat-row"><span class="modal-stat-label">Urgency</span><span class="modal-stat-value">${c.urgency}</span></div>
      <div class="modal-stat-row"><span class="modal-stat-label">Sources</span><span class="modal-stat-value">${c.sources}</span></div>
    </div>
    <div class="modal-items-title">Sample Reports</div>
    ${(c.sample_texts || []).map(s => `<div class="modal-item">"${s.text}"<div class="modal-item-meta">${s.meta}</div></div>`).join('')}
  `;
  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}
```

Remove the old `CLUSTERS` object and the old `openCluster(key)` function entirely.

- [ ] **Step 5: Call renderFromData on page load**

Add this line at the very end of the `<script>` block:

```javascript
renderFromData();
```

- [ ] **Step 6: Verify in browser**

Run:

```bash
open dashboard/index.html
```

Verify:
- All stat cards show correct values from LIVE_DATA
- Product areas chart renders with correct bars
- Donut chart renders with correct proportions
- All 6 clusters render with correct data
- Clicking a cluster opens the modal with sample texts
- All 12 feed items render with correct category tags
- Source chips render with correct counts
- Search still filters clusters and feed items
- Stat card clicks still filter feed items

- [ ] **Step 7: Commit**

```bash
git add dashboard/index.html
git commit -m "feat: dashboard renders from LIVE_DATA with injection markers"
```

---

## Task 4: Create fetch_feedback.py

A small Python script that fetches real VS Code GitHub issues and writes them to `data/raw/github_issues.json`. Stdlib only — no pip dependencies.

**Files:**
- Create: `scripts/fetch_feedback.py`

- [ ] **Step 1: Write the script**

```python
"""
Fetches VS Code GitHub Issues (public API, no auth needed — 60 req/hr limit)
and writes them to data/raw/github_issues.json.

Usage: python3 scripts/fetch_feedback.py
"""

import json
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent.parent
RAW = BASE / "data" / "raw"


def fetch_github_issues(
    repo: str = "microsoft/vscode", per_page: int = 50
) -> list[dict]:
    url = (
        f"https://api.github.com/repos/{repo}/issues"
        f"?state=open&per_page={per_page}&sort=updated"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CustomerFeedbackBot/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            issues = json.loads(resp.read())
    except Exception as e:
        print(f"GitHub API error: {e} — keeping existing data")
        return []

    items = []
    for issue in issues:
        if issue.get("pull_request"):
            continue
        body = (issue.get("body") or "").strip()
        if not body or len(body) < 20:
            continue
        items.append(
            {
                "id": f"gh-{issue['number']}",
                "source": "github_issues",
                "source_type": "external",
                "timestamp": issue["updated_at"],
                "raw_text": f"{issue['title']}. {body[:500]}".strip(),
                "author_id": f"gh_user_{hash(issue['user']['login']) % 99999}",
                "rating": None,
                "version": None,
                "url": issue["html_url"],
            }
        )

    return items


def run():
    RAW.mkdir(parents=True, exist_ok=True)
    items = fetch_github_issues()
    if not items:
        print("No items fetched — github_issues.json unchanged")
        return

    out = RAW / "github_issues.json"
    with open(out, "w") as f:
        json.dump(items, f, indent=2)
    print(f"Wrote {len(items)} GitHub issues to {out}")


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Run the script**

Run:

```bash
python3 scripts/fetch_feedback.py
```

Expected: prints "Wrote NN GitHub issues to data/raw/github_issues.json" (exact count depends on GitHub API response).

- [ ] **Step 3: Validate the output**

Run:

```bash
python3 -c "
import json
with open('data/raw/github_issues.json') as f:
    items = json.load(f)
    print(f'{len(items)} items')
    for key in ['id','source','source_type','timestamp','raw_text']:
        assert key in items[0], f'Missing {key}'
    print('Schema OK')
    print(f'Sample: {items[0][\"id\"]} — {items[0][\"raw_text\"][:80]}...')
"
```

Expected: item count, "Schema OK", and a sample item preview.

- [ ] **Step 4: Commit**

```bash
git add scripts/fetch_feedback.py
git commit -m "feat: add GitHub issues fetcher script"
```

---

## Task 5: Create the Claude skill and update CLAUDE.md

This is the core of the project — the skill file that Claude follows when the user says "Refresh the feedback page."

**Files:**
- Create: `.claude/skills/refresh-feedback.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/refresh-feedback.md`:

```markdown
---
name: refresh-feedback
description: Runs the VS Code customer feedback classification pipeline. Reads raw feedback, classifies new items, updates the dashboard.
---

## Overview

You are running the Customer Feedback Intelligence pipeline for VS Code.

**Project location:** /Users/shayalpatel/Documents/Claude Projects/Customer Feedback Loop

## Step 1: Identify new items

Read `data/processed/feedback_classified.json`. If it does not exist, treat all items as new.

Extract the set of all `id` values from the classified file.

Then read every JSON file in `data/raw/`. Collect all items whose `id` is NOT in the classified set. These are the new items to classify.

If there are zero new items, skip to Step 4.

## Step 2: Classify new items

For each new item, determine:

- **category:** `bug` | `feature_request` | `ux_issue` | `praise`
  - bug: product behaves unexpectedly, crashes, errors, regressions
  - feature_request: user wants something that doesn't exist yet
  - ux_issue: product works but is confusing, frustrating, or inefficient
  - praise: positive feedback

- **sub_category:** a short label for the specific type (e.g., crash, performance, new_feature, navigation, visual_design)

- **sentiment:** `positive` | `neutral` | `negative`

- **urgency:** `low` | `medium` | `high` | `critical`
  - critical: data loss, completely unusable, affects every session
  - high: blocking work, affects many users
  - medium: happens regularly, meaningful friction
  - low: minor, occasional, cosmetic

- **product_area:** terminal | editor | extensions | git | copilot | settings | sidebar | debugging | search | notebooks | remote | themes | workspaces | performance | null

- **one_line_summary:** a 10-word plain-English description

Consider context, tone, and intent — not just keywords. "I have to manually do X every time" is a feature_request. A 1-star review that says "great UI but crashes constantly" is primarily a bug.

Process in batches of approximately 100 items. After each batch, append the classified items to `data/processed/feedback_classified.json` before continuing to the next batch. This ensures no work is lost if the session is interrupted.

Each classified item should include all original fields from the raw item plus the classification fields and a `classified_at` timestamp (ISO 8601).

## Step 3: Identify clusters

Read the full `data/processed/feedback_classified.json` (including items from previous runs).

Group items that describe the same underlying issue. A cluster is 3+ items about the same problem. Use your judgment to identify clusters — look for similar descriptions, same product area, same type of complaint.

For each cluster, record:
- title: a clear one-line name for the issue
- category: the dominant category
- item_count: how many items belong
- sources: which data sources contributed
- growth: estimate if growing, stable, or new (compare timestamps)
- urgency: the highest urgency among members
- signal: a short status phrase (e.g., "spike detected", "2 weeks open", "watch this week")
- sample_texts: 2-3 representative quotes with source/time metadata

Write clusters to `data/processed/clusters.json`, sorted by item_count descending.

## Step 4: Rebuild summary

Read the full `data/processed/feedback_classified.json`.

Compute:
- totals by category (bug, feature_request, ux_issue)
- counts by source
- counts by product_area
- list of critical items
- top clusters (from clusters.json)

Write to `data/processed/feedback_summary.json`:

```json
{
  "generated_at": "ISO 8601 timestamp",
  "totals": { "bug": N, "feature_request": N, "ux_issue": N },
  "by_source": { "github_issues": N, ... },
  "by_product_area": { "extensions": N, ... },
  "critical_items": [ ... ],
  "top_clusters": [ ... ]
}
```

## Step 5: Update dashboard

Read `dashboard/index.html`. Find the text between `/* DATA_START */` and `/* DATA_END */`.

Replace that entire block with a new `LIVE_DATA` object built from the summary, clusters, and recent classified items. The structure must match:

```javascript
/* DATA_START */
const LIVE_DATA = {
  generated_at: "...",
  totals: { bug: N, feature_request: N, ux_issue: N },
  by_source: { ... },
  by_product_area: { ... },
  clusters: [ { title, category, item_count, sources, growth, urgency, signal, sample_texts: [{text, meta}] } ],
  recent: [ { text, source, time, source_type, category, urgency, icon } ]  // 12 most recent items
};
/* DATA_END */
```

For the `recent` array, use the 12 most recently timestamped items. Assign icons based on source:
- github_issues: 🐙, in_app_widget: 📱, nps_survey/csat_survey: 📊, reddit: 💬
- support_ticket: 🎫, tech_community: 🏢, g2_review/capterra_review: ⭐
- stack_overflow: 📚, email_survey: 📧

Write the updated `dashboard/index.html`.

## Step 6: Commit and push

Run:

```bash
git add data/processed/ dashboard/index.html
git commit -m "chore: feedback refresh $(date '+%Y-%m-%d %H:%M')"
git push
```

If git push fails, report the error but continue to Step 7.

## Step 7: Report

Tell the user:
1. How many new items were classified (and how many total are now in the system)
2. Category breakdown (bugs / features / UX)
3. Top 3 most urgent clusters with item count
4. Any notable changes since last run
5. Remind them: "You can now ask me questions about the feedback — e.g., 'Are there any sidebar bugs?' or 'What are users asking for in the terminal?'"
```

- [ ] **Step 2: Update CLAUDE.md**

Replace the entire contents of `CLAUDE.md` with:

```markdown
Microsoft wants to optimize products based on market feedback.

## Feedback Loop Skill

When the user says something similar to "Refresh the feedback page", "update the feedback",
"scan feedback", or "run the feedback pipeline", run the skill at:
`.claude/skills/refresh-feedback.md`

After the skill runs, you have full context from data/processed/feedback_summary.json
and data/processed/feedback_classified.json to answer follow-up questions like:
- "Are there any bugs with the sidebar?"
- "What are the top feature requests?"
- "Is there anything critical right now?"
- "What do users say about Copilot?"
- "Show me all UX issues"

To answer these, read data/processed/feedback_summary.json first, then
data/processed/feedback_classified.json if you need individual items.
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/refresh-feedback.md CLAUDE.md
git commit -m "feat: add feedback classification skill and trigger"
```

---

## Task 6: End-to-end verification

Verify the entire system works from trigger to dashboard to Q&A.

**Files:** None — this is a testing task.

- [ ] **Step 1: Run the feedback skill**

In Claude Code, say: "Refresh the feedback page"

Verify:
- Claude acknowledges and starts the skill
- Claude reads all raw files
- Claude classifies items and writes to `data/processed/feedback_classified.json`
- Claude creates `data/processed/clusters.json`
- Claude creates `data/processed/feedback_summary.json`
- Claude updates `dashboard/index.html` (LIVE_DATA block changes)
- Claude commits (push may fail if GitHub repo not set up — that's OK for local verification)
- Claude reports category breakdown and top clusters

- [ ] **Step 2: Verify dashboard**

Run:

```bash
open dashboard/index.html
```

Verify:
- Stat cards show real counts from classified data
- Product areas bar chart reflects actual product area distribution
- Donut chart shows correct bug/feature/UX proportions
- Cluster cards show real clusters from the data
- Clicking a cluster opens modal with sample texts
- Feed shows recent items with correct category tags
- Search filters clusters and feed
- Stat card clicks filter the feed
- Timestamp in header reflects the latest classification run

- [ ] **Step 3: Test follow-up Q&A**

Ask Claude: "Are there any sidebar bugs?"

Verify: Claude reads `feedback_summary.json` and/or `feedback_classified.json` and gives a specific, data-grounded answer naming actual items.

- [ ] **Step 4: Test incremental classification**

Add a new item to any raw file (e.g., append to `data/raw/mock_in_app.json`):

```json
{
  "id": "iaw-9999",
  "source": "in_app_widget",
  "source_type": "internal",
  "timestamp": "2026-05-07T15:00:00Z",
  "raw_text": "The terminal cursor blinks way too fast. It's distracting and gives me a headache.",
  "author_id": "user_TEST1",
  "rating": null,
  "version": "1.89.1",
  "url": null
}
```

Say: "Refresh the feedback page"

Verify: Claude reports only 1 new item classified (not the entire dataset re-classified). Check `feedback_classified.json` — item `iaw-9999` should appear with `classified_at` set to the current run time, while all other items retain their original `classified_at` timestamps.

- [ ] **Step 5: Verify GitHub Pages (if repo is set up)**

If the GitHub repo exists and git push succeeded:

Visit: https://shayalpatel.github.io/CustomerFeedback

Verify the dashboard renders with the same data as the local version.

---

## Self-Review Checklist

- [x] **Spec coverage:** Every section of the design spec (Sections 1-8) maps to a task. Mock data → Task 1. Dashboard layout/components → Tasks 2-3. Fetch script → Task 4. Skill + CLAUDE.md → Task 5. E2E verification → Task 6. Success criteria → Task 6 steps.
- [x] **Placeholder scan:** No TBDs, TODOs, or "implement later" anywhere. All code blocks are complete.
- [x] **Type consistency:** `LIVE_DATA` structure in Task 3 matches what the skill writes in Task 5. Raw item schema in Task 1 matches what the skill reads in Task 5. Category values (`bug`, `feature_request`, `ux_issue`) are consistent across dashboard rendering (Task 3), skill classification (Task 5), and filter logic (Task 2).
- [x] **Missing pieces:** The design spec mentions `data/processed/clusters.json` as a separate file — the skill writes it in Step 3. Dashboard footer update is in Task 2 Step 6. Git credential setup for push is not in scope (noted as "may fail" in Task 6).
