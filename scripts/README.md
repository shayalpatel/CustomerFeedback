# /scripts

Python scripts that power the feedback pipeline.

## Files

### generate_dashboard.py
Reads `data/processed/feedback_summary.json` and `data/processed/clusters.json`
and writes a fresh `dashboard/index.html`.

Run manually:  python scripts/generate_dashboard.py
Run by:        the Claude skill AND the GitHub Actions daily workflow

### fetch_feedback.py  (created during build phase)
Fetches raw feedback from each source and writes to `data/raw/`.
Sources: VS Code GitHub Issues API (free/public), mock data generator.

### classify_feedback.py  (created during build phase)
Reads `data/raw/`, sends each item to Claude API for classification,
writes results to `data/processed/feedback_classified.json`.
