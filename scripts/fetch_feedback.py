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
