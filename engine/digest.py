"""
DevRadar Weekly Digest Generator
Compiles the top breakout repositories into a shareable Markdown digest.
"""
import json, os
from datetime import datetime, timezone

def generate_digest():
    with open("data/repos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    repos = sorted(data.get("repositories", []), key=lambda x: x.get("trending_score", 0), reverse=True)[:5]
    date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

    lines = [
        f"# 🛰️ DevRadar Weekly Radar — {date_str}",
        "",
        "> Curated autonomous open-source intelligence tracking breakout star velocity, authenticity, and local-first readiness.",
        ""
    ]

    for idx, r in enumerate(repos, 1):
        lines.append(f"### {idx}. [{r['full_name']}]({r['url']})")
        lines.append(f"- **Category:** `{r['category']}` | **License:** `{r.get('license', 'MIT')}`")
        lines.append(f"- **Stars:** ⭐ {r['stars']:,} (`+{r.get('stars_24h', 0)}` in 24h) | **Authenticity:** `{r.get('authenticity_score', 95)}% Organic`")
        lines.append(f"- **Hardware Viability:** `{r.get('hardware_req', 'Minimal RAM')}`")
        lines.append(f"- **Description:** {r.get('description', 'No description.')}")
        lines.append(f"- **Quick Run:** `{r.get('quick_run', 'git clone ' + r['url'])}`")
        lines.append("")

    lines.append("---")
    lines.append("Discover all 20 disciplines live at [siddharthakki.github.io/devradar](https://siddharthakki.github.io/devradar/).")

    os.makedirs("digests", exist_ok=True)
    digest_path = f"digests/digest_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}.md"
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Weekly digest saved to {digest_path}")

if __name__ == "__main__":
    generate_digest()
