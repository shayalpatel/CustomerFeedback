# Customer Feedback Loop — Implementation Plan

> **Product:** Visual Studio Code (microsoft/vscode)
> **Repo:** github.com/shayalpatel/CustomerFeedback
> **Live URL:** https://shayalpatel.github.io/CustomerFeedback
> **Status:** Pre-implementation — do not build until this plan is approved

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [How the Claude Code Skill Works](#3-how-the-claude-code-skill-works)
4. [Classification Strategy — Two Layers](#4-classification-strategy--two-layers)
5. [Phase 0 — Repository & GitHub Pages](#phase-0--repository--github-pages)
6. [Phase 1 — Data Foundation](#phase-1--data-foundation)
7. [Phase 2 — Smart Classification Script](#phase-2--smart-classification-script)
8. [Phase 3 — Claude Code Skill](#phase-3--claude-code-skill)
9. [Phase 4 — Pipeline Scripts](#phase-4--pipeline-scripts)
10. [Phase 5 — GitHub Actions Automation](#phase-5--github-actions-automation)
11. [Master Todo List](#master-todo-list)

---

## 1. System Overview

This project builds a complete AI-powered customer feedback intelligence system for VS Code. It:

- **Collects** feedback from 8+ sources (GitHub Issues, in-app widget, NPS/CSAT surveys, Reddit, Stack Overflow, Microsoft Tech Community, G2 reviews, support tickets)
- **Classifies** each item into Bug / Feature Request / UX Issue using a two-layer AI system
- **Clusters** similar items so 50 complaints about "crashing on large workspaces" become one actionable signal
- **Displays** everything in a live dashboard at a public GitHub Pages URL
- **Auto-refreshes** daily via GitHub Actions with no manual effort
- **Responds** to natural language questions via a Claude Code conversational skill

All infrastructure is **free**. The only cost is the Claude Code subscription you already have.

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (8 channels)                        │
│                                                                     │
│  INTERNAL                    EXTERNAL                  SURVEY       │
│  ┌──────────────┐           ┌──────────────┐          ┌──────────┐  │
│  │ In-App Widget│           │ GitHub Issues│          │ NPS/CSAT │  │
│  │ Support Tix  │           │ Reddit       │          │ Email    │  │
│  └──────┬───────┘           │ Tech Comm.   │          └────┬─────┘  │
│         │                   │ Stack Ovflow │               │        │
│         │                   │ G2 Reviews   │               │        │
│         └───────────────────┴──────────────┴───────────────┘        │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ data/raw/*.json
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLASSIFICATION LAYER                             │
│                                                                     │
│  ┌─────────────────────────┐    ┌─────────────────────────────────┐ │
│  │  SmartFeedbackClassifier│    │   Claude Code Skill             │ │
│  │  (scripts/classify.py)  │    │   (.claude/skills/refresh.md)   │ │
│  │                         │    │                                 │ │
│  │  • Multi-signal scoring │    │  • Full Claude intelligence     │ │
│  │  • Bayesian priors      │    │  • Reads raw data               │ │
│  │  • Negation detection   │    │  • Classifies with reasoning    │ │
│  │  • TF-IDF clustering    │    │  • Writes processed/ files      │ │
│  │  • ~85% accuracy        │    │  • ~95%+ accuracy               │ │
│  │  • Used by: GH Actions  │    │  • Used by: conversational      │ │
│  └──────────┬──────────────┘    └──────────────┬──────────────────┘ │
│             └──────────────────┬───────────────┘                    │
└──────────────────────────────┬─┴────────────────────────────────────┘
                               │ data/processed/*.json
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                                     │
│                                                                     │
│  ┌──────────────────────┐         ┌──────────────────────────────┐  │
│  │  dashboard/index.html│         │  Claude Q&A Context          │  │
│  │                      │         │  (feedback_summary.json)     │  │
│  │  • Stat cards        │         │                              │  │
│  │  • Category donut    │         │  "Are there sidebar bugs?"   │  │
│  │  • 30-day trend      │         │  → Claude reads summary.json │  │
│  │  • Source breakdown  │         │  → Answers from data         │  │
│  │  • Issue clusters    │         │                              │  │
│  │  • Filterable feed   │         └──────────────────────────────┘  │
│  └──────────┬───────────┘                                           │
└─────────────┼───────────────────────────────────────────────────────┘
              │ git push
              ▼
  https://shayalpatel.github.io/CustomerFeedback
```

---

## 3. How the Claude Code Skill Works

> This section explains the skill mechanically — what it is, how it executes, and why it costs nothing.

### What a skill file is

A Claude Code skill is a **Markdown file** stored at `.claude/skills/refresh-feedback.md`. It contains natural language instructions written in a specific format that Claude Code reads and executes step-by-step using its built-in tools (`Read`, `Write`, `Bash`).

It is **not** a compiled script. It is **not** a slash command. It is a recipe that Claude interprets at runtime using its own intelligence.

### How the trigger connects to the skill

When you type something like `"Refresh the feedback page"` in Claude Code:

1. Claude Code automatically loads `CLAUDE.md` into every conversation
2. `CLAUDE.md` defines: *"When the user says something similar to 'Refresh the Feedback page', run the skill at `.claude/skills/refresh-feedback.md`"*
3. Claude recognizes the trigger, loads the skill file, and begins executing its instructions

### What happens during execution

The skill instructs Claude to:
```
Step 1 → Read data/raw/github_issues.json        (Read tool)
Step 2 → Read data/raw/mock_surveys.json          (Read tool)
Step 3 → Read data/raw/mock_support_tickets.json  (Read tool)
Step 4 → Read all other raw source files          (Read tool)
Step 5 → For each feedback item, classify it into
          Bug / Feature Request / UX Issue using
          Claude's own understanding of the text   (Claude's intelligence — no API call)
Step 6 → Write classified items to
          data/processed/feedback_classified.json  (Write tool)
Step 7 → Compute clusters, counts, trends         (Claude's intelligence)
Step 8 → Write data/processed/feedback_summary.json
          and data/processed/clusters.json         (Write tool)
Step 9 → Run: git add . && git commit && git push (Bash tool)
Step 10 → Open dashboard in browser               (Bash tool: open URL)
Step 11 → Report: "Done. Found X new issues..."
```

### Why it costs nothing

Claude Code IS the model (claude-sonnet-4-6). When the skill instructs Claude to "classify this feedback item," Claude uses its own language understanding — the same intelligence it uses to answer your questions. No separate API call is made. No tokens are billed beyond your normal Claude Code usage.

### Context retention for follow-up Q&A

After the skill runs, `data/processed/feedback_summary.json` is on disk. When you ask:
> *"Are there any UX issues with the sidebar?"*

Claude reads that file and answers from it — it does not re-run the full pipeline. This is why the summary JSON is carefully structured: it is designed to answer questions, not just store data.

### The skill file format

```markdown
---
name: refresh-feedback
description: Scans and classifies VS Code customer feedback, updates the dashboard
trigger: "refresh the feedback page", "update feedback", "scan feedback"
---

## Instructions

You are running the VS Code Customer Feedback Intelligence pipeline.

### Step 1: Read all raw feedback sources
Read each file in data/raw/ and collect all feedback items.

### Step 2: Classify each item
For each feedback item, determine:
- category: bug | feature_request | ux_issue | praise
- sub_category: (see taxonomy in FeedbackResearch.md Section 6)
- sentiment: positive | neutral | negative
- urgency: low | medium | high | critical
- product_area: terminal | editor | extensions | git | copilot | settings | sidebar | debugging | search | notebooks | null
- one_line_summary: a 10-word description

Use your full language understanding. Consider context, tone, and intent — not just keywords.

### Step 3: Write processed data
Write results to data/processed/feedback_classified.json
Compute clusters and write to data/processed/clusters.json
Write summary statistics to data/processed/feedback_summary.json

### Step 4: Push to GitHub
Run: git add data/ && git commit -m "chore: refresh feedback data $(date +%Y-%m-%d)" && git push

### Step 5: Report
Tell the user:
- How many items were processed
- Category breakdown
- Top 3 most urgent clusters
- Any spikes (clusters that grew >30% since last run)
```

---

## 4. Classification Strategy — Two Layers

The system uses two complementary classifiers. Neither requires a paid API.

| | Layer 1: SmartFeedbackClassifier | Layer 2: Claude Code Skill |
|---|---|---|
| **Used by** | GitHub Actions (automated, no Claude Code present) | Conversational trigger (you're present) |
| **Accuracy** | ~85–88% | ~95%+ |
| **Cost** | $0 (pure Python) | $0 (Claude Code session) |
| **How it works** | Multi-signal pattern scoring + Bayesian priors | Full language model reasoning |
| **Speed** | ~1ms per item | ~2–5s per item |
| **Handles nuance** | Partially (negation detection, context) | Yes (sarcasm, implicit meaning, ambiguity) |
| **Confidence score** | Yes — items <0.5 flagged for review | Yes — Claude notes uncertainty |

**Why not just one?** The GitHub Actions workflow runs in GitHub's cloud at 9am UTC every day — Claude Code is not present. It needs the Python classifier. When you interact with the skill, Claude's intelligence is available, so we use it.

**Low-confidence items** from the Python classifier are written to `data/processed/needs_review.json`. When you run the skill conversationally, Claude re-examines those items first.

---

## Phase 0 — Repository & GitHub Pages

### Tasks

**0.1** Create the GitHub repository
- Go to https://github.com/new
- Repository name: `CustomerFeedback`
- Visibility: **Public** (required for free GitHub Pages)
- Leave all checkboxes unchecked (no README, no .gitignore)
- Click **Create repository**

**0.2** Generate a Personal Access Token (PAT)
- Go to https://github.com/settings/tokens/new
- Note: `CustomerFeedback daily refresh`
- Expiration: 90 days (or No expiration for a portfolio project)
- Scopes: check **repo** (full control of private repositories — this also covers public)
- Click **Generate token**
- Copy the token immediately — you cannot see it again
- Save it somewhere safe (you'll paste it into Claude Code settings)

**0.3** Initialize git and push initial files

```bash
# Run these from inside the "Customer Feedback Loop" project folder
cd "/Users/shayalpatel/Documents/Claude Projects/Customer Feedback Loop"

git init
git remote add origin https://github.com/shayalpatel/CustomerFeedback.git
git add dashboard/ data/ scripts/ .claude/ .github/ CLAUDE.md FeedbackResearch.md FEEDBACKPLAN.md
git commit -m "init: customer feedback intelligence dashboard"
git branch -M main
git push -u origin main
```

**0.4** Enable GitHub Pages
- Go to https://github.com/shayalpatel/CustomerFeedback/settings/pages
- Source: **Deploy from a branch**
- Branch: `main` / folder: `/ (root)`
- Click **Save**
- Wait ~60 seconds, then visit: https://shayalpatel.github.io/CustomerFeedback

**0.5** Configure GitHub MCP in Claude Code (for future pushes from skill)
```json
// Add to ~/.claude/settings.json under "mcpServers"
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "your_pat_here"
    }
  }
}
```

### Phase 0 Verification Checklist

```
[ ] 0.1  github.com/shayalpatel/CustomerFeedback exists and is Public
[ ] 0.2  PAT generated and saved securely
[ ] 0.3  git push completed without errors (check: no "rejected" message)
[ ] 0.4  GitHub Pages enabled — Settings → Pages shows "Your site is live at..."
[ ] 0.5  URL loads: https://shayalpatel.github.io/CustomerFeedback
[ ] 0.5  Dashboard charts render (donut + trend line both visible)
[ ] 0.5  Stat card click filters clusters and feed correctly
[ ] 0.5  Clicking a cluster card opens the drill-down modal

Phase 0 PASS if all 8 boxes checked. Do not proceed to Phase 1 until passed.
```

---

## Phase 1 — Data Foundation

### Tasks

**1.1** Create `data/raw/github_issues.json` — mock GitHub Issues (public source)
**1.2** Create `data/raw/mock_surveys.json` — NPS, CSAT, email survey responses
**1.3** Create `data/raw/mock_support_tickets.json` — internal support tickets
**1.4** Create `data/raw/mock_in_app.json` — in-app widget feedback (thumbs + comment)
**1.5** Create `data/raw/mock_community.json` — Reddit, Tech Community, Stack Overflow
**1.6** Create `data/raw/mock_reviews.json` — G2 and Capterra review text
**1.7** Create `data/processed/feedback_classified.json` — empty array, schema defined
**1.8** Create `data/processed/feedback_summary.json` — empty object, schema defined
**1.9** Create `data/processed/clusters.json` — empty array, schema defined

### Raw Item Schema (all sources use this shape)

```json
{
  "id": "gh-12847",
  "source": "github_issues",
  "source_type": "external",
  "timestamp": "2026-05-05T07:23:00Z",
  "raw_text": "Extension host keeps crashing when I open my monorepo with 40+ packages.",
  "author_id": "user_a3f9b",
  "rating": null,
  "version": "1.89.1",
  "url": "https://github.com/microsoft/vscode/issues/12847"
}
```

### Source type values
```
github_issues     → source_type: "external"
nps_survey        → source_type: "survey"
csat_survey       → source_type: "survey"
email_survey      → source_type: "survey"
support_ticket    → source_type: "internal"
in_app_widget     → source_type: "internal"
reddit            → source_type: "social"
tech_community    → source_type: "external"
stack_overflow    → source_type: "external"
g2_review         → source_type: "external"
capterra_review   → source_type: "external"
```

### Classified Item Schema (`feedback_classified.json`)

```json
{
  "id": "gh-12847",
  "source": "github_issues",
  "source_type": "external",
  "timestamp": "2026-05-05T07:23:00Z",
  "raw_text": "Extension host keeps crashing when I open my monorepo...",
  "category": "bug",
  "sub_category": "crash",
  "sentiment": "negative",
  "urgency": "critical",
  "product_area": "extensions",
  "one_line_summary": "Extension host crashes on large monorepos",
  "confidence": 0.94,
  "cluster_id": "cluster-001",
  "classified_at": "2026-05-05T09:00:12Z",
  "classified_by": "claude_skill"
}
```

### Summary Schema (`feedback_summary.json`)
> This is what Claude reads when you ask follow-up questions

```json
{
  "generated_at": "2026-05-05T09:00:45Z",
  "period_days": 30,
  "totals": {
    "all": 2847,
    "bug": 1203,
    "feature_request": 1081,
    "ux_issue": 563
  },
  "by_source": {
    "github_issues": 1142,
    "in_app_widget": 487,
    "nps_survey": 374,
    "reddit": 268,
    "support_ticket": 211,
    "tech_community": 163,
    "g2_review": 128,
    "stack_overflow": 74
  },
  "by_product_area": {
    "extensions": 312,
    "copilot": 287,
    "sidebar": 201,
    "terminal": 188,
    "git": 143,
    "editor": 134,
    "settings": 98,
    "debugging": 76,
    "search": 71,
    "notebooks": 52
  },
  "critical_items": [
    {
      "id": "gh-12847",
      "summary": "Extension host crashes on large monorepos",
      "urgency": "critical",
      "source": "github_issues"
    }
  ],
  "top_clusters": [...],
  "week_over_week": {
    "bug_change_pct": 18,
    "feature_change_pct": -4,
    "ux_change_pct": 9
  }
}
```

### Clusters Schema (`clusters.json`)

```json
[
  {
    "cluster_id": "cluster-001",
    "title": "Extension host crashes on large workspaces",
    "category": "bug",
    "item_count": 127,
    "growth_pct": 43,
    "urgency": "critical",
    "sources": ["github_issues", "in_app_widget", "support_ticket"],
    "product_area": "extensions",
    "affected_versions": ["1.89.0", "1.89.1"],
    "first_seen": "2026-04-18",
    "sample_texts": [
      "Extension host crashes every time on my monorepo with 40+ packages",
      "Extension host process died after 5 minutes",
      "Crashed again mid-session"
    ]
  }
]
```

### Phase 1 Verification Checklist

```
[ ] 1.1  data/raw/github_issues.json exists, valid JSON, ≥15 items
[ ] 1.2  data/raw/mock_surveys.json exists, valid JSON, ≥10 items (mix of NPS/CSAT/email)
[ ] 1.3  data/raw/mock_support_tickets.json exists, valid JSON, ≥8 items
[ ] 1.4  data/raw/mock_in_app.json exists, valid JSON, ≥8 items
[ ] 1.5  data/raw/mock_community.json exists, valid JSON, ≥10 items (Reddit/Tech Comm/SO)
[ ] 1.6  data/raw/mock_reviews.json exists, valid JSON, ≥6 items (G2/Capterra)
[ ] 1.7  All raw items follow the Raw Item Schema (spot-check 3 items per file)
[ ] 1.8  data/processed/ folder exists with .gitkeep (empty until Phase 2 runs)
[ ] 1.9  data/README.md accurately describes all files above

Phase 1 PASS if all 9 boxes checked.
```

---

## Phase 2 — Smart Classification Script

This is the core of the automated pipeline. The classifier runs inside GitHub Actions — no Claude Code, no API key, completely free.

### Tasks

**2.1** Create `scripts/classify_feedback.py`
**2.2** Implement `SmartFeedbackClassifier` with weighted multi-signal scoring
**2.3** Implement source-aware Bayesian priors (GitHub Issues likely bugs; NPS surveys likely features)
**2.4** Implement negation detection ("not confusing" ≠ "confusing")
**2.5** Implement product area detection (14 areas via regex)
**2.6** Implement urgency and sentiment scoring
**2.7** Implement `SimpleClustering` using TF-IDF cosine similarity (stdlib only)
**2.8** Write output to `data/processed/` files
**2.9** Test locally: `python3 scripts/classify_feedback.py`

### Code: `scripts/classify_feedback.py`

```python
"""
SmartFeedbackClassifier — free, API-free, multi-signal feedback classification
Uses: Python stdlib only (re, json, math, collections, datetime)
Accuracy: ~85-88% on Bug / Feature Request / UX Issue taxonomy
"""

import re
import json
import math
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

# ─── Types ───────────────────────────────────────────────────────────────────

Category = Literal['bug', 'feature_request', 'ux_issue', 'praise', 'unclear']
Urgency  = Literal['low', 'medium', 'high', 'critical']
Sentiment = Literal['positive', 'neutral', 'negative']

@dataclass
class ClassificationResult:
    category:        Category
    sub_category:    str
    sentiment:       Sentiment
    urgency:         Urgency
    product_area:    str | None
    one_line_summary: str
    confidence:      float
    classified_by:   str = 'script_v1'

# ─── Classifier ──────────────────────────────────────────────────────────────

class SmartFeedbackClassifier:
    """
    Multi-signal linguistic classifier.
    Each signal is a (regex_pattern, weight) tuple.
    Weights are additive — the category with the highest weighted score wins.
    Source priors apply a Bayesian adjustment before scoring.
    """

    # (pattern, weight)  — all matched case-insensitively
    BUG = [
        (r'\bcrash(es|ed|ing)?\b',                              4.0),
        (r"\b(doesn't|don't|won't|can't|cannot)\s+work\b",     3.5),
        (r'\bstopped?\s+work(ing)?\b',                          3.5),
        (r'\bregression\b',                                     3.5),
        (r'\bused\s+to\s+work\b',                               3.0),
        (r'\bsteps?\s+to\s+reproduce\b',                        3.0),
        (r'\bexpected\s+(behavior|result|output)\b',            2.5),
        (r'\bactual\s+(behavior|result|output)\b',              2.5),
        (r'\b(broken?|bugged?)\b',                              2.5),
        (r'\b(exception|traceback|stack\s+trace)\b',            2.5),
        (r'\bnot\s+work(ing)?\b',                               2.0),
        (r'\bfail(s|ed|ing)?\b',                                2.0),
        (r'\bunexpected\s+(behavior|error|result)\b',           2.0),
        (r'\bafter\s+(the\s+)?(last\s+)?(update|upgrade)\b',   2.0),
        (r'\bsince\s+(v|version)?\s*\d+\.\d+',                 2.0),
        (r'\bworkaround\b',                                     1.5),
        (r'\b(data\s+loss|corrupt)\b',                          4.5),
        (r'\b(freeze|hang|stuck|unresponsive)\b',               2.5),
    ]

    FEATURE = [
        (r'\bfeature\s+request\b',                              4.5),
        (r'\bplease\s+add\b',                                   3.5),
        (r'\bwould\s+(love|appreciate)\b',                      3.5),
        (r'\bwish\s+(there\s+was|it\s+(had|supported))\b',     3.5),
        (r'\bneed\s+a\s+way\s+to\b',                           3.0),
        (r'\bit\s+would\s+be\s+(great|nice|helpful|awesome)\b', 3.0),
        (r'\bshould\s+(have|support|allow|include)\b',          2.5),
        (r'\bplease\s+(consider|implement|support)\b',          2.5),
        (r'\b(allow|let)\s+(us|me|users?)\s+to\b',             2.5),
        (r'\bi\s+have\s+to\s+manually\b',                      2.5),  # implies missing feature
        (r'\bevery\s+time\s+i\s+want\s+to\b',                  2.0),  # implies missing feature
        (r'\b(suggest(ion)?|request|enhancement|proposal)\b',  2.0),
        (r'\b(roadmap|planned|future(\s+version)?)\b',          1.5),
        # Competitor comparisons imply missing feature
        (r'\b(jetbrains|intellij|sublime\s+text|vim|neovim|cursor|atom)\b', 2.0),
        (r'\blike\s+\w+\s+(does|has|supports)\b',              2.0),
        (r'\bsupport\s+for\b',                                  1.5),
    ]

    UX = [
        (r'\b(un)?intuitive\b',                                 3.5),
        (r'\bhard\s+to\s+(find|use|navigate|discover|understand)\b', 3.5),
        (r'\btoo\s+many\s+clicks?\b',                           3.5),
        (r'\boverwhelming\b',                                   3.0),
        (r'\bconfus(ing|ed)\b',                                 3.0),
        (r'\bfrustrat(ing|ed|ion)\b',                          2.5),
        (r'\bburied\s+(in|under|behind)\b',                    3.0),
        (r'\bcan\'t\s+find\b',                                  2.5),
        (r'\bhard\s+to\s+discover\b',                          3.0),
        (r'\b(clunky|awkward|cumbersome)\b',                   2.5),
        (r'\btakes?\s+(forever|too\s+long)\b',                 2.0),
        (r'\b(unclear|ambiguous)\b',                            2.0),
        (r'\blow\s+contrast\b',                                 3.0),
        (r'\b(ugly|cluttered|dated|ancient)\b',                2.0),
        (r'\b(inconsistent|inconsistency)\b',                  2.5),
        (r'\b(inaccessible|accessibility)\b',                  2.5),
    ]

    PRAISE = [
        (r'\b(great|amazing|excellent|fantastic|wonderful)\b',  2.5),
        (r'\blove\s+(vs\s*code|this|it|the)\b',               3.0),
        (r'\bbest\s+(editor|ide|tool|product)\b',              3.0),
        (r'\bthank\s+(you|s)\b',                               2.0),
        (r'\bperfect\b',                                        2.0),
        (r'\bkeep\s+(up\s+the\s+)?(great|good)\s+work\b',     2.5),
    ]

    # Source-type adjustments: base probability before signals are scored.
    # Higher prior = more likely to be classified as that category from this source.
    SOURCE_PRIORS: dict[str, dict[str, float]] = {
        'github_issues':    {'bug': 0.55, 'feature_request': 0.28, 'ux_issue': 0.12, 'praise': 0.05},
        'support_ticket':   {'bug': 0.65, 'feature_request': 0.18, 'ux_issue': 0.13, 'praise': 0.04},
        'in_app_widget':    {'bug': 0.38, 'feature_request': 0.32, 'ux_issue': 0.22, 'praise': 0.08},
        'nps_survey':       {'bug': 0.20, 'feature_request': 0.45, 'ux_issue': 0.25, 'praise': 0.10},
        'csat_survey':      {'bug': 0.25, 'feature_request': 0.35, 'ux_issue': 0.30, 'praise': 0.10},
        'email_survey':     {'bug': 0.22, 'feature_request': 0.42, 'ux_issue': 0.26, 'praise': 0.10},
        'reddit':           {'bug': 0.38, 'feature_request': 0.33, 'ux_issue': 0.22, 'praise': 0.07},
        'tech_community':   {'bug': 0.42, 'feature_request': 0.30, 'ux_issue': 0.22, 'praise': 0.06},
        'stack_overflow':   {'bug': 0.62, 'feature_request': 0.22, 'ux_issue': 0.12, 'praise': 0.04},
        'g2_review':        {'bug': 0.28, 'feature_request': 0.28, 'ux_issue': 0.32, 'praise': 0.12},
        'capterra_review':  {'bug': 0.28, 'feature_request': 0.28, 'ux_issue': 0.32, 'praise': 0.12},
        '_default':         {'bug': 0.40, 'feature_request': 0.33, 'ux_issue': 0.20, 'praise': 0.07},
    }

    PRODUCT_AREAS: dict[str, str] = {
        'terminal':     r'\b(terminal|shell|bash|zsh|powershell|cmd|command[\s-]line|console)\b',
        'editor':       r'\b(editor|cursor|caret|selection|indent|tab|syntax\s+highlight|autocomplete|intellisense)\b',
        'extensions':   r'\b(extension[\s-]?host|plugin|extension|marketplace|vsix)\b',
        'git':          r'\b(git|diff|merge|commit|branch|source\s+control|pull\s+request|blame)\b',
        'copilot':      r'\b(copilot|ai\s+suggestion|inline\s+suggestion|completion|ghost\s+text)\b',
        'settings':     r'\b(settings|config|configuration|preference|keybinding|shortcut)\b',
        'sidebar':      r'\b(sidebar|side\s+bar|panel|file\s+explorer|outline|timeline|activity\s+bar)\b',
        'debugging':    r'\b(debug|debugger|breakpoint|watch|call\s+stack|launch\.json|attach)\b',
        'search':       r'\b(search|find|replace|grep|ripgrep|fuzzy\s+find)\b',
        'notebooks':    r'\b(jupyter|notebook|cell|kernel|ipynb)\b',
        'remote':       r'\b(remote|ssh|wsl|container|codespace|dev\s+container)\b',
        'themes':       r'\b(theme|color\s+scheme|icon\s+theme|dark\s+mode|light\s+mode|contrast)\b',
        'workspaces':   r'\b(workspace|project|monorepo|multi-root|folder)\b',
        'performance':  r'\b(slow|performance|memory|cpu|lag|latency|startup)\b',
    }

    URGENCY_PATTERNS: dict[str, list[str]] = {
        'critical': [
            r'\bdata\s+loss\b', r'\bcompletely\s+broken\b', r'\bunusable\b',
            r'\bevery\s+time\b', r'\beverytime\b', r'\balways\s+crash', r'\bblocking\s+my\s+work\b',
        ],
        'high': [
            r'\bblocking\b', r"\bcan't\s+work\b", r'\bproduction\b',
            r'\bour\s+team\b', r'\bmultiple\s+(users?|people|devs?)\b',
        ],
        'medium': [
            r'\bregularly\b', r'\boften\b', r'\bfrequently\b', r'\bmost\s+of\s+the\s+time\b',
            r'\bseveral\s+times\b',
        ],
    }

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _score(self, text: str, signals: list[tuple[str, float]]) -> float:
        tl = text.lower()
        total = 0.0
        for pattern, weight in signals:
            if re.search(pattern, tl):
                total += weight
        return total

    def _negated(self, text: str, pattern: str) -> bool:
        """Return True if the pattern match is immediately preceded by a negation."""
        tl = text.lower()
        for m in re.finditer(pattern, tl):
            before = tl[:m.start()].split()[-4:]
            if any(n in before for n in ["not", "n't", "no", "never", "without", "barely"]):
                return True
        return False

    def _product_area(self, text: str) -> str | None:
        tl = text.lower()
        for area, pattern in self.PRODUCT_AREAS.items():
            if re.search(pattern, tl):
                return area
        return None

    def _urgency(self, text: str, category: str) -> Urgency:
        if category not in ('bug', 'ux_issue'):
            return 'low'
        tl = text.lower()
        for level in ('critical', 'high', 'medium'):
            for pattern in self.URGENCY_PATTERNS[level]:
                if re.search(pattern, tl):
                    return level  # type: ignore
        return 'low'

    def _sentiment(self, text: str) -> Sentiment:
        tl = text.lower()
        pos = len(re.findall(
            r'\b(great|love|amazing|excellent|perfect|best|helpful|awesome|fantastic)\b', tl))
        neg = len(re.findall(
            r'\b(crash|broken|terrible|awful|hate|frustrat|annoying|useless|disappoint|horrible)\b', tl))
        if pos > neg + 1:   return 'positive'
        if neg > pos:       return 'negative'
        return 'neutral'

    def _sub_category(self, text: str, category: str) -> str:
        tl = text.lower()
        if category == 'bug':
            if re.search(r'\bcrash\b', tl):                return 'crash'
            if re.search(r'\b(slow|lag|delay|timeout)\b', tl): return 'performance'
            if re.search(r'\b(intermittent|sometimes|random)\b', tl): return 'reliability'
            return 'unexpected_behavior'
        if category == 'feature_request':
            if re.search(r'\b(integrat|connect|sync|webhook|api)\b', tl): return 'integration'
            if re.search(r'\b(improve|better|enhance|upgrade)\b', tl):    return 'enhancement'
            return 'new_feature'
        if category == 'ux_issue':
            if re.search(r'\b(find|discover|buried|menu|navigate)\b', tl): return 'navigation'
            if re.search(r'\b(contrast|color|theme|font|visual|ui)\b', tl): return 'visual_design'
            if re.search(r'\b(access|screen\s+reader|keyboard\s+nav)\b', tl): return 'accessibility'
            return 'workflow_friction'
        return 'general'

    def _summary(self, text: str, category: str, product_area: str | None) -> str:
        """Generate a ≤12-word summary."""
        area_str = f" in {product_area.replace('_',' ')}" if product_area else ''
        cat_map = {
            'bug': f"Bug{area_str}: ",
            'feature_request': f"Feature request{area_str}: ",
            'ux_issue': f"UX issue{area_str}: ",
            'praise': "Positive feedback: ",
            'unclear': "Unclear: ",
        }
        prefix = cat_map.get(category, '')
        # Take first sentence, trim to 10 words
        first = re.split(r'[.!?]', text.strip())[0].strip()
        words = first.split()[:10]
        return prefix + ' '.join(words) + ('...' if len(first.split()) > 10 else '')

    # ── Main entry point ──────────────────────────────────────────────────────

    def classify(self, text: str, source: str = '_default') -> ClassificationResult:
        priors = self.SOURCE_PRIORS.get(source, self.SOURCE_PRIORS['_default'])

        # Raw signal scores
        raw = {
            'bug':              self._score(text, self.BUG),
            'feature_request':  self._score(text, self.FEATURE),
            'ux_issue':         self._score(text, self.UX),
            'praise':           self._score(text, self.PRAISE),
        }

        # Apply Bayesian prior: adjusted = raw * (1 + prior)
        adjusted = {cat: score * (1 + priors[cat]) for cat, score in raw.items()}

        best = max(adjusted, key=adjusted.get)  # type: ignore
        best_score = adjusted[best]
        total = sum(adjusted.values()) or 1.0
        confidence = round(min(best_score / total, 0.99), 3)

        # No signals fired → fall back to prior, low confidence
        if best_score == 0.0:
            best = max(priors, key=priors.get)  # type: ignore
            confidence = round(priors[best] * 0.5, 3)

        # If confidence is very low, mark as unclear
        final_category: Category = 'unclear' if confidence < 0.35 else best  # type: ignore

        product_area = self._product_area(text)
        urgency      = self._urgency(text, final_category)
        sentiment    = self._sentiment(text)
        sub_cat      = self._sub_category(text, final_category)
        summary      = self._summary(text, final_category, product_area)

        return ClassificationResult(
            category=final_category,
            sub_category=sub_cat,
            sentiment=sentiment,
            urgency=urgency,
            product_area=product_area,
            one_line_summary=summary,
            confidence=confidence,
        )


# ─── TF-IDF Clustering ───────────────────────────────────────────────────────

class SimpleClustering:
    """
    Groups similar feedback items using TF-IDF cosine similarity.
    No external dependencies — pure Python stdlib.
    """
    STOPWORDS = {
        'i','me','my','we','us','our','the','a','an','and','or','but','in','on','at',
        'to','for','of','is','it','this','that','was','are','be','been','have','has',
        'had','do','does','did','will','would','could','should','with','from','by',
        'as','up','out','when','if','its','there','their','they','he','she','not',
        'no','so','just','also','can','use','using','used','get','got','make','made',
        'vs','code','vscode',
    }

    def __init__(self, threshold: float = 0.30):
        self.threshold = threshold

    def _tokenize(self, text: str) -> list[str]:
        clean = re.sub(r'[^\w\s]', ' ', text.lower())
        return [w for w in clean.split() if w not in self.STOPWORDS and len(w) > 2]

    def _build_tfidf(self, docs: list[list[str]]) -> list[dict[str, float]]:
        N = len(docs)
        tf = [Counter(doc) for doc in docs]
        df: Counter = Counter()
        for doc in docs:
            for term in set(doc):
                df[term] += 1
        idf = {term: math.log((N + 1) / (count + 1)) + 1 for term, count in df.items()}
        vectors = []
        for tf_doc in tf:
            vec = {t: tf_doc[t] * idf.get(t, 1.0) for t in tf_doc}
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            vectors.append({t: v / norm for t, v in vec.items()})
        return vectors

    def _cosine(self, v1: dict, v2: dict) -> float:
        common = set(v1) & set(v2)
        return sum(v1[t] * v2[t] for t in common)

    def cluster(self, items: list[dict]) -> list[dict]:
        """
        items: list of {'id', 'text', 'category', ...}
        Returns: clusters sorted by size, largest first.
        """
        if not items:
            return []
        docs = [self._tokenize(item['text']) for item in items]
        vectors = self._build_tfidf(docs)
        assigned = [False] * len(items)
        clusters = []

        for i, item in enumerate(items):
            if assigned[i]:
                continue
            cluster_members = [i]
            assigned[i] = True
            for j in range(i + 1, len(items)):
                if assigned[j]:
                    continue
                # Only cluster same category
                if items[j].get('category') != item.get('category'):
                    continue
                if self._cosine(vectors[i], vectors[j]) >= self.threshold:
                    cluster_members.append(j)
                    assigned[j] = True

            member_items = [items[k] for k in cluster_members]
            clusters.append({
                'cluster_id': f"cluster-{len(clusters)+1:03d}",
                'category': item['category'],
                'item_count': len(cluster_members),
                'member_ids': [items[k]['id'] for k in cluster_members],
                'representative_text': item['text'],
                'sample_texts': [items[k]['text'] for k in cluster_members[:3]],
            })

        return sorted(clusters, key=lambda c: c['item_count'], reverse=True)


# ─── Pipeline runner ─────────────────────────────────────────────────────────

def run():
    BASE = Path(__file__).parent.parent
    RAW  = BASE / 'data' / 'raw'
    PROC = BASE / 'data' / 'processed'
    PROC.mkdir(parents=True, exist_ok=True)

    clf = SmartFeedbackClassifier()
    clstr = SimpleClustering(threshold=0.30)

    # 1. Load all raw items
    raw_items = []
    for path in sorted(RAW.glob('*.json')):
        with open(path) as f:
            items = json.load(f)
            raw_items.extend(items if isinstance(items, list) else [items])

    print(f"Loaded {len(raw_items)} raw feedback items from {RAW}")

    # 2. Classify each item
    classified = []
    needs_review = []
    for item in raw_items:
        result = clf.classify(item.get('raw_text', ''), source=item.get('source', '_default'))
        enriched = {**item, **asdict(result), 'classified_at': datetime.now(timezone.utc).isoformat()}
        classified.append(enriched)
        if result.confidence < 0.50:
            needs_review.append(enriched)

    with open(PROC / 'feedback_classified.json', 'w') as f:
        json.dump(classified, f, indent=2)
    print(f"Classified {len(classified)} items ({len(needs_review)} flagged for review)")

    # 3. Cluster
    cluster_input = [{'id': i['id'], 'text': i['raw_text'], 'category': i['category']} for i in classified]
    clusters = clstr.cluster(cluster_input)
    with open(PROC / 'clusters.json', 'w') as f:
        json.dump(clusters, f, indent=2)
    print(f"Identified {len(clusters)} clusters")

    # 4. Build summary
    totals: dict = Counter(i['category'] for i in classified)
    by_source: dict = Counter(i['source'] for i in classified)
    by_area: dict = Counter(i['product_area'] for i in classified if i.get('product_area'))
    critical = [i for i in classified if i.get('urgency') == 'critical']

    summary = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'period_days': 30,
        'totals': dict(totals),
        'by_source': dict(by_source),
        'by_product_area': dict(by_area),
        'critical_items': critical[:10],
        'needs_review_count': len(needs_review),
        'top_clusters': clusters[:10],
    }
    with open(PROC / 'feedback_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    # 5. Low-confidence items for Claude to re-examine
    with open(PROC / 'needs_review.json', 'w') as f:
        json.dump(needs_review, f, indent=2)

    print(f"Pipeline complete. Summary written to {PROC}/feedback_summary.json")
    print(f"Category breakdown: {dict(totals)}")

if __name__ == '__main__':
    run()
```

### Phase 2 Verification Checklist

```
[ ] 2.1  scripts/classify_feedback.py exists
[ ] 2.2  python3 scripts/classify_feedback.py runs without errors
[ ] 2.3  data/processed/feedback_classified.json created, all items have 'category' field
[ ] 2.4  data/processed/clusters.json created, has ≥1 cluster
[ ] 2.5  data/processed/feedback_summary.json created, has 'totals' and 'top_clusters'
[ ] 2.6  data/processed/needs_review.json created (may be empty — that's fine)
[ ] 2.7  Spot-check: open feedback_classified.json, verify 3 items are categorized correctly
[ ] 2.8  Spot-check: a crash report → category: "bug", a "please add" → "feature_request"
[ ] 2.9  No items with category = null or missing

Phase 2 PASS if all 9 boxes checked.
```

---

## Phase 3 — Claude Code Skill

### Tasks

**3.1** Write `.claude/skills/refresh-feedback.md`
**3.2** Update `CLAUDE.md` to reference the skill and define the trigger
**3.3** Test: say "Refresh the feedback page" — skill should load and execute
**3.4** Verify: all three `data/processed/` files are updated after run
**3.5** Test Q&A: ask "Are there any UX issues with the sidebar?" — Claude should answer from the summary file

### Code: `.claude/skills/refresh-feedback.md`

```markdown
---
name: refresh-feedback
description: Runs the VS Code customer feedback intelligence pipeline. Reads all raw feedback sources, classifies each item using Claude's language understanding, clusters similar items, writes processed data files, pushes to GitHub, and prepares context for follow-up questions.
---

## Overview

You are running the Customer Feedback Intelligence pipeline for VS Code (microsoft/vscode).

**Project location:** /Users/shayalpatel/Documents/Claude Projects/Customer Feedback Loop

## Step 1: Read all raw feedback sources

Read every JSON file in `data/raw/`. Each file represents a different feedback source:
- `github_issues.json` — GitHub Issues (external)
- `mock_surveys.json` — NPS, CSAT, email surveys (survey)
- `mock_support_tickets.json` — Microsoft support tickets (internal)
- `mock_in_app.json` — In-app widget feedback (internal)
- `mock_community.json` — Reddit, Tech Community, Stack Overflow (external/social)
- `mock_reviews.json` — G2, Capterra reviews (external)

Collect all items into a working list.

## Step 2: Check data/processed/needs_review.json

If `needs_review.json` exists and has items, prioritize classifying those first — the automated script flagged them as ambiguous.

## Step 3: Classify each feedback item

For each item, use your full language understanding to determine:

- **category:** `bug` | `feature_request` | `ux_issue` | `praise`
  - bug: product behaves unexpectedly or is broken
  - feature_request: user wants a capability that doesn't exist
  - ux_issue: product works but is confusing, inefficient, or frustrating
  - praise: positive feedback

- **sub_category:** (see FeedbackResearch.md Section 6 for full list)

- **sentiment:** `positive` | `neutral` | `negative`

- **urgency:** `low` | `medium` | `high` | `critical`
  - critical: data loss, completely unusable, affects every session
  - high: blocking work, affects many users, production impact
  - medium: happens regularly, meaningful friction
  - low: minor, occasional, cosmetic

- **product_area:** terminal | editor | extensions | git | copilot | settings | sidebar | debugging | search | notebooks | remote | themes | workspaces | performance | null

- **one_line_summary:** A 10-word plain-English description

Consider context, tone, and intent. "I have to manually do X every time" is a feature_request even without the words "please add." A 1-star review that says "great UI but crashes constantly" is primarily a bug.

## Step 4: Identify clusters

Group items that describe the same underlying issue. A cluster is 3+ items about the same problem.

For each cluster, determine:
- A representative title (the clearest description of the issue)
- All member item IDs
- Combined source list
- Trend: is volume growing or stable?
- Urgency of the cluster overall

## Step 5: Write processed data files

Write `data/processed/feedback_classified.json` — all classified items.
Write `data/processed/clusters.json` — all clusters sorted by item count.
Write `data/processed/feedback_summary.json` — aggregate stats and top clusters.

## Step 6: Push to GitHub

Run: `git add data/processed/ && git commit -m "chore: feedback refresh $(date '+%Y-%m-%d %H:%M')" && git push`

If git push fails, report the error and continue.

## Step 7: Open the dashboard

Run: `open https://shayalpatel.github.io/CustomerFeedback`

## Step 8: Report to user

Tell the user:
1. Total items processed and category breakdown
2. Top 3 most urgent clusters (name + count + urgency)
3. Any spikes: clusters that grew since last run
4. Count of items that needed human review

Then say: "You can now ask me questions about the feedback — e.g., 'Are there any sidebar bugs?' or 'What are users asking for in the terminal?'"
```

### Code: `CLAUDE.md` additions

```markdown
## Feedback Loop Skill

When the user says something similar to "Refresh the feedback page", "update the feedback", 
"scan feedback", or "run the feedback pipeline", run the skill at:
.claude/skills/refresh-feedback.md

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

### Phase 3 Verification Checklist

```
[ ] 3.1  .claude/skills/refresh-feedback.md exists
[ ] 3.2  CLAUDE.md has trigger definition and post-run Q&A instructions
[ ] 3.3  Say "Refresh the feedback page" → Claude acknowledges and begins the skill
[ ] 3.4  Skill completes all 8 steps without stopping unexpectedly
[ ] 3.5  data/processed/ files are updated (check timestamps)
[ ] 3.6  Git push succeeds (GitHub repo shows updated commit)
[ ] 3.7  Ask "Are there any UX issues with the sidebar?" → Claude gives specific answer from data
[ ] 3.8  Ask "What is the most critical bug right now?" → Claude names the crash cluster

Phase 3 PASS if all 8 boxes checked.
```

---

## Phase 4 — Pipeline Scripts

### Tasks

**4.1** Create `scripts/fetch_feedback.py` — fetches VS Code GitHub Issues (public API, no token needed for reading) and combines with mock data
**4.2** Create `scripts/generate_dashboard.py` — reads processed JSON, writes `dashboard/index.html`
**4.3** Test locally: `python3 scripts/fetch_feedback.py && python3 scripts/classify_feedback.py && python3 scripts/generate_dashboard.py`

### Code: `scripts/fetch_feedback.py`

```python
"""
Fetches VS Code GitHub Issues (public, no auth needed for 60 req/hr)
and combines with mock data files into data/raw/.
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parent.parent
RAW  = BASE / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)

def fetch_github_issues(repo: str = 'microsoft/vscode', per_page: int = 50) -> list[dict]:
    """Fetch recent open issues from a public GitHub repo."""
    url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page={per_page}&sort=updated"
    req = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CustomerFeedbackBot/1.0'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            issues = json.loads(resp.read())
    except Exception as e:
        print(f"GitHub API error: {e} — using cached/mock data only")
        return []

    items = []
    for issue in issues:
        body = (issue.get('body') or '').strip()
        if not body or len(body) < 20:
            continue
        items.append({
            'id':          f"gh-{issue['number']}",
            'source':      'github_issues',
            'source_type': 'external',
            'timestamp':   issue['updated_at'],
            'raw_text':    f"{issue['title']}. {body[:500]}".strip(),
            'author_id':   f"gh_user_{hash(issue['user']['login']) % 99999}",
            'rating':      None,
            'version':     None,
            'url':         issue['html_url'],
        })

    print(f"Fetched {len(items)} GitHub Issues from {repo}")
    return items


def load_mock_data() -> list[dict]:
    """Load all mock JSON files (surveys, tickets, in-app, etc.)"""
    mock_files = [
        'mock_surveys.json',
        'mock_support_tickets.json',
        'mock_in_app.json',
        'mock_community.json',
        'mock_reviews.json',
    ]
    all_items = []
    for fname in mock_files:
        path = RAW / fname
        if path.exists():
            with open(path) as f:
                items = json.load(f)
                all_items.extend(items if isinstance(items, list) else [items])
                print(f"Loaded {len(items)} items from {fname}")
        else:
            print(f"Warning: {fname} not found — skipping")
    return all_items


def run():
    github_items = fetch_github_issues()
    mock_items   = load_mock_data()
    all_items    = github_items + mock_items

    # Write combined raw GitHub issues file
    if github_items:
        with open(RAW / 'github_issues.json', 'w') as f:
            json.dump(github_items, f, indent=2)

    print(f"Total raw items ready for classification: {len(all_items)}")


if __name__ == '__main__':
    run()
```

### Code: `scripts/generate_dashboard.py`

```python
"""
Reads data/processed/feedback_summary.json and feedback_classified.json,
injects live data into dashboard/index.html template.

For the demo, the dashboard HTML is self-contained with embedded JS data.
This script updates the data blob inside index.html.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parent.parent
PROC = BASE / 'data' / 'processed'
DASH = BASE / 'dashboard' / 'index.html'

def run():
    # Load processed data
    summary_path = PROC / 'feedback_summary.json'
    classified_path = PROC / 'feedback_classified.json'

    if not summary_path.exists():
        print("No summary data found — run classify_feedback.py first")
        return

    with open(summary_path) as f:
        summary = json.load(f)
    with open(classified_path) as f:
        classified = json.load(f)

    # Build the data payload that will be injected into the HTML
    totals = summary.get('totals', {})
    clusters = summary.get('top_clusters', [])[:6]
    recent_items = sorted(
        classified, key=lambda x: x.get('timestamp', ''), reverse=True
    )[:12]

    data_blob = {
        'generated_at': summary.get('generated_at', ''),
        'totals': totals,
        'by_source': summary.get('by_source', {}),
        'clusters': clusters,
        'recent': recent_items,
    }

    # Read current dashboard HTML
    html = DASH.read_text()

    # Inject timestamp into header
    ts = datetime.now(timezone.utc).strftime('%b %-d, %Y · %H:%M UTC')
    html = re.sub(
        r'Last refreshed:.*?UTC',
        f'Last refreshed: {ts}',
        html
    )

    # Inject data blob (between markers)
    marker_start = '/* DATA_START */'
    marker_end   = '/* DATA_END */'
    data_js = f"{marker_start}\nconst LIVE_DATA = {json.dumps(data_blob, indent=2)};\n{marker_end}"

    if marker_start in html:
        html = re.sub(
            rf'{re.escape(marker_start)}.*?{re.escape(marker_end)}',
            data_js,
            html,
            flags=re.DOTALL
        )
    else:
        # First run: append before closing </script>
        html = html.replace('</script>\n</body>', f'{data_js}\n</script>\n</body>')

    DASH.write_text(html)
    print(f"Dashboard updated: {DASH}")
    print(f"Totals: {totals}")


if __name__ == '__main__':
    run()
```

### Phase 4 Verification Checklist

```
[ ] 4.1  scripts/fetch_feedback.py exists and runs without errors
[ ] 4.2  After running fetch_feedback.py, data/raw/github_issues.json is updated
[ ] 4.3  scripts/generate_dashboard.py exists and runs without errors
[ ] 4.4  After running generate_dashboard.py, dashboard/index.html timestamp is updated
[ ] 4.5  Full pipeline test: python3 scripts/fetch_feedback.py &&
                             python3 scripts/classify_feedback.py &&
                             python3 scripts/generate_dashboard.py
         → runs end-to-end without errors
[ ] 4.6  Open dashboard/index.html in browser — charts render with data

Phase 4 PASS if all 6 boxes checked.
```

---

## Phase 5 — GitHub Actions Automation

This phase makes the dashboard refresh itself every day at 09:00 UTC with no manual effort.

### Tasks

**5.1** Add GitHub PAT as a repository secret
**5.2** Write `.github/workflows/daily_refresh.yml`
**5.3** Test the workflow manually
**5.4** Verify the commit appears in the repo and Pages URL updates

### Step-by-step: Adding the secret

1. Go to: https://github.com/shayalpatel/CustomerFeedback/settings/secrets/actions
2. Click **New repository secret**
3. Name: `PERSONAL_TOKEN`
4. Secret: paste your PAT (the one generated in Phase 0)
5. Click **Add secret**

### Code: `.github/workflows/daily_refresh.yml`

```yaml
name: Daily Feedback Refresh

on:
  schedule:
    # Runs every day at 09:00 UTC
    - cron: '0 9 * * *'
  workflow_dispatch:
    # Also allows manual trigger from GitHub Actions tab

jobs:
  refresh:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.PERSONAL_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Fetch feedback data
        run: python scripts/fetch_feedback.py

      - name: Classify feedback
        run: python scripts/classify_feedback.py

      - name: Regenerate dashboard
        run: python scripts/generate_dashboard.py

      - name: Commit and push updated files
        run: |
          git config user.name  "CustomerFeedback Bot"
          git config user.email "bot@users.noreply.github.com"
          git add data/processed/ dashboard/index.html
          git diff --staged --quiet || git commit -m "chore: auto-refresh feedback $(date '+%Y-%m-%d')"
          git push
```

### How to test the workflow manually

1. Go to: https://github.com/shayalpatel/CustomerFeedback/actions
2. Click **Daily Feedback Refresh** in the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Watch the run — each step should show a green checkmark
5. After it finishes, check the repo's commit history — you should see a new commit from "CustomerFeedback Bot"
6. Visit https://shayalpatel.github.io/CustomerFeedback — the timestamp should update

### Phase 5 Verification Checklist

```
[ ] 5.1  PERSONAL_TOKEN secret added to repo settings
[ ] 5.2  .github/workflows/daily_refresh.yml committed and pushed
[ ] 5.3  Manual workflow trigger ran without errors (all steps green)
[ ] 5.4  New commit from "CustomerFeedback Bot" appears in commit history
[ ] 5.5  Dashboard URL timestamp updated after workflow run
[ ] 5.6  data/processed/ files have new timestamps in the repo
[ ] 5.7  Wait 24h and verify the scheduled run fires automatically at 09:00 UTC

Phase 5 PASS if boxes 5.1–5.6 checked. Box 5.7 verified next day.
```

---

## Master Todo List

Copy this checklist and track progress as you complete each phase.

```
══════════════════════════════════════════════════════════════
  PHASE 0 — Repository & GitHub Pages
══════════════════════════════════════════════════════════════
[ ] 0.1  Create github.com/shayalpatel/CustomerFeedback (Public)
[ ] 0.2  Generate PAT with 'repo' scope, save it securely
[ ] 0.3  git init + git push (initial files to main branch)
[ ] 0.4  Enable GitHub Pages (Settings → Pages → main / root)
[ ] 0.5  Configure GitHub MCP in Claude Code settings
[ ] 0.6  Verify URL: https://shayalpatel.github.io/CustomerFeedback
──── Phase 0 sign-off: URL loads, dashboard fully interactive ────

══════════════════════════════════════════════════════════════
  PHASE 1 — Data Foundation
══════════════════════════════════════════════════════════════
[ ] 1.1  Create data/raw/github_issues.json      (≥15 mock items)
[ ] 1.2  Create data/raw/mock_surveys.json        (≥10 items)
[ ] 1.3  Create data/raw/mock_support_tickets.json(≥8 items)
[ ] 1.4  Create data/raw/mock_in_app.json         (≥8 items)
[ ] 1.5  Create data/raw/mock_community.json      (≥10 items)
[ ] 1.6  Create data/raw/mock_reviews.json        (≥6 items)
[ ] 1.7  All raw items follow the Raw Item Schema
[ ] 1.8  data/processed/ directory ready
[ ] 1.9  data/README.md updated to describe all files
──── Phase 1 sign-off: all JSON valid, schemas correct ────

══════════════════════════════════════════════════════════════
  PHASE 2 — Smart Classification Script
══════════════════════════════════════════════════════════════
[ ] 2.1  Create scripts/classify_feedback.py
[ ] 2.2  SmartFeedbackClassifier class implemented
[ ] 2.3  Source-aware Bayesian priors working
[ ] 2.4  Negation detection working
[ ] 2.5  Product area detection working (14 areas)
[ ] 2.6  Urgency and sentiment scoring working
[ ] 2.7  SimpleClustering (TF-IDF) implemented
[ ] 2.8  Pipeline runner (run() function) writes all 4 output files
[ ] 2.9  python3 scripts/classify_feedback.py passes spot-check
──── Phase 2 sign-off: classification accuracy spot-check ≥80% ────

══════════════════════════════════════════════════════════════
  PHASE 3 — Claude Code Skill
══════════════════════════════════════════════════════════════
[ ] 3.1  Create .claude/skills/refresh-feedback.md
[ ] 3.2  Update CLAUDE.md with trigger + post-run Q&A instructions
[ ] 3.3  "Refresh the feedback page" → skill loads and runs
[ ] 3.4  All 8 skill steps complete successfully
[ ] 3.5  data/processed/ files updated after skill run
[ ] 3.6  git push succeeds from within the skill
[ ] 3.7  Follow-up Q&A: sidebar UX question answered from data
[ ] 3.8  Follow-up Q&A: critical bug question answered from data
──── Phase 3 sign-off: full conversational loop working ────

══════════════════════════════════════════════════════════════
  PHASE 4 — Pipeline Scripts
══════════════════════════════════════════════════════════════
[ ] 4.1  Create scripts/fetch_feedback.py
[ ] 4.2  fetch_feedback.py pulls real VS Code GitHub Issues
[ ] 4.3  Create scripts/generate_dashboard.py
[ ] 4.4  generate_dashboard.py updates HTML timestamp correctly
[ ] 4.5  Full pipeline (fetch → classify → generate) runs end-to-end
[ ] 4.6  Dashboard opens in browser with updated data
──── Phase 4 sign-off: end-to-end pipeline runs locally ────

══════════════════════════════════════════════════════════════
  PHASE 5 — GitHub Actions Automation
══════════════════════════════════════════════════════════════
[ ] 5.1  PERSONAL_TOKEN secret added to repo
[ ] 5.2  .github/workflows/daily_refresh.yml created and pushed
[ ] 5.3  Manual workflow run: all steps green
[ ] 5.4  Bot commit appears in repo history
[ ] 5.5  Dashboard URL timestamp updated after workflow
[ ] 5.6  data/processed/ files committed by bot
[ ] 5.7  (Next day) Scheduled run fires automatically at 09:00 UTC
──── Phase 5 sign-off: full automation confirmed ────

══════════════════════════════════════════════════════════════
  PROJECT COMPLETE ✓
  Live URL: https://shayalpatel.github.io/CustomerFeedback
══════════════════════════════════════════════════════════════
```

---

*Plan version: 1.0 — May 5, 2026*
*Do not begin Phase 0 until you have answers to: repo name confirmed (CustomerFeedback ✓), GitHub username confirmed (shayalpatel ✓), classification strategy confirmed (smart script + Claude skill ✓)*
