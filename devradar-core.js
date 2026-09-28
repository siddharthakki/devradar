/**
 * DevRadar Core Engine
 * 20-Category Taxonomy, Composite Breakout Ranking, Jaccard Similarity & NL Intent Parsing
 */

export const TAXONOMY = {
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
};

export function classifyRepo(repo) {
  const text = `${repo.name || ''} ${repo.description || ''} ${(repo.topics || []).join(' ')}`.toLowerCase();
  let bestCategory = "CLI & TUI Tooling";
  let maxMatches = 0;

  for (const [category, keywords] of Object.entries(TAXONOMY)) {
    let matches = 0;
    for (const kw of keywords) {
      if (text.includes(kw)) matches++;
    }
    if (matches > maxMatches) {
      maxMatches = matches;
      bestCategory = category;
    }
  }
  return bestCategory;
}

export function computeBreakoutScore(repo) {
  const v24 = repo.stars_24h || repo.v24 || 0;
  const stars = Math.max(1, repo.stars || repo.stargazers_count || 1);
  const authBonus = (repo.authenticity_score || 85) / 100;

  const lastActive = new Date(repo.pushed_at || repo.created_at || Date.now());
  const daysSincePush = Math.max(0, (Date.now() - lastActive.getTime()) / (1000 * 3600 * 24));
  
  let recencyMultiplier = 1.0;
  if (daysSincePush <= 7) recencyMultiplier = 1.4;
  else if (daysSincePush <= 30) recencyMultiplier = 1.15;
  else if (daysSincePush > 180) recencyMultiplier = 0.35;

  const authority = Math.log10(stars);
  const velocityWeight = v24 * 3.5;

  return Number(((velocityWeight + (authority * 2.5)) * recencyMultiplier * authBonus).toFixed(2));
}

export function computeSimilarity(repoA, repoB) {
  if ((repoA.full_name || repoA.name) === (repoB.full_name || repoB.name)) return -1;
  let score = 0;

  if (repoA.category && repoB.category && repoA.category === repoB.category) score += 0.45;
  if (repoA.language && repoB.language && repoA.language.toLowerCase() === repoB.language.toLowerCase()) score += 0.25;

  const topicsA = new Set((repoA.topics || []).map(t => t.toLowerCase()));
  const topicsB = new Set((repoB.topics || []).map(t => t.toLowerCase()));
  if (topicsA.size > 0 && topicsB.size > 0) {
    const intersection = new Set([...topicsA].filter(x => topicsB.has(x)));
    const union = new Set([...topicsA, ...topicsB]);
    score += (intersection.size / union.size) * 0.5;
  }
  return score;
}

export function getSimilarRepos(targetRepo, allRepos, limit = 2) {
  return allRepos
    .filter(r => (r.full_name || r.name) !== (targetRepo.full_name || targetRepo.name))
    .map(r => ({ repo: r, score: computeSimilarity(targetRepo, r) }))
    .filter(item => item.score > 0.2)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(item => item.repo);
}

/**
 * Pure Natural Language Query Parser
 * Returns { cleanText, filters } without touching DOM directly
 */
