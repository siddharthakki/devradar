# ⚡ StackFit Viral Growth & Promotion Playbook

> **"Find the open-source tool you actually need — by what it replaces, what it runs on, and whether it's alive."**

This playbook provides copy-paste ready launch kits, viral hooks, community distribution channels, and URL migration instructions to propel StackFit to the front page of Hacker News, developer Twitter, and Reddit.

---

## 🌐 1. The URL Rename: `devradar` &rarr; `stackfit`

### Should you change the URL to StackFit?
**Yes, unconditionally.** Here is why:
1. **Brand Authenticity & Trust:** When engineers click a link promoting "StackFit", landing on `.../stackfit/` (or `stackfit.dev`) instantly signals a real, focused product rather than a leftover development repo.
2. **Zero Link Rot Risk:** GitHub automatically configures 301 redirects for web requests and git clones from `siddharthakki/devradar` &rarr; `siddharthakki/stackfit`.
3. **Dynamic Client Compatibility:** The codebase has already been upgraded so that badges, RSS feeds, watchlist URLs, and comparison links dynamically detect whatever URL they are hosted on.

### How to Rename in 10 Seconds:
Run this command directly in your terminal:
```bash
gh repo rename stackfit --yes
```
*Or via GitHub Web:* Go to **Repository Settings &rarr; General &rarr; Repository name &rarr; Type `stackfit` &rarr; Click Rename**.

GitHub Pages will immediately re-point to:
`https://siddharthakki.github.io/stackfit/`

---

## 🚀 2. Hacker News (Show HN) Launch Package

> **Best Timing:** Tuesday or Wednesday between **13:00 UTC and 14:30 UTC** (08:00 AM – 09:30 AM US Eastern Time). This hits the morning commute in the US and the afternoon in Europe when HN traffic peaks.

### Post Title
```text
Show HN: StackFit – Find OSS tools by what they replace and what hardware they run on
```

### Submission URL
```text
https://siddharthakki.github.io/stackfit/
```

### First Comment (Post immediately after submitting)
```markdown
Hey HN,

We built StackFit (https://siddharthakki.github.io/stackfit/) because cumulative GitHub stars have become an unreliable vanity metric. Legacy projects that haven't merged a commit since 2021 sit on 85,000 legacy stars, while high-velocity, lightweight alternatives that solve today's problems get buried.

Worse, bot farms and VC hype cycles make raw trending pages noisy.

StackFit indexes 147+ verified repositories across 20 disciplines and evaluates them by:

1. **The Architectural Verdict:** Every tool is matched directly against what incumbent it replaces (e.g., Dify replaces LangChain/Flowise; SGLang replaces vLLM with RadixAttention; Qdrant replaces Pinecone without cloud lock-in).
2. **Hardware Floor Viability:** Can my M-series Mac or 16GB GPU actually run this locally without OOM crashes? We flag CUDA VRAM requirements, Apple Silicon compatibility, and low-spec CPU viability.
3. **24-Hour Velocity & 90-Day Sparklines:** Instead of lifetime stars, we track real momentum and commit freshness (`pushed 3h ago`).
4. **Hero Stack Advisor:** Pick your available hardware (CPU Only, 8GB VRAM, 24GB+ CUDA) and engineering goal &rarr; get a tested, deployable stack with 1-click `docker-compose.yml` generation.
5. **No Trackers or Signups:** Pure client-side single page app, persistent localStorage watchlists, RSS feeds, and side-by-side comparison tables.

Methodology details and anti-bot weighting can be read here:
https://siddharthakki.github.io/stackfit/how-it-works.html

Everything is 100% open-source. What tools or hardware profiles would you like to see added? Would love your brutal architectural feedback!
```

---

## 𝕏 3. The 𝕏 (Twitter) Viral Thread Package

Attach the generated visual preview card (`assets/stackfit-og.png`) to Tweet 1.

### Tweet 1 (The Hook)
```text
GitHub stars are broken.

VC hype and star-buying bot farms have turned repo discovery into a vanity contest. Abandoned tools from 2020 sit on 90k stars while blazing-fast Rust and Python alternatives stay invisible.

We built StackFit to fix this:
⚡ What it replaces
💻 What hardware runs it
📈 24h momentum, not vanity stars

https://siddharthakki.github.io/stackfit/

🧵👇
```

### Tweet 2 (The Hardware Problem)
```text
1/ The Hardware Reality 💻

How many times have you cloned a repo only to realize it requires 4x A100 GPUs or 48GB VRAM?

StackFit tags every tool with an explicit Hardware Floor:
• Runs on CPU / Low RAM
• Mac M-Series (Metal)
• 8GB–16GB VRAM
• 24GB+ CUDA Clusters

Stop guessing if your laptop can run it.
```

### Tweet 3 (The Incumbent Replacement Verdict)
```text
2/ The Incumbent Replacement Index ⚡

Every single project features a non-templated Architectural Verdict answering: "What does this actually replace?"

• Dify &rarr; Alt to LangChain & Flowise
• SGLang &rarr; Alt to vLLM (RadixAttention caching)
• LightRAG &rarr; Alt to GraphRAG (10x cheaper & faster)
• LibreChat &rarr; Alt to ChatGPT Team with native MCP
```

