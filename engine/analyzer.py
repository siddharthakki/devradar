import os
import re
import json
import time
import urllib.parse
from datetime import datetime, timezone
import urllib.request
import urllib.error

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

SEEDS = [
    "llm inference", "multi-agent", "rag", "vector database",
    "stable-diffusion comfyui", "whisper tts voice", "vlm ocr",
    "pkm second-brain", "local-first crdt", "cli tui tool"
]

TAXONOMY = {
    "Local LLM Engines": ["llm", "inference", "gguf", "vllm", "ollama", "transformers", "local-ai", "quantization", "llama.cpp", "exllamav2", "mistral"],
    "Multi-Agent Frameworks": ["agent", "agents", "autogen", "crewai", "langgraph", "swarm", "pydantic-ai", "multi-agent", "smolagents"],
    "RAG Engines": ["rag", "retrieval", "langchain", "llamaindex", "hybrid-search", "semantic-search", "haystack", "chunking"],
    "Vector Databases": ["vector-database", "vectordb", "chroma", "qdrant", "milvus", "weaviate", "pinecone", "pgvector", "embeddings"],
    "Generative Image/Video": ["stable-diffusion", "comfyui", "flux", "diffusion", "image-generation", "video-generation", "text-to-video", "sdxl"],
    "Audio & Voice Synthesis": ["tts", "stt", "whisper", "speech-to-text", "text-to-speech", "voice-clone", "audio", "bark", "musicgen"],
    "Vision & OCR": ["ocr", "vision-language", "vlm", "yolo", "segmentation", "paddleocr", "document-ai", "surya"],
    "Creative Media & Design": ["canvas", "photo-editor", "video-editor", "canvas-ui", "3d-engine", "animation", "generative-art"],
    "Second Brain & PKM": ["second-brain", "pkm", "obsidian", "note-taking", "knowledge-base", "logseq", "zettelkasten"],
    "AI Writing & Synthesis": ["writing-assistant", "summarization", "copilot", "text-generation", "grammar", "autocomplete"],
    "Document Vaults & Search": ["vault", "paperless", "pdf", "full-text-search", "document-management", "archive", "knowledge-graph"],
    "Spreadsheets & Data Grid": ["spreadsheet", "data-grid", "excel", "sheets", "csv", "table", "data-table"],
    "CLI & TUI Tooling": ["cli", "tui", "terminal", "command-line", "interactive-cli", "prompt", "repl"],
    "Local-First Sync & CRDTs": ["local-first", "crdt", "offline-first", "peer-to-peer", "p2p", "automerge", "yjs", "sync-engine"],
    "Container & MicroVMs": ["docker", "container", "microvm", "firecracker", "podman", "orchestration", "wasm"],
    "Reverse Eng & Security": ["security", "reverse-engineering", "decompiler", "disassembler", "cve", "pentest", "vulnerability", "exploit"],
    "Embedded & Edge AI": ["edge-ai", "embedded", "tinygrad", "microcontroller", "esp32", "robotics", "tensorrt-edge"],
    "Desktop & Native Bridges": ["tauri", "electron", "flutter-desktop", "native-ui", "tray-app", "systray"],
    "Databases & Storage": ["sqlite", "duckdb", "embedded-database", "storage-engine", "key-value", "cache", "rocksdb"],
    "API & Gateway Proxies": ["api-gateway", "reverse-proxy", "mcp", "model-context-protocol", "rpc", "grpc", "proxy"]
}