export function parseNaturalLanguage(raw) {
  let text = (raw || '').toLowerCase().trim();
  const filters = {};

  if (!text) return { cleanText: '', filters };

  // 1. Discipline
  if (text.includes("local llm") || text.includes("llm engine") || text.includes("offline model")) {
    filters.discipline = "Local LLM Engines";
    text = text.replace(/local llms?|llm engines?|offline models?/g, "");
  } else if (text.includes("agent") || text.includes("multi-agent") || text.includes("crew")) {
    filters.discipline = "Multi-Agent Frameworks";
    text = text.replace(/multi-agents?|agents?|crew/g, "");
  } else if (text.includes("rag") || text.includes("retrieval")) {
    filters.discipline = "RAG Engines";
    text = text.replace(/rag|retrieval/g, "");
  } else if (text.includes("cli") || text.includes("tui") || text.includes("terminal tool")) {
    filters.discipline = "CLI & TUI Tooling";
    text = text.replace(/cli|tui|terminal tools?/g, "");
  }

  // 2. Hardware / Needs
  if (text.includes("without gpu") || text.includes("no gpu") || text.includes("don't need a gpu") || text.includes("dont need a gpu") || text.includes("on cpu") || text.includes("for mac")) {
    filters.needs = "cpu-only";
    text = text.replace(/without gpu|no gpu|don'?t need a gpu|on cpu|for mac/g, "");
  } else if (text.includes("with gpu") || text.includes("needs cuda") || text.includes("rtx") || text.includes("nvidia")) {
    filters.needs = "gpu";
    text = text.replace(/with gpu|needs cuda|rtx|nvidia/g, "");
  }

  // 3. Language
  const langMatch = text.match(/\b(in|for|using)\s+(python|rust|typescript|javascript|go)\b/);
  if (langMatch) {
    filters.lang = langMatch[2];
    text = text.replace(langMatch[0], "");
  }

  // 4. Strip conversational noise
  text = text.replace(/\b(show me|find me|give me|i need|looking for|that|which|are|is|a|an|the|tools?|repos?|software)\b/gi, "").trim();

  return { cleanText: text, filters };
}

/**
 * Render lightweight inline SVG sparkline path
 */
export function renderSparklineSvg(points = [], width = 56, height = 18, color = 'var(--accent-primary, #f59e0b)') {
  if (!points || points.length === 0) points = [20, 30, 45, 60, 80, 95];
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = Math.max(1, max - min);
  const step = width / (points.length - 1);

  const coords = points.map((p, i) => {
    const x = (i * step).toFixed(1);
    const y = (height - 2 - ((p - min) / range) * (height - 4)).toFixed(1);
    return `${x},${y}`;
  });

  const pathD = `M ${coords.join(' L ')}`;
  return `
    <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" class="overflow-visible inline-block">
      <path d="${pathD}" fill="none" stroke="${color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" />
      <circle cx="${coords[coords.length - 1].split(',')[0]}" cy="${coords[coords.length - 1].split(',')[1]}" r="2" fill="${color}" />
    </svg>
  `;
}

/**
 * Render unicode block sparkline
 */
export function renderSparklineText(points = []) {
  if (!points || points.length === 0) points = [10, 25, 40, 60, 80, 95];
  const blocks = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█'];
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = Math.max(1, max - min);
  return points.map(p => {
    const idx = Math.min(blocks.length - 1, Math.floor(((p - min) / range) * (blocks.length - 1)));
    return blocks[idx];
  }).join('');
}

/**
 * Curated Stack Advisor Knowledge Engine
 * Maps (Hardware Floor, Architectural Intent) -> deployable stack, docker-compose.yml & markdown sheet
 */
export const STACK_RECOMMENDATIONS = {
  "mac-m-series": {
    "local-llm": {
      title: "Apple Silicon Metal Acceleration Stack",
      subtitle: "Sub-100ms TTFT local inference with unified memory and native MCP tool calling.",
      components: [
        { role: "Inference Engine", name: "Rapid-MLX", full_name: "raullenchai/Rapid-MLX", why: "4.2x faster TTFT than Ollama on Apple Silicon Metal with prompt cache." },
        { role: "Multi-User WebUI", name: "LibreChat", full_name: "danny-avila/LibreChat", why: "Full multi-model UI with native MCP server integration." },
        { role: "CLI Coding Agent", name: "Codewhale", full_name: "Hmbown/Codewhale", why: "Blazing fast Rust terminal coding assistant with AST refactoring." }
      ],
      docker_compose: `version: '3.8'
services:
  mlx-engine:
    image: python:3.11-slim
    container_name: stackfit-mlx-engine
    restart: unless-stopped
    command: sh -c "pip install rapid-mlx && rapid-mlx serve --port 8000"
    ports:
      - "8000:8000"
    environment:
      - MLX_CACHE_DIR=/models

  librechat:
    image: ghcr.io/danny-avila/librechat-dev:latest
    container_name: stackfit-librechat
    ports:
      - "3080:3080"
    environment:
      - HOST=0.0.0.0
      - OPENAI_REVERSE_PROXY=http://mlx-engine:8000/v1
    depends_on:
      - mlx-engine`,
      markdown_sheet: `# StackFit Architecture Sheet: Apple Silicon Local Stack
- **Hardware Profile:** Apple Silicon (M1/M2/M3/M4 - 16GB+ Unified Memory)
- **Primary Goal:** Local-first LLM inference without cloud dependencies or per-token fees.

### Recommended Components:
1. **Rapid-MLX** (\`raullenchai/Rapid-MLX\`): 4.2x faster TTFT on Metal with native tool calling.
2. **LibreChat** (\`danny-avila/LibreChat\`): Self-hosted UI with full MCP server connectivity.
3. **Codewhale** (\`Hmbown/Codewhale\`): Terminal agent written in Rust.

### Quick Start:
\`\`\`bash
# 1. Start local engine
pip install rapid-mlx && rapid-mlx serve
# 2. Point LibreChat or Claude Code to http://localhost:8000/v1
\`\`\``
    },
    "rag-knowledge": {
      title: "Apple Silicon Graph & Vector RAG Stack",
      subtitle: "Dual-level entity retrieval with Qdrant vector storage running locally on Mac.",
      components: [
        { role: "Vector Database", name: "Qdrant", full_name: "qdrant/qdrant", why: "Fast Rust vector search with memory-efficient payload filtering." },
        { role: "Graph RAG Engine", name: "LightRAG", full_name: "HKUDS/LightRAG", why: "Dual-level entity relationship retrieval 10x cheaper than GraphRAG." },
        { role: "Knowledge Base", name: "claude-obsidian", full_name: "AgriciDaniel/claude-obsidian", why: "Self-organizing markdown second brain based on Karpathy's wiki." }
      ],
      docker_compose: `version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: stackfit-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage

  lightrag-service:
    image: python:3.11-slim
    container_name: stackfit-lightrag
    restart: unless-stopped
    command: sh -c "pip install lightrag-hku && python -m lightrag.api"
    ports:
      - "8020:8020"
    environment:
      - VECTOR_DATABASE=qdrant
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - qdrant`,
      markdown_sheet: `# StackFit Architecture Sheet: Local Graph & Vector RAG
- **Hardware Profile:** Mac M-Series (16GB+ Unified Memory)
- **Primary Goal:** Self-hosted entity-relationship RAG without cloud lock-in.

### Components:
- **Qdrant**: High-performance Rust vector store.
- **LightRAG**: Fast dual-level graph retrieval.
- **claude-obsidian**: Markdown knowledge vault.`
    }
  },
  "cpu-only": {
    "local-llm": {
      title: "Commodity CPU Zero-GPU Stack",
      subtitle: "Pure C++ quantized GGUF execution with minimal memory footprint on x86/ARM.",
      components: [
        { role: "Inference Engine", name: "llama.cpp", full_name: "ggml-org/llama.cpp", why: "Raw C++ runtime with AVX2/NEON optimizations, zero server layer." },
        { role: "Terminal Client", name: "mcp-client-for-ollama", full_name: "jonigl/mcp-client-for-ollama", why: "Terminal-native MCP harness running 100% locally." },
        { role: "Code Agent", name: "Codewhale", full_name: "Hmbown/Codewhale", why: "Fast Rust agent operating smoothly on CPU-only machines." }
      ],
      docker_compose: `version: '3.8'
services:
  llamacpp-server:
    image: ghcr.io/ggerganov/llama.cpp:server
    container_name: stackfit-llamacpp
    restart: unless-stopped
    ports:
      - "8080:8080"
    command: -m /models/qwen2.5-7b-instruct-q4_k_m.gguf -c 4096 --host 0.0.0.0 --port 8080
    volumes:
      - ./models:/models`,
      markdown_sheet: `# StackFit Architecture Sheet: CPU-Only Inference Stack
- **Hardware Profile:** CPU Only / Low RAM (x86_64 or ARM commodity)
- **Primary Goal:** Run offline AI inference without requiring a dedicated GPU.

### Components:
- **llama.cpp**: Efficient CPU quantization (Q4_K_M GGUF).
- **mcp-client**: TUI interface with Model Context Protocol support.

### Run Command:
\`\`\`bash
docker compose up -d
curl http://localhost:8080/v1/models
\`\`\``
    },
    "rag-knowledge": {
      title: "Lightweight CPU Vector Search & RAG Stack",
      subtitle: "Rust-native vector indexing on CPU memory with ManticoreSearch hybrid retrieval.",
      components: [
        { role: "Search Database", name: "manticoresearch", full_name: "manticoresoftware/manticoresearch", why: "C++ real-time hybrid search with tiny RAM footprint." },
        { role: "Embedding Engine", name: "Qdrant", full_name: "qdrant/qdrant", why: "Fast filtered vector search operating comfortably on 2GB RAM." },
        { role: "Local Vault", name: "QOwnNotes", full_name: "pbek/QOwnNotes", why: "Pure markdown note-taking with Nextcloud synchronization." }
      ],
      docker_compose: `version: '3.8'
services:
  manticore:
    image: manticoresearch/manticore:latest
    container_name: stackfit-manticore
    ports:
      - "9306:9306"
      - "9308:9308"
    volumes:
      - ./manticore_data:/var/lib/manticore

  qdrant:
    image: qdrant/qdrant:latest
    container_name: stackfit-qdrant-cpu
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage`,
      markdown_sheet: `# StackFit Architecture Sheet: Lightweight CPU RAG
- **Hardware Profile:** CPU Only / Low RAM
- **Primary Goal:** Hybrid keyword + vector search with minimal memory consumption.`
    }
  },
  "gpu-8gb": {
    "local-llm": {
      title: "Consumer GPU (8GB–12GB VRAM) Production Stack",
      subtitle: "Quantized 7B/8B model serving with PagedAttention or SGLang prefix caching.",
      components: [
        { role: "Inference Engine", name: "sglang", full_name: "sgl-project/sglang", why: "RadixAttention prefix caching delivers 3-5x higher throughput on 8GB-12GB GPUs." },
        { role: "Enterprise WebUI", name: "LibreChat", full_name: "danny-avila/LibreChat", why: "OpenAI-compatible client with tool calling and prompt presets." },
        { role: "Speech Synthesis", name: "vui", full_name: "fluxions-ai/vui", why: "Lightweight 219M param conversational voice cloning running on CPU." }
      ],
      docker_compose: `version: '3.8'
services:
  sglang:
    image: lmsysorg/sglang:latest
    container_name: stackfit-sglang
    restart: unless-stopped
    runtime: nvidia
    ports:
      - "30000:30000"
    command: python3 -m sglang.launch_server --model-path Qwen/Qwen2.5-7B-Instruct --port 30000 --host 0.0.0.0 --mem-fraction-static 0.8
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  librechat:
    image: ghcr.io/danny-avila/librechat-dev:latest
    container_name: stackfit-librechat
    ports:
      - "3080:3080"
    environment:
      - HOST=0.0.0.0
      - OPENAI_REVERSE_PROXY=http://sglang:30000/v1
    depends_on:
      - sglang`,
      markdown_sheet: `# StackFit Architecture Sheet: Consumer GPU Stack
- **Hardware Profile:** 8GB–12GB CUDA VRAM (RTX 3060 / 4060 / 3070)
- **Primary Goal:** Fast token generation with prefix caching and chat UI.

### Quick Start:
\`\`\`bash
docker compose up -d
# Access UI at http://localhost:3080
\`\`\``
    },
    "rag-knowledge": {
      title: "Enterprise Visual RAG & Agent Stack",
      subtitle: "Visual workflow builder with Qdrant vector storage and MCP agent coordination.",
      components: [
        { role: "Orchestration & UI", name: "dify", full_name: "langgenius/dify", why: "Visual agentic workflow and RAG builder that exports clean standalone APIs." },
        { role: "Vector Database", name: "Qdrant", full_name: "qdrant/qdrant", why: "Rust-native vector search with zero cloud lock-in." },
        { role: "Agent Memory", name: "OpenViking", full_name: "volcengine/OpenViking", why: "Self-evolving context database unifying agent memory and knowledge." }
      ],
      docker_compose: `version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: stackfit-qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage

  dify-api:
    image: langgenius/dify-api:latest
    container_name: stackfit-dify
    ports:
      - "5001:5001"
    environment:
      - VECTOR_STORE=qdrant
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - qdrant`,
      markdown_sheet: `# StackFit Architecture Sheet: Visual RAG & Agents
- **Hardware Profile:** 8GB–12GB VRAM + Host System
- **Components:** Dify visual builder + Qdrant vector store + OpenViking agent memory.`
    }
  },
  "gpu-24gb": {
    "local-llm": {
      title: "Hyperscale High-Throughput Cluster Stack",
      subtitle: "SGLang RadixAttention prefix caching paired with LMCache KV layers for massive concurrency.",
      components: [
        { role: "Serving Runtime", name: "sglang", full_name: "sgl-project/sglang", why: "State-of-the-art serving engine handling multi-turn batching on 24GB+ hardware." },
        { role: "KV Cache Acceleration", name: "LMCache", full_name: "LMCache/LMCache", why: "Supercharges serving with fastest cross-GPU KV cache sharing, cutting TTFT 85%." },
        { role: "Cluster Operator", name: "LLMKube", full_name: "defilantech/LLMKube", why: "Kubernetes operator sharding inference across heterogeneous GPU fleets." }
      ],
      docker_compose: `version: '3.8'
services:
  sglang-cluster:
    image: lmsysorg/sglang:latest
    container_name: stackfit-sglang-prod
    runtime: nvidia
    ports:
      - "30000:30000"
    command: python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-V3 --tp 2 --port 30000
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  lmcache:
    image: lmcache/lmcache-server:latest
    container_name: stackfit-lmcache
    ports:
      - "65432:65432"
    environment:
      - LMCACHE_CHUNK_SIZE=256
      - LMCACHE_LOCAL_CPU=True`,
      markdown_sheet: `# StackFit Architecture Sheet: 24GB+ Production Cluster
- **Hardware Profile:** 24GB+ CUDA VRAM (RTX 4090 / A100 / H100)
- **Primary Goal:** Maximum throughput for high-concurrency API serving and coding agents.`
    },
    "rag-knowledge": {
      title: "Hyperscale Enterprise Vector & RAG Stack",
      subtitle: "Multi-billion vector ANN indexing with Milvus and self-hosted Onyx workplace intelligence.",
      components: [
        { role: "Enterprise Search", name: "onyx", full_name: "onyx-dot-app/onyx", why: "Self-hosted alternative to Glean connecting 30+ workplace apps to private AI chat." },
        { role: "Distributed Vector DB", name: "milvus", full_name: "milvus-io/milvus", why: "Massive-scale distributed vector indexing for multi-billion vector clusters." },
        { role: "Context Engine", name: "OpenViking", full_name: "volcengine/OpenViking", why: "Unified context database for memory and knowledge RAG." }
      ],
      docker_compose: `version: '3.8'
services:
  milvus-standalone:
    image: milvusdb/milvus:v2.4.0
    container_name: stackfit-milvus
    command: ["milvus", "run", "standalone"]
    ports:
      - "19530:19530"

  onyx-service:
    image: onyxdotapp/onyx-backend:latest
    container_name: stackfit-onyx
    ports:
      - "8080:8080"
    environment:
      - VECTOR_DB_TYPE=milvus
      - MILVUS_HOST=milvus-standalone
    depends_on:
      - milvus-standalone`,
      markdown_sheet: `# StackFit Architecture Sheet: Enterprise Knowledge Hub
- **Hardware Profile:** 24GB+ VRAM / Production Docker Host
- **Components:** Onyx enterprise workplace search + Milvus vector database.`
    }
  }
};

/**
 * Retrieve recommended stack or fallback gracefully
 */
export function getRecommendedStack(hw = "mac-m-series", intent = "local-llm") {
  const hwGroup = STACK_RECOMMENDATIONS[hw] || STACK_RECOMMENDATIONS["mac-m-series"];
  return hwGroup[intent] || hwGroup["local-llm"];
}