### Tweet 4 (Hero Stack Advisor)
```text
3/ Hero Stack Advisor 🛠️

Select your available hardware and your engineering goal (e.g., "M3 Mac + Private Offline Code Assistant").

StackFit calculates the optimal stack and outputs a 1-click copyable docker-compose.yml and architecture README ready to run locally.
```

### Tweet 5 (Interactive Features)
```text
4/ Zero Fluff, 100% Client-Side 🛡️

• ⚖️ 3-way Side-by-Side Comparison Drawer (Markdown export)
• 🔔 Browser & Webhook alerts for watched repo spikes
• 📡 Sliced RSS feeds (feed only your bookmarked tools to Slack)
• 🎨 6 custom theme presets (Amber Gold, Titanium Mono, Cyber Violet...)
```

### Tweet 6 (CTA & Open Source)
```text
StackFit is completely open-source and updates autonomously every 24 hours.

Check it out, test your stack, and find the tools you actually need:
👉 https://siddharthakki.github.io/stackfit/

If you find it useful, drop a star on GitHub:
⭐ https://github.com/siddharthakki/stackfit
```

---

## 🤖 4. Reddit Subreddit Strategy

### Subreddit 1: `r/selfhosted`
* **Title:** `I built StackFit: An open-source tool matchmaker that filters by self-hosting viability and docker-compose export (no star vanity)`
* **Body:**
```markdown
Hey r/selfhosted,

Like many of you, I've grown exhausted with GitHub's trending tab. Most repos pushed by algorithms require closed enterprise cloud APIs or unstated monster GPU clusters.

I built **StackFit** (https://siddharthakki.github.io/stackfit/) to help self-hosters find genuine alternatives to SaaS:
- Every tool is evaluated by its **self-hosting model** and **cloud lock-in risk**.
- Filter specifically by **CPU-Only**, **Docker Container**, and **Local-First / CRDT** architectures.
- Built-in **Hero Stack Advisor** that outputs tested `docker-compose.yml` configs for local stacks (e.g., Local LLM + Vector DB + Chat UI).
- Sliced RSS feeds you can pipe directly into Miniflux, FreshRSS, or self-hosted Discord bots.

Zero ads, zero accounts, pure static client. Feedback on missing self-hosted gems is welcome!
```

### Subreddit 2: `r/LocalLLaMA`
* **Title:** `StackFit: Indexing local LLM engines & RAG tools by hardware floor (Mac M-Series, 8GB, 16GB, 24GB+ VRAM) and 24h momentum`
* **Body:**
```markdown
Hey everyone,

Whenever a new inference engine or RAG framework drops, the first question in the comments is always: *"Can I run this on my RTX 4070 or 16GB M-series Mac?"*

I built **StackFit** (https://siddharthakki.github.io/stackfit/) to index 147+ local AI tools by explicit hardware requirements:
- **Local LLM Engines:** llama.cpp vs vLLM vs SGLang vs ExLlamaV2 compared by throughput and VRAM allocation.
- **RAG & Vector DBs:** LightRAG vs GraphRAG, Qdrant vs Milvus vs pgvector.
- **Side-by-Side Comparison Drawer:** Pick 3 tools and compare their memory footprint, quantization support, MCP support, and 24h star momentum side by side.

Check it out and let me know if any hardware requirements need tuning!
```

### Subreddit 3: `r/programming`
* **Title:** `Why cumulative GitHub stars are a misleading metric for developer tools (and what we built instead)`
* **Body:**
```markdown
We published an open-source radar and methodology examining why cumulative lifetime stars fail software engineering teams:
https://siddharthakki.github.io/stackfit/how-it-works.html

Instead of cumulative counts, StackFit introduces a composite velocity scoring model:
`Score = (Velocity24h * 3.5 + log10(Stars) * 2.5) * RecencyMultiplier * AuthenticityBonus`

Where:
- Push recency within 7 days gives a 1.4x multiplier, while repos inactive >180 days decay by 0.35x.
- An anti-bot authenticity model discounts accounts with sudden anomalous spikes from unstarred empty accounts.
- Tools are classified into a 20-category ontology with explicit architectural verdicts.

Live interactive radar: https://siddharthakki.github.io/stackfit/
Code: https://github.com/siddharthakki/stackfit
```

---

## 🏆 5. Developer Newsletters & Direct Syndication

