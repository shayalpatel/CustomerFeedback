# /.claude/skills

Claude Code skill files for this project.

## Files

### refresh-feedback.md
The conversational skill. Triggered when you say something like
"Refresh the feedback page" in Claude Code.

What it does:
  1. Fetches latest VS Code GitHub Issues
  2. Classifies each item (Bug / Feature Request / UX Issue)
  3. Updates data/processed/ files
  4. Regenerates dashboard/index.html
  5. Pushes to GitHub → public URL updates
  6. Loads feedback_summary.json into context for follow-up Q&A
