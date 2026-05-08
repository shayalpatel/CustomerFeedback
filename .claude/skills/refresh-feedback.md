---
name: refresh-feedback
description: Runs the VS Code customer feedback classification pipeline. Reads raw feedback, classifies new items, updates the dashboard.
---

## Overview

You are running the Customer Feedback Intelligence pipeline for VS Code.

All file paths in this skill are relative to the project root (where CLAUDE.md lives).

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

Note: `praise` items should be classified as such but excluded from category totals in Step 4 and not clustered in Step 3.

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

Process in batches of approximately 100 items. After each batch: read the existing `data/processed/feedback_classified.json` (as an array, or start with an empty array if the file does not exist), add the newly classified items to the array, and write the full array back to the file. This read-merge-write pattern ensures prior batches are preserved.

Each classified item should include all original fields from the raw item plus the classification fields and a `classified_at` timestamp (ISO 8601).

## Step 3: Identify clusters

Read the full `data/processed/feedback_classified.json` (including items from previous runs).

Group items that describe the same underlying issue. A cluster is 3+ items about the same problem. Use your judgment to identify clusters — look for similar descriptions, same product area, same type of complaint.

For each cluster, record:
- title: a clear one-line name for the issue
- category: the dominant category
- item_count: how many items belong
- sources: which data sources contributed
- growth: estimate if growing, stable, or new (compare timestamps). Use this rule: if all items appeared within the last 7 days, mark as `new`; if items from the last 7 days outnumber items from 8-30 days ago, mark as `growing`; otherwise mark as `stable`. Include the percentage change if growing (e.g., '+28%').
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
- top clusters (from clusters.json — if `data/processed/clusters.json` does not exist, use an empty array for `top_clusters`)

Write to `data/processed/feedback_summary.json`:

```json
{
  "generated_at": "ISO 8601 timestamp",
  "totals": { "bug": N, "feature_request": N, "ux_issue": N },  // totals counts only bug, feature_request, ux_issue — exclude praise items
  "by_source": { "github_issues": N, ... },
  "by_product_area": { "extensions": N, ... },
  "critical_items": [ ... ],
  "top_clusters": [ ... ]
}
```

## Step 5: Update dashboard

Read `index.html`. Find the text between `/* DATA_START */` and `/* DATA_END */`.

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

Write the updated `index.html`.

## Step 6: Commit and push

Run:

```bash
git add data/processed/ index.html
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
