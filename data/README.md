# /data

This folder holds all feedback data at every stage of the pipeline.

## Subfolders

### /raw
Raw feedback exactly as fetched from each source — never edited.
One JSON file per source, overwritten on each daily run.

Files created here:
- `github_issues.json`       — pulled from microsoft/vscode GitHub Issues (public, free)
- `mock_surveys.json`        — synthetic survey responses (for demo)
- `mock_support_tickets.json`— synthetic support tickets (for demo)

### /processed
Output produced by the Claude AI classification agent.
These files are read by the dashboard and by Claude for follow-up Q&A.

Files created here:
- `feedback_classified.json` — every item with: category, sub_category, sentiment, urgency, summary
- `feedback_summary.json`    — aggregated stats + top clusters (what Claude reads for Q&A)
- `clusters.json`            — grouped similar items with volume + trend data

### /archive
Previous daily runs are moved here for trend tracking over time.
Format: `YYYY-MM-DD_feedback_summary.json`
