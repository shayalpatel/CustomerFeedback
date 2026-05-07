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
