import os
import re
import json
import time
from datetime import datetime, timezone
import urllib.request
import urllib.error

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Search Seeds spanning modern open source workloads
SEEDS = [
    "llm inference", "multi-agent", "rag", "vector database",
    "stable-diffusion comfyui", "whisper tts voice", "vlm ocr",
    "pkm second-brain", "local-first crdt", "cli tui tool"
]

def fetch_json(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "DevRadar-Engine/2.0")
    req.add_header("Accept", "application/vnd.github+json")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def extract_capabilities(repo, readme_text=""):
    text = f"{repo.get('name', '')} {repo.get('description', '')} {' '.join(repo.get('topics', []))} {readme_text}".lower()
    
    # Interaction Pattern
    interaction = []
    if any(k in text for k in ["cli", "terminal", "command line", "tui"]):
        interaction.append("cli")
    if any(k in text for k in ["sdk", "library", "python package", "pip", "npm package"]):
        interaction.append("library")
    if any(k in text for k in ["docker", "server", "rest api", "http service", "daemon", "service"]):
        interaction.append("service")
    if any(k in text for k in ["desktop", "electron", "tauri", "gui", "tray"]):
        interaction.append("desktop")
    if not interaction:
        interaction = ["library"]

    # Integration & Standards
    integrations = []
    if any(k in text for k in ["openai-compatible", "openai api", "v1/chat/completions"]):
        integrations.append("openai-api")
    if any(k in text for k in ["mcp", "model context protocol"]):
        integrations.append("mcp-server")
    if any(k in text for k in ["langchain", "llamaindex"]):
        integrations.append("orchestrators")
    if any(k in text for k in ["crdt", "automerge", "yjs", "sync"]):
        integrations.append("crdt-sync")
    if not integrations:
        integrations = ["standalone"]

    # Deployment Model
    deployment = []
    if any(k in text for k in ["local-first", "offline", "zero cloud", "on-device"]):
        deployment.append("local-only")
    if any(k in text for k in ["docker", "container", "docker-compose"]):
        deployment.append("docker")
    if any(k in text for k in ["cloud", "saas", "api key", "byok"]):
        deployment.append("byok-cloud")
    if not deployment:
        deployment = ["local-only"]

    # Intent Tags
    intent_tags = []
    if "drop-in" in text or "alternative" in text or "replace" in text:
        intent_tags.append("drop-in-replacement")
    if "self-host" in text or "self hosted" in text:
        intent_tags.append("self-hosted")
    if "streaming" in text or "real-time" in text:
        intent_tags.append("real-time")
    if "cpu" in text and not "requires gpu" in text:
        intent_tags.append("runs-on-cpu")
    if "fine-tun" in text:
        intent_tags.append("fine-tuning")

    # Hardware Floor
    has_cuda = any(k in text for k in ["cuda", "nvidia", "rtx", "vram", "tensorrt"])
    cpu_friendly = any(k in text for k in ["cpu", "gguf", "llama.cpp", "onnx", "wasm", "apple silicon", "metal"])
    
    hardware = {
        "is_cuda_ready": has_cuda,
        "cpu_supported": cpu_friendly or not has_cuda,
        "floor": "16GB+ CUDA VRAM" if (has_cuda and not cpu_friendly) else ("8GB Unified / Metal" if cpu_friendly else "Minimal CPU")
    }

    return {
        "interaction": interaction,
        "integrations": integrations,
        "deployment": deployment,
        "intent_tags": intent_tags,
        "hardware": hardware
    }

