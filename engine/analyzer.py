import os, re, json, time
from datetime import datetime, timezone, timedelta
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Accept": "application/vnd.github.v3+json", "User-Agent": "devradar-engine"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

DATA_FILE = "data/repos.json"

TAXONOMY = {
    "Local AI & Inference": ["llm", "inference", "gguf", "vllm", "ollama", "transformers", "local-ai", "quantization", "cuda"],
    "Autonomous Agents": ["agent", "agents", "rag", "langchain", "autogen", "crewai", "workflow"],
    "Developer Tooling & CLI": ["cli", "terminal", "debugger", "compiler", "linter", "devtools"],
    "Systems & Infrastructure": ["kubernetes", "k8s", "docker", "rust", "database", "distributed", "storage", "wasm"],
    "Local-First & Sovereign Apps": ["offline-first", "local-first", "sqlite", "desktop", "tauri", "electron"],
    "Security & Reverse Eng": ["security", "cve", "pentest", "vulnerability", "auth", "exploit"]
}

def classify(desc, topics):
    text = f"{desc or ''} {' '.join(topics or [])}".lower()
    scores = {cat: sum(1 for kw in kws if kw in text) for cat, kws in TAXONOMY.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Core Utilities"

def profile_specs(desc, topics):
    text = f"{desc or ''} {' '.join(topics or [])}".lower()
    vram = "CPU / Minimal RAM"
    if any(k in text for k in ["24gb", "3090", "4090", "a100", "70b"]):
        vram = "Heavy (16–24GB+ VRAM)"
    elif any(k in text for k in ["cuda", "vram", "gpu", "8b", "14b"]):
        vram = "Moderate (8–16GB VRAM)"
    elif any(k in text for k in ["metal", "apple silicon", "mlx"]):
        vram = "Apple Silicon (Unified)"
    
    is_local = any(k in text for k in ["local", "offline", "self-hosted", "zero-cloud", "private", "sqlite"])
    return {"hardware_req": vram, "is_local_first": is_local, "is_cuda_ready": "cuda" in text or "gpu" in text}

def extract_readme_metadata(full_name, default_branch="main"):
    image_url = None
    quick_run = f"git clone https://github.com/{full_name}.git"

    for branch in [default_branch, "master", "main"]:
        url = f"https://raw.githubusercontent.com/{full_name}/{branch}/README.md"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                text = r.text

                # Match Markdown images: ![alt](target) and HTML images: <img src="target">
                md_targets = re.findall(r'!\[.*?\]\(([^ \)]+)', text)
                html_targets = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.IGNORECASE)
                candidates = md_targets + html_targets

                badge_filters = ["shields.io", "badge.svg", "actions/workflows", "codecov", "travis-ci", "github-readme-stats", "licence", "license"]

                for src in candidates:
                    src = src.strip().strip('"').strip("'")
                    if any(b in src.lower() for b in badge_filters):
                        continue

                    # GitHub user-attachments CDN links
                    if "github.com/user-attachments/assets" in src or "raw.githubusercontent.com" in src:
                        image_url = src
                        break

                    # External image URLs
                    if src.startswith("http://") or src.startswith("https://"):
                        if any(src.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]):
                            image_url = src
                            break

                    # Relative asset paths inside the repo (e.g. assets/preview.png, ./screenshot.jpg)
                    clean_rel = src.lstrip("./").lstrip("/")
                    if any(clean_rel.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]):
                        image_url = f"https://raw.githubusercontent.com/{full_name}/{branch}/{clean_rel}"
                        break

                cmd_match = re.search(r'```(?:bash|sh|shell)?\s*(docker run[^\n`]+|pip install[^\n`]+|npm (?:i|install)[^\n`]+|cargo install[^\n`]+)\s*```', text, re.IGNORECASE)
                if cmd_match:
                    quick_run = cmd_match.group(1).strip()

                break
        except Exception:
            pass

    return image_url, quick_run

def fetch_repos(query):
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=50"
    res = requests.get(url, headers=HEADERS, timeout=15)
    return res.json().get("items", []) if res.status_code == 200 else []

def run():
    os.makedirs("data", exist_ok=True)
    existing = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing = {r["id"]: r for r in json.load(f).get("repositories", [])}
        except Exception:
            pass

    now = datetime.now(timezone.utc)
    month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    raw = {r["id"]: r for r in fetch_repos(f"created:>{month_ago}+stars:>10")}

    processed = []
    now_ts = int(now.timestamp())
    for r_id, r in raw.items():
        prev = existing.get(r_id, {})
        stars = r["stargazers_count"]
        forks = r.get("forks_count", 0)

        history = prev.get("star_history", [])
        history.append({"ts": now_ts, "stars": stars})
        history = [h for h in history if h["ts"] >= now_ts - 7 * 86400]

        day_ago = now_ts - 86400
        pts = [h["stars"] for h in history if h["ts"] <= day_ago]
        delta_24h = max(0, stars - (pts[-1] if pts else history[0]["stars"]))

        created = datetime.strptime(r["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age_h = max(1.0, (now - created).total_seconds() / 3600.0)
        score = round(stars / ((age_h + 2.0) ** 1.25), 4)

        topics = r.get("topics", [])
        specs = profile_specs(r.get("description"), topics)
        auth = 95 if stars < 20 else max(20, min(99, int(100 - (30 if forks / max(1, stars) < 0.03 else 0))))

        # Force re-extract if image was missing
        img_url = prev.get("image_url")
        quick_run = prev.get("quick_run")
        if not img_url:
            img_url, quick_run = extract_readme_metadata(r["full_name"], r.get("default_branch", "main"))

        license_info = r.get("license") or {}
        license_spdx = license_info.get("spdx_id") or "Custom"

        processed.append({
            "id": r["id"], "name": r["name"], "full_name": r["full_name"], "url": r["html_url"],
            "description": r.get("description") or "No description provided.",
            "language": r.get("language") or "Unspecified",
            "license": license_spdx,
            "pushed_at": r.get("pushed_at"),
            "category": classify(r.get("description"), topics),
            "stars": stars, "stars_24h": delta_24h, "created_at": r["created_at"],
            "trending_score": score, "hardware_req": specs["hardware_req"],
            "is_local_first": specs["is_local_first"], "is_cuda_ready": specs["is_cuda_ready"],
            "authenticity_score": auth, "star_history": history,
            "image_url": img_url,
            "quick_run": quick_run
        })

    processed.sort(key=lambda x: x["trending_score"], reverse=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"updated_at": now.isoformat(), "repositories": processed}, f, indent=2)

if __name__ == "__main__":
    run()
