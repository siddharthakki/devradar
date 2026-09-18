/**
 * DevRadar Core Engine
 * 20-Category Taxonomy, Composite Breakout Ranking & Resilient Similarity Engine
 */

export const TAXONOMY = {
  // Core AI & Agents
  "Local LLM Engines": ["llm", "inference", "gguf", "vllm", "ollama", "transformers", "local-ai", "quantization", "llama.cpp", "exllamav2", "mistral"],
  "Multi-Agent Frameworks": ["agent", "agents", "autogen", "crewai", "langgraph", "swarm", "pydantic-ai", "multi-agent", "smolagents"],
  "RAG Engines": ["rag", "retrieval", "langchain", "llamaindex", "hybrid-search", "semantic-search", "haystack", "chunking"],
  "Vector Databases": ["vector-database", "vectordb", "chroma", "qdrant", "milvus", "weaviate", "pinecone", "pgvector", "embeddings"],
  
  // Media & Vision
  "Generative Image/Video": ["stable-diffusion", "comfyui", "flux", "diffusion", "image-generation", "video-generation", "text-to-video", "sdxl"],
  "Audio & Voice Synthesis": ["tts", "stt", "whisper", "speech-to-text", "text-to-speech", "voice-clone", "audio", "bark", "musicgen"],
  "Vision & OCR": ["ocr", "vision-language", "vlm", "yolo", "segmentation", "paddleocr", "document-ai", "surya"],
  "Creative Media & Design": ["canvas", "photo-editor", "video-editor", "canvas-ui", "3d-engine", "animation", "generative-art"],
  
  // Productivity & Knowledge
  "Second Brain & PKM": ["second-brain", "pkm", "obsidian", "note-taking", "knowledge-base", "logseq", "zettelkasten"],
  "AI Writing & Synthesis": ["writing-assistant", "summarization", "copilot", "text-generation", "grammar", "autocomplete"],
  "Document Vaults & Search": ["vault", "paperless", "pdf", "full-text-search", "document-management", "archive", "knowledge-graph"],
  "Spreadsheets & Data Grid": ["spreadsheet", "data-grid", "excel", "sheets", "csv", "table", "data-table"],

  // Sovereign & Infrastructure
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

  // 1. Same category gives baseline affinity
  if (repoA.category && repoB.category && repoA.category === repoB.category) {
    score += 0.45;
  }

  // 2. Same primary language
  if (repoA.language && repoB.language && repoA.language.toLowerCase() === repoB.language.toLowerCase()) {
    score += 0.25;
  }

  // 3. Jaccard similarity across topics
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
    .filter(item => item.score > 0.2) // Relaxed threshold so alternatives always appear
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(item => item.repo);
}