| Channel | Submission URL | Suggested Hook |
| :--- | :--- | :--- |
| **TLDR Web Dev / AI** | [tldr.tech/submit](https://tldr.tech) | "StackFit: An open-source matchmaker indexing 147+ tools by hardware requirements & what they replace" |
| **Console.dev** | [console.dev/contact](https://console.dev) | Focus on the developer tools angle & CLI tool (`python cli.py --top 10`) |
| **Bytes.dev** | [bytes.dev](https://bytes.dev) | Punchy summary of the anti-star-vanity angle |
| **Changelog** | [changelog.com/submit](https://changelog.com/submit) | Request a quick mention in "Changelog Weekly" OSS spotlight |
| **Daily.dev** | Direct source submission on daily.dev | RSS feed submission `https://siddharthakki.github.io/stackfit/data/feed.xml` |

---

## 🏷️ 6. The Repo Maintainer Viral Loop

Every repository indexed on StackFit has an embeddable markdown badge:
```markdown
[![StackFit Verdict](https://img.shields.io/badge/StackFit-Production%20Ready-amber)](https://siddharthakki.github.io/stackfit/#repo/<reponame>)
```

Find 10 fast-rising repositories featured in Today's Radar (e.g., `sglang`, `dify`, `LibreChat`, `Codewhale`, `LightRAG`) and tweet / open a polite discussion:
> *"Hey team! We analyzed @[Repo] on StackFit and awarded it the [🚀 Spiking] badge with an architectural verdict over [Incumbent]. If you'd like to show your verified status, feel free to drop this badge in your README!"*

---

## 🤖 7. Autonomous Social Media Posting Engine

StackFit includes an automated multi-platform broadcast engine in `engine/social_poster.py` that formats and publishes breakout tools and stacks.

### Dry-Run Preview (Test locally anytime):
```bash
# Preview today's #1 breakout spiker post:
python engine/social_poster.py --topic spiker --dry-run

# Preview today's recommended deployable stack post:
python engine/social_poster.py --topic stack --dry-run
```

### Supported Platforms & Setup:
| Network | Env Var / Secret | Notes |
| :--- | :--- | :--- |
| **Discord** | `DISCORD_WEBHOOK_URL` | Posts formatted rich embed cards with hardware floor & 24h momentum |
| **Slack** | `SLACK_WEBHOOK_URL` | Instant team updates via incoming webhook |
| **Bluesky** | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` | AT Protocol REST API (100% free, high developer engagement) |
| **Twitter / 𝕏** | `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET` | OAuth 1.0a / v2 automated tweets |

### Automatic Scheduled Posting via GitHub Actions:
The workflow `.github/workflows/social-broadcast.yml` runs **automatically every day at 07:30 UTC** (right after radar data syncs).
- Add any of the above secrets to your GitHub repository at: `Settings -> Secrets and variables -> Actions`.
- You can also trigger an immediate post at any time from GitHub: `Actions -> StackFit Social Broadcast -> Run workflow`.

---

## 🎬 8. 30-Second Viral Video Assets & YouTube Shorts Kit

We generated a studio-quality 30-second promo video in two resolutions with Kokoro neural voice narration and a driving 120BPM tech backing pulse:

1. **Landscape 16:9 (`assets/stackfit_promo_16x9.mp4`):**
   - **Resolution:** 1920x1080 Full HD
   - **Ideal for:** YouTube Video, Twitter/𝕏 desktop feed, LinkedIn, Product Hunt media gallery.
2. **Vertical 9:16 (`assets/stackfit_promo_vertical.mp4`):**
   - **Resolution:** 1080x1920 Full HD
   - **Ideal for:** YouTube Shorts, TikTok, Instagram Reels, Twitter/𝕏 Mobile.

### Voiceover Script Breakdown:
- **0:00 - 0:06 (The Hook):** *"GitHub stars are broken. Bot farms and VC hype have turned repo discovery into a vanity contest."*
- **0:06 - 0:13 (The Hardware Trap):** *"You clone a repo, only to find it needs four A100 GPUs and 48 gigabytes of VRAM just to boot."*
- **0:13 - 0:22 (The Solution):** *"Meet StackFit: the open-source matchmaker that indexes 147 tools by what they replace, what they run on, and whether they are alive."*
- **0:22 - 0:27 (Hero Stack Advisor):** *"Pick your laptop specs and get tested, one-click docker-compose stacks in seconds."*
- **0:27 - 0:33 (Call to Action):** *"Stop guessing. Start building. Explore StackFit at siddharthakki.github.io/stackfit."*

### YouTube Shorts & TikTok Posting Metadata:
* **Video Title:** `Why GitHub stars are lying to you (and what to use instead) ⚡`
* **Alternative Title:** `Can your laptop actually run that AI repo? 💻 #Shorts`
* **Description:**
```text
Stop trusting cumulative GitHub stars. Abandoned repos sit on 90k stars while high-velocity tools get buried.

StackFit indexes 147+ verified open-source tools by:
⚡ What they replace (Dify vs LangChain, SGLang vs vLLM)
💻 Hardware floor (Mac M-Series, 16GB, 24GB+ CUDA)
📈 24-hour momentum (not vanity stars)
🛠️ 1-click docker-compose generation

👉 Explore for free: https://siddharthakki.github.io/stackfit/
⭐ GitHub: https://github.com/siddharthakki/stackfit

#OpenSource #Coding #SoftwareEngineering #AI #LocalAI #DevTools #Programming #Tech
```

