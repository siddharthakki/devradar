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

  // 4. Competitor & Alternative Intent (e.g., "vs ollama", "alt:langchain", "alternative to pinecone", "replaces docker")
  const vsMatch = text.match(/\b(?:vs|versus|alt|alternative to|replaces?)\s*[:=]?\s*([a-z0-9_.-]+)\b/i);
  if (vsMatch) {
    filters.competitor = vsMatch[1].toLowerCase();
    text = text.replace(vsMatch[0], "");
  }

  // 5. Strip conversational noise
  text = text.replace(/\b(show me|find me|give me|i need|looking for|that|which|are|is|a|an|the|tools?|repos?|software)\b/gi, "").trim();

  return { cleanText: text, filters };
}

/**
 * Client-Side Hardware Specs Sniffer
 * Probes browser APIs (Navigator, WebGL, DeviceMemory) to detect local hardware tier.
 */
export function detectHardwareSpecs() {
  const specs = {
    platform: 'Unknown OS',
    cores: (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) || 4,
    ramGB: (typeof navigator !== 'undefined' && navigator.deviceMemory) || 8,
    gpu: 'Integrated Graphics',
    isAppleSilicon: false,
    isNvidia: false,
    tier: 'Minimal CPU',
    tierName: 'Minimal CPU',
    label: 'Standard CPU'
  };

  if (typeof navigator === 'undefined') return specs;

  // 1. Platform Detection
  const ua = navigator.userAgent || '';
  const plat = navigator.platform || '';
  if (/Mac/i.test(plat) || /Macintosh/i.test(ua)) {
    specs.platform = 'macOS';
  } else if (/Win/i.test(plat) || /Windows/i.test(ua)) {
    specs.platform = 'Windows';
  } else if (/Linux/i.test(plat) || /Linux/i.test(ua)) {
    specs.platform = 'Linux';
  }

  // 2. WebGL GPU Sniffing
  if (typeof document !== 'undefined') {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (gl) {
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
          specs.gpu = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || 'Integrated Graphics';
        }
      }
    } catch (e) {
      // WebGL blocked
    }
  }

  // 3. Classify Acceleration Tier
  const gpuLower = specs.gpu.toLowerCase();
  if (gpuLower.includes('apple') || (specs.platform === 'macOS' && (gpuLower.includes('metal') || !gpuLower.includes('intel')))) {
    specs.isAppleSilicon = true;
    specs.tier = '8GB Unified / Metal';
    specs.tierName = 'Apple Silicon (Metal)';
    specs.label = 'Apple Silicon (Metal)';
  } else if (gpuLower.includes('nvidia') || gpuLower.includes('geforce') || gpuLower.includes('rtx') || gpuLower.includes('quadro')) {
    specs.isNvidia = true;
    if (gpuLower.includes('3090') || gpuLower.includes('4090') || gpuLower.includes('a100') || gpuLower.includes('h100') || gpuLower.includes('a6000') || specs.ramGB >= 32) {
      specs.tier = '24GB+ CUDA VRAM';
      specs.tierName = 'Heavy CUDA (24GB+)';
      specs.label = 'NVIDIA 24GB+ CUDA';
    } else {
      specs.tier = '16GB+ CUDA VRAM';
      specs.tierName = 'CUDA (16GB)';
      specs.label = 'NVIDIA CUDA';
    }
  } else if (gpuLower.includes('radeon') || gpuLower.includes('amd')) {
    specs.tier = 'Minimal CPU';
    specs.tierName = 'AMD Radeon';
    specs.label = 'AMD GPU';
  } else {
    specs.tier = 'Minimal CPU';
    specs.tierName = 'Minimal CPU';
    specs.label = 'Minimal CPU';
  }

  return specs;
}

/**
 * Checks whether a repository's hardware requirement runs on a given rig tier
 */
export function isRepoCompatibleWithRig(repoHardwareReq, rigTier) {
  const req = (repoHardwareReq || '').toLowerCase();
  const tier = (rigTier || '').toLowerCase();

  // "Minimal CPU" runs on any machine
  if (req.includes('minimal') || req.includes('cpu')) return true;

  // "8GB Unified" requires Apple Silicon, high unified RAM, or CUDA
  if (req.includes('unified') || req.includes('metal')) {
    return tier.includes('metal') || tier.includes('unified') || tier.includes('cuda');
  }

  // "16GB+ CUDA" requires 16GB or 24GB CUDA
  if (req.includes('16gb')) {
    return tier.includes('16gb') || tier.includes('24gb');
  }

  // "24GB+ CUDA" requires 24GB CUDA
  if (req.includes('24gb')) {
    return tier.includes('24gb');
  }

  return true;
}