def analyze_health(repo):
    pushed_at = repo.get("pushed_at") or repo.get("updated_at")
    created_at = repo.get("created_at")
    now = datetime.now(timezone.utc)
    
    last_push_days = 999
    if pushed_at:
        dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        last_push_days = max(0, int((now - dt).total_seconds() / 86400))

    age_days = 100
    if created_at:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        age_days = max(1, int((now - dt).total_seconds() / 86400))

    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    open_issues = repo.get("open_issues_count", 0)

    # Readiness Tagging Heuristic
    if last_push_days > 90:
        stage = "maintenance"
    elif age_days < 60 and stars < 500:
        stage = "experimental"
    elif stars > 3000 and last_push_days <= 14:
        stage = "mature"
    else:
        stage = "active"

    # Authenticity: Fork/Star balance check
    fork_ratio = (forks / stars) if stars > 0 else 0.05
    authenticity = 95
    if fork_ratio < 0.015 and stars > 500:
        authenticity = 65
    elif fork_ratio < 0.03:
        authenticity = 80

    return {
        "stage": stage,
        "last_push_days": last_push_days,
        "age_days": age_days,
        "authenticity_score": authenticity,
        "open_issues": open_issues,
        "is_stale": last_push_days > 90
    }

def run_pipeline():
    os.makedirs("data", exist_ok=True)
    history_file = os.path.join("data", "history.json")
    history = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {}

    all_repos = {}
    print("Collecting high-signal open-source repositories...")
    
    for seed in SEEDS:
        query = f"{seed} stars:>100"
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=updated&order=desc&per_page=15"
        res = fetch_json(url)
        if not res or "items" not in res:
            continue
        
        for item in res["items"]:
            full_name = item["full_name"]
            if full_name not in all_repos:
                all_repos[full_name] = item
        time.sleep(0.8)

    print(f"Aggregated {len(all_repos)} unique candidate repositories. Analyzing intents and health...")

    processed = []
    now_ts = int(time.time())

    for full_name, repo in all_repos.items():
        stars = repo.get("stargazers_count", 0)
        
        # Velocity Tracking (24h)
        repo_history = history.get(full_name, [])
        v24 = 0
        if repo_history:
            # Filter entries older than 20 hours
            day_old = [h for h in repo_history if (now_ts - h.get("ts", 0)) >= 72000]
            if day_old:
                v24 = max(0, stars - day_old[-1].get("stars", stars))
            else:
                v24 = max(0, stars - repo_history[0].get("stars", stars))

        # Append snapshot (keeping last 14 days)
        repo_history.append({"ts": now_ts, "stars": stars})
        history[full_name] = repo_history[-14:]

        capabilities = extract_capabilities(repo)
        health = analyze_health(repo)

        # Quick run construction
        lang = (repo.get("language") or "").lower()
        if lang == "python":
            quick_run = f"pip install {repo.get('name')}"
        elif lang in ["typescript", "javascript"]:
            quick_run = f"npm install {repo.get('name')}"
        elif lang == "rust":
            quick_run = f"cargo install {repo.get('name')}"
        elif "docker" in capabilities["deployment"]:
            quick_run = f"docker run -d {repo.get('name')}"
        else:
            quick_run = f"git clone {repo.get('html_url')}"

        processed.append({
            "full_name": full_name,
            "name": repo.get("name"),
            "url": repo.get("html_url"),
            "description": repo.get("description"),
            "language": repo.get("language") or "Code",
            "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else "MIT",
            "stars": stars,
            "stars_24h": v24,
            "trending_score": v24 * 3 + int(stars ** 0.5),
            "topics": repo.get("topics", []),
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("pushed_at"),
            "quick_run": quick_run,
            "hardware_req": capabilities["hardware"]["floor"],
            "is_cuda_ready": capabilities["hardware"]["is_cuda_ready"],
            "is_local_first": "local-only" in capabilities["deployment"],
            "authenticity_score": health["authenticity_score"],
            "star_history": history[full_name],
            "capabilities": capabilities,
            "health": health
        })

    # Save outputs
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_repositories": len(processed),
        "repositories": processed
    }

    with open(os.path.join("data", "repos.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Saved {len(processed)} enriched repositories to data/repos.json")

if __name__ == "__main__":
    run_pipeline()
