"""
DevRadar Weekly Digest Generator
Compiles the top breakout repositories into a shareable Markdown digest.
"""
import json, os
from datetime import datetime, timezone

def generate_digest():
    with open("data/repos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    repos = sorted(data.get("repositories", []), key=lambda x: x.get("stars_24h", 0), reverse=True)[:5]
    date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

    lines = [
        f"# ⚡ StackFit Weekly Radar — {date_str}",
        "",
        "> 5 breakout open-source repos that spiked this week, what they replace, and what they run on.",
        ""
    ]

    for idx, r in enumerate(repos, 1):
        lines.append(f"### {idx}. [{r['full_name']}]({r['url']}) `[{r.get('signal_badge', 'climber').upper()}]`")
        lines.append(f"**Verdict:** {r.get('verdict', '')}")
        lines.append(f"- **What it is:** {r.get('description', 'No description.')}")
        lines.append(f"- **What it replaces:** `{r.get('replaces', 'Incumbents')}`")
        lines.append(f"- **Why this week:** {r.get('why_this_week', 'High momentum on GitHub Trending.')}")
        lines.append(f"- **Hardware Viability:** `{r.get('hardware_alert', r.get('hardware_req', 'Minimal CPU'))}`")
        lines.append(f"- **Stars & Momentum:** ⭐ {r['stars']:,} (`+{r.get('stars_24h', 0)}` in 24h) | {r.get('contributors_count', 20)} contributors")
        lines.append(f"- **Quick Run:** `{r.get('quick_run', 'git clone ' + r['url'])}`")
        lines.append("")

    lines.append("---")
    lines.append("Explore live interactive stacks & recommendations at [siddharthakki.github.io/stackfit](https://siddharthakki.github.io/stackfit/).")

    os.makedirs("digests", exist_ok=True)
    digest_path = f"digests/digest_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}.md"
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Weekly digest saved to {digest_path}")

if __name__ == "__main__":
    generate_digest()