def classify(desc="", topics=None, name=""):
    """Classifies a repository into one of the 20 DevRadar categories."""
    topics = topics or []
    text = f"{name or ''} {desc or ''} {' '.join(topics)}".lower()
    scores = {cat: sum(1 for kw in kws if kw in text) for cat, kws in TAXONOMY.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "CLI & TUI Tooling"

def profile_specs(desc="", topics=None):
    """Profiles hardware viability and local-first status for tests and capabilities."""
    topics = topics or []
    text = f"{desc or ''} {' '.join(topics)}".lower()
    has_cuda = any(k in text for k in ["cuda", "nvidia", "rtx", "vram", "tensorrt"])
    cpu_friendly = any(k in text for k in ["cpu", "gguf", "llama.cpp", "onnx", "wasm", "apple silicon", "metal"])
    heavy_cuda = any(k in text for k in ["24gb", "3090", "4090", "a100", "h100", "70b"])

    if heavy_cuda or (has_cuda and any(k in text for k in ["3090", "4090", "24gb"])):
        floor = "24GB+ CUDA VRAM"
    elif has_cuda and not cpu_friendly:
        floor = "16GB+ CUDA VRAM"
    elif cpu_friendly:
        floor = "8GB Unified / Metal"
    else:
        floor = "Minimal CPU"

    is_local = any(k in text for k in ["local-first", "offline", "zero cloud", "on-device", "self-host", "sqlite", "private"])
    return {
        "hardware_req": floor,
        "is_local_first": is_local,
        "is_cuda_ready": has_cuda
    }

def fetch_json(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "DevRadar-Engine/2.0")
    req.add_header("Accept", "application/vnd.github+json")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error fetching {url}: {e.code} - {e.reason}")
        if e.code in (403, 429):
            reset_ts = e.headers.get("x-ratelimit-reset")
            if reset_ts:
                wait_time = max(0, int(reset_ts) - int(time.time())) + 2
                print(f"GitHub rate limit reached. Reset in {wait_time}s.")
        return None
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def normalize_history_entry(entry):
    """Safely converts legacy list/str snapshots into standardized dicts."""
    if isinstance(entry, dict):
        return {
            "ts": int(entry.get("ts", 0)),
            "stars": int(entry.get("stars", 0))
        }
    elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
        try:
            return {"ts": int(entry[0]), "stars": int(entry[1])}
        except (ValueError, TypeError):
            return None
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

    # Hardware Specs
    specs = profile_specs(f"{repo.get('name', '')} {repo.get('description', '')} {readme_text}", repo.get('topics', []))
    hardware = {
        "is_cuda_ready": specs["is_cuda_ready"],
        "cpu_supported": "Minimal CPU" in specs["hardware_req"] or "Unified" in specs["hardware_req"],
        "floor": specs["hardware_req"]
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
        try:
            dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            last_push_days = max(0, int((now - dt).total_seconds() / 86400))
        except Exception:
            last_push_days = 0

    age_days = 100
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age_days = max(1, int((now - dt).total_seconds() / 86400))
        except Exception:
            age_days = 30

    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    open_issues = repo.get("open_issues_count", 0)

    if last_push_days > 90:
        stage = "maintenance"
    elif age_days < 60 and stars < 500:
        stage = "experimental"
    elif stars > 3000 and last_push_days <= 14:
        stage = "mature"
    else:
        stage = "active"

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

KNOWN_COMPETITORS = {
    # Local LLMs & Inference
    "llama.cpp": ("Alternative to Ollama (Raw C/C++ inference runtime)", ["ollama", "vllm"]),
    "ollama": ("Alternative to LocalAI & LM Studio (CLI and REST inference engine)", ["localai", "lmstudio"]),
    "vllm": ("Alternative to TGI (High-throughput PagedAttention server)", ["tgi", "tensorrt-llm"]),
    "sglang": ("Alternative to vLLM (Fast structured decoding and spec decoding engine)", ["vllm", "tgi"]),
    "tgi": ("Alternative to vLLM (Hugging Face production LLM server)", ["vllm"]),
    "exllamav2": ("Alternative to llama.cpp (Ultra-fast EXL2 quantization for NVIDIA GPUs)", ["llama.cpp"]),
    "aphrodite-engine": ("Alternative to vLLM (Multi-backend sampling & inference engine)", ["vllm"]),
    "open-webui": ("Alternative to ChatGPT Web UI (Private interface for Ollama/vLLM)", ["chatgpt", "librechat"]),
    "librechat": ("Alternative to ChatGPT Plus (Multi-model enterprise AI web UI)", ["chatgpt"]),
    "tabby": ("Alternative to GitHub Copilot (Self-hosted AI coding assistant)", ["copilot"]),
    "continue": ("Alternative to GitHub Copilot (Open-source IDE copilot extension)", ["copilot"]),
    "jan": ("Alternative to proprietary desktop AI chat apps", ["chatgpt", "lmstudio"]),
    "localai": ("Alternative to OpenAI API (Drop-in REST API for local models)", ["openai"]),
    "litellm": ("Alternative to LangChain Model I/O (Unified 100+ LLM API proxy)", ["langchain", "openai"]),

    # Multi-Agent Frameworks
    "crewai": ("Alternative to AutoGen (Role-playing multi-agent orchestrator)", ["autogen", "langchain"]),
    "autogen": ("Alternative to LangGraph (Conversational multi-agent framework)", ["langgraph", "crewai"]),
    "langgraph": ("Alternative to CrewAI (Graph-based cyclical agent workflows)", ["crewai", "langchain"]),
    "dify": ("Alternative to Flowise / Langflow (Production LLM app development platform)", ["flowise", "langflow"]),
    "langflow": ("Alternative to Dify (Drag-and-drop visual agent builder)", ["dify"]),
    "flowise": ("Alternative to Dify (Drag-and-drop visual LLM workflows)", ["dify"]),
    "chatdev": ("Alternative to AutoGen (Virtual software development studio)", ["autogen"]),
    "openhands": ("Alternative to Devin (Autonomous software engineering agent)", ["devin"]),
    "swe-agent": ("Alternative to Devin (Autonomous benchmark-solving agent)", ["devin"]),
    "browser-use": ("Alternative to Selenium / Puppeteer (Autonomous AI web navigation)", ["selenium", "puppeteer"]),

    # Vector Databases & Search
    "chroma": ("Alternative to Pinecone & Weaviate (Embedded open-source vector store)", ["pinecone", "weaviate"]),
    "qdrant": ("Alternative to Milvus & Pinecone (Rust-based production vector search)", ["pinecone", "milvus"]),
    "milvus": ("Alternative to Pinecone (Cloud-native distributed vector database)", ["pinecone"]),
    "weaviate": ("Alternative to Pinecone (Modular GraphQL/REST vector database)", ["pinecone"]),
    "sqlite-vec": ("Alternative to pgvector (Zero-dependency embedded vector search)", ["pgvector", "chroma"]),
    "pgvector": ("Alternative to standalone vector DBs (PostgreSQL native vector search)", ["pinecone", "chroma"]),
    "ragflow": ("Alternative to Dify RAG (Deep document understanding retrieval engine)", ["dify", "langchain"]),

    # Local-First & Sync
    "electric": ("Alternative to Firebase & Supabase Realtime (SQLite sync layer)", ["firebase", "supabase"]),
    "powersync": ("Alternative to Firebase Realtime (PostgreSQL to SQLite offline sync)", ["firebase"]),
    "automerge": ("Alternative to Yjs (Binary CRDT library for collaborative apps)", ["yjs"]),
    "yjs": ("Alternative to Automerge (High-performance shared types CRDT framework)", ["automerge"]),
    "rxdb": ("Alternative to PouchDB / CouchDB (Reactive local-first client database)", ["pouchdb", "firebase"]),

    # Developer Tooling & CLI
    "ripgrep": ("Alternative to grep (High-velocity Rust recursive regex search)", ["grep"]),
    "fd": ("Alternative to find (Fast, user-friendly directory traverser in Rust)", ["find"]),
    "bat": ("Alternative to cat (Syntax-highlighted terminal pager)", ["cat"]),
    "lazygit": ("Alternative to GitKraken (Keyboard-driven terminal Git GUI)", ["gitkraken"]),
    "bruno": ("Alternative to Postman & Insomnia (Lightweight, local-only API client)", ["postman", "insomnia"]),
    "yaak": ("Alternative to Postman (Fast desktop REST/GraphQL client in Rust)", ["postman", "insomnia"]),
    "act": ("Alternative to pushing to GitHub (Run GitHub Actions locally in Docker)", ["github-actions"]),

    # Audio & Voice
    "whisper.cpp": ("Alternative to OpenAI Whisper API (Zero-cloud C++ speech transcription)", ["whisper", "openai"]),
    "piper": ("Alternative to ElevenLabs (Fast, local neural text-to-speech)", ["elevenlabs"]),
    "coqui-tts": ("Alternative to ElevenLabs (Self-hosted voice cloning & TTS)", ["elevenlabs"]),

    # Image & Video
    "comfyui": ("Alternative to Automatic1111 (Node-based modular Stable Diffusion workflow)", ["automatic1111"]),
    "fooocus": ("Alternative to Midjourney (One-click local image generation)", ["midjourney"])
}

CATEGORY_COMPETITORS = {
    "Local LLM Engines": ("Alternative to Ollama & vLLM (Self-hosted LLM runtime)", ["ollama", "vllm"]),
    "Multi-Agent Frameworks": ("Alternative to AutoGen & LangChain (Specialized agent coordinator)", ["autogen", "langchain"]),
    "RAG Engines": ("Alternative to LangChain RAG (Focused retrieval pipeline)", ["langchain", "llamaindex"]),
    "Vector Databases": ("Alternative to Pinecone (Self-hosted vector similarity search)", ["pinecone", "milvus"]),
    "Local-First Sync & CRDTs": ("Alternative to Firebase (Decentralized state synchronization)", ["firebase", "replicache"]),
    "Audio & Voice Synthesis": ("Alternative to ElevenLabs & Whisper API (On-device audio pipeline)", ["elevenlabs", "whisper"]),
    "Vision & OCR": ("Alternative to Cloud Vision APIs (Local neural OCR model)", ["google-vision", "aws-textract"]),
    "Document Vaults & Search": ("Alternative to Elastic / Notion (Private self-hosted search engine)", ["notion", "elastic"]),
    "CLI & TUI Tooling": ("Alternative to GUI Utilities (Keyboard-driven terminal tool)", ["gui"]),
    "Container & MicroVMs": ("Alternative to Docker Desktop (Lightweight isolation environment)", ["docker"]),
    "Second Brain & PKM": ("Alternative to Notion & Obsidian Sync (Local markdown knowledge vault)", ["notion", "obsidian"]),
    "Databases & Storage": ("Alternative to Cloud SQL (Embedded sovereign storage engine)", ["cloudsql", "sqlite"]),
    "Generative Image/Video": ("Alternative to Midjourney & proprietary diffusion APIs", ["midjourney"]),
    "AI Writing & Synthesis": ("Alternative to Notion AI & Copilot (Sovereign writing assistant)", ["copilot", "notion-ai"]),
    "Spreadsheets & Data Grid": ("Alternative to Google Sheets & Airtable (Local data grid)", ["airtable", "sheets"]),
    "Reverse Eng & Security": ("Alternative to IDA Pro & Burp Suite (Open security tooling)", ["burp-suite", "ida-pro"]),
    "Embedded & Edge AI": ("Alternative to JetPack & Cloud Edge APIs (Ultra-low footprint AI)", ["jetpack", "tensorrt"]),
    "Desktop & Native Bridges": ("Alternative to Electron (Lightweight native desktop runtime)", ["electron"]),
    "API & Gateway Proxies": ("Alternative to Kong & Cloudflare Workers (Private edge API proxy)", ["kong", "cloudflare"])
}

def generate_architectural_verdict(repo, category, capabilities, health):
    """Synthesizes a 1-sentence engineering verdict, gotchas, and competitor positioning."""
    hw = capabilities["hardware"]["floor"]
    stage = health["stage"]
    is_local = "local-only" in capabilities["deployment"]
    has_mcp = "mcp-server" in capabilities["integrations"]
    tags = capabilities["intent_tags"]
    name = (repo.get("name") or "").lower()

    # 1. Verdict
    if "24GB" in hw:
        verdict = "Heavyweight architecture engineered for large parameter weights with dedicated CUDA hardware."
    elif "Unified" in hw:
        verdict = "Optimized for Apple Silicon unified memory; ideal for local on-device inference."
    elif is_local and category == "Local LLM Engines":
        verdict = "Zero-cloud inference runner designed for private, offline execution."
    elif category == "Multi-Agent Frameworks" and has_mcp:
        verdict = "Modern agentic framework with Model Context Protocol (MCP) tool-calling integration."
    elif category == "Multi-Agent Frameworks":
        verdict = "Orchestration engine for multi-agent workflows and autonomous tool coordination."
    elif category == "RAG Engines":
        verdict = "Retrieval pipeline built for hybrid search and context-augmented generation."
    elif category == "Vector Databases":
        verdict = "High-performance vector storage optimized for similarity search and embedding retrieval."
    elif category == "Local-First Sync & CRDTs":
        verdict = "Decentralized state engine leveraging CRDT primitives for conflict-free peer synchronization."
    elif category == "CLI & TUI Tooling":
        verdict = "Keyboard-driven terminal utility built for fast, scriptable developer workflows."
    elif "drop-in-replacement" in tags:
        verdict = "Drop-in alternative providing compatible API surfaces with lower overhead."
    else:
        verdict = f"High-velocity open-source project delivering focused capabilities for {category.lower()}."

    # 2. Gotchas
    if "24GB" in hw:
        gotchas = "High VRAM requirement (24GB+ CUDA); cannot run on standard consumer laptops."
    elif "16GB" in hw:
        gotchas = "Requires dedicated NVIDIA GPU with 16GB+ VRAM for quantized execution."
    elif stage == "experimental":
        gotchas = "Fast-evolving experimental codebase (<60 days old); expect API surface shifts."
    elif stage == "maintenance":
        gotchas = "Maintenance mode (no commits in 90+ days); verify issue tracker before adopting."
    elif health["authenticity_score"] < 75:
        gotchas = "Unusual fork/star ratio anomaly detected; inspect commit log for organic activity."
    elif "byok-cloud" in capabilities["deployment"]:
        gotchas = "Cloud dependency or external API keys required; not fully self-contained offline."
    else:
        gotchas = ""

    # 3. Direct Competitor Comparison
    comparison = ""
    replaces = []
    for k, (comp_text, repl_list) in KNOWN_COMPETITORS.items():
        if k in name or name in k:
            comparison = comp_text
            replaces = repl_list
            break

    if not comparison:
        if category in CATEGORY_COMPETITORS:
            comparison, replaces = CATEGORY_COMPETITORS[category]
        else:
            comparison = "Alternative to Proprietary Cloud SaaS (Open-source sovereign tooling)"
            replaces = ["cloud-saas"]

    return verdict, gotchas, comparison, replaces

def enrich_with_ai(repo, category, capabilities, health, cache):
    """Enriches repo with Principal Engineer verdict, gotchas, and competitor comparison with persistent caching."""
    full_name = repo.get("full_name") or repo.get("name", "")

    # 1. Check persistent cache
    if full_name in cache and isinstance(cache[full_name], dict):
        cached = cache[full_name]
        if "verdict" in cached and "gotchas" in cached and "comparison" in cached and "replaces" in cached:
            return cached["verdict"], cached["gotchas"], cached["comparison"], cached["replaces"]

    # 2. Expert rule-based baseline
    verdict, gotchas, comparison, replaces = generate_architectural_verdict(repo, category, capabilities, health)

    # 3. If GEMINI_API_KEY or AI_API_KEY is available in environment, enrich via LLM
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("AI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            prompt = (
                f"You are a Principal Software Engineer and System Architect. Analyze this GitHub repository:\n"
                f"Name: {full_name}\n"
                f"Category: {category}\n"
                f"Description: {repo.get('description', '')}\n"
                f"Hardware floor: {capabilities.get('hardware', {}).get('floor', '')}\n"
                f"Tags: {capabilities.get('intent_tags', [])}\n"
                f"Deployment: {capabilities.get('deployment', [])}\n\n"
                f"Return ONLY valid JSON matching this schema:\n"
                f'{{"verdict": "blunt 1-sentence engineering assessment", '
                f'"gotchas": "realistic trade-off/hardware ceiling", '
                f'"comparison": "Alternative to [Incumbent] ([reason])", '
                f'"replaces": ["tool1", "tool2"]}}'
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                res_data = res.json()
                text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text)
                if parsed.get("verdict") and parsed.get("comparison"):
                    verdict = parsed["verdict"]
                    gotchas = parsed.get("gotchas", gotchas)
                    comparison = parsed["comparison"]
                    if isinstance(parsed.get("replaces"), list):
                        replaces = [str(x).lower() for x in parsed["replaces"]]
        except Exception:
            pass

    # Save to persistent cache
    cache[full_name] = {
        "verdict": verdict,
        "gotchas": gotchas,
        "comparison": comparison,
        "replaces": replaces
    }
    return verdict, gotchas, comparison, replaces

def atomic_save_json(filepath, data):
    """Atomically writes JSON using a temporary file to avoid corruption."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    tmp_path = f"{filepath}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, filepath)

def run_pipeline():
    os.makedirs("data", exist_ok=True)
    history_file = os.path.join("data", "history.json")
    raw_history = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                raw_history = json.load(f)
        except Exception:
            raw_history = {}

    # Normalize loaded history safely
    history = {}
    for key, entries in raw_history.items():
        if isinstance(entries, list):
            valid = [normalize_history_entry(e) for e in entries]
            history[key] = [v for v in valid if v is not None]

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

    ai_cache_file = os.path.join("data", "ai_verdicts.json")
    ai_cache = {}
    if os.path.exists(ai_cache_file):
        try:
            with open(ai_cache_file, "r", encoding="utf-8") as f:
                ai_cache = json.load(f)
        except Exception:
            ai_cache = {}

    processed = []
    now_ts = int(time.time())
    for full_name, repo in all_repos.items():
        stars = repo.get("stargazers_count", 0)
        repo_history = history.get(full_name, [])

        v24 = 0
        if repo_history:
            day_old = [h for h in repo_history if (now_ts - h["ts"]) >= 72000]
            if day_old:
                v24 = max(0, stars - day_old[-1]["stars"])
            else:
                v24 = max(0, stars - repo_history[0]["stars"])

        repo_history.append({"ts": now_ts, "stars": stars})
        # Retain up to 7 days (168 hourly snapshots) of history
        history[full_name] = repo_history[-168:]

        capabilities = extract_capabilities(repo)
        health = analyze_health(repo)
        category = classify(repo.get("description"), repo.get("topics", []), repo.get("name", ""))
        verdict, gotchas, comparison, replaces = enrich_with_ai(repo, category, capabilities, health, ai_cache)

        # Safe quick run default without supply-chain hallucination
        html_url = repo.get("html_url") or f"https://github.com/{full_name}"
        quick_run = f"git clone {html_url}"

        processed.append({
            "full_name": full_name,
            "name": repo.get("name"),
            "url": html_url,
            "description": repo.get("description"),
            "category": category,
            "verdict": verdict,
            "gotchas": gotchas,
            "comparison": comparison,
            "replaces": replaces,
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

    # Prune history keys that have been empty or unseen for 30 days
    cutoff_ts = now_ts - (30 * 86400)
    current_keys = set(all_repos.keys())
    pruned_history = {}
    for fn, entries in history.items():
        if fn in current_keys or (entries and entries[-1]["ts"] >= cutoff_ts):
            pruned_history[fn] = entries

    atomic_save_json(history_file, pruned_history)
    atomic_save_json(ai_cache_file, ai_cache)

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_repositories": len(processed),
        "repositories": processed
    }

    atomic_save_json(os.path.join("data", "repos.json"), payload)
    print(f"Saved {len(processed)} enriched repositories with AI verdicts to data/repos.json")

if __name__ == "__main__":
    run_pipeline()
