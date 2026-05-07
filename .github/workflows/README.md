# /.github/workflows

GitHub Actions automation files.

## Files

### daily_refresh.yml  (created during build phase)
Runs once per day at 09:00 UTC automatically.
Steps:
  1. Fetch latest VS Code GitHub Issues → data/raw/
  2. Run Claude classification → data/processed/
  3. Regenerate dashboard/index.html
  4. Commit and push → GitHub Pages serves the updated dashboard
