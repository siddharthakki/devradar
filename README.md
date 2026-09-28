# ⚡ StackFit

> **Find the open-source tool you actually need — by what it replaces, what it runs on, and whether it's alive.**

StackFit is an opinionated, autonomous open-source matchmaker indexing 147+ verified high-velocity repositories across 20 disciplines. Instead of relying on vanity cumulative stars, StackFit ranks projects by **24-hour momentum**, **90-day activity sparklines**, **commit freshness**, and **hardware floor viability**.

---

## 🚀 Core Features

- **⚡ The Architectural Verdict:** Every repository features a repo-specific, non-templated verdict answering what incumbent it replaces and its architectural differentiator.
- **🛠️ Hero Stack Advisor:** Select your GPU/hardware floor (Mac M-Series, CPU Only, 8GB VRAM, 24GB+ CUDA) and engineering intent &rarr; get a tested, deployable stack with copyable `docker-compose.yml` and README specs.
- **📈 Today's Radar (Biggest Mover):** The single most interesting tool that appeared or spiked in the last 24 hours, with what it is, why this week, and what it replaces.
- **🗂️ 3-Tier Card Hierarchy:**
  - **Tier 1 (Identity & Health):** Category, Repo Name, 90-day SVG sparkline, why-it's-here signal badge (`[🚀 Spiking]`, `[✨ New]`, `[🧗 Climber]`, `[★ Established]`), and push cadence (`pushed 3h ago`).
  - **Tier 2 (The Verdict):** High-weight signature blockquote comparing directly to incumbents.
  - **Tier 3 (Requirements & Metadata):** Hardware floor, bold color-coded 24h delta, total stars, contributors, license, and action buttons.
- **⚖️ Side-by-Side Comparison Drawer:** Select up to 3 repositories to compare license, hardware floor, self-hosting model, MCP support, cloud lock-in risk, and 24h momentum, with one-click Markdown export.
- **📄 Deep-Dive Pages & Embeddable Badges:** Detailed modal/view with hardware matrix, alternative recommendations, and copyable README badge markdown.
- **🔖 Persistent Watchlist:** Stored in `localStorage` and encoded in shareable URLs (`?watch=...`).
- **✉️ Weekly Digest & RSS:** Top 5 movers that spiked this week and what they replace, available in markdown newsletter format and RSS 2.0 XML.
- **🎨 Multi-Theme System:** Amber Gold, Emerald Forest, Cyber Violet, Copper Rust, Titanium Mono, and Cyan Ice tucked behind a clean popover.

---

## 💻 CLI Usage

Query breakout tools directly from your terminal:

```bash
# Top 10 breakout tools
python cli.py --top 10

# Filter by category
python cli.py --category "Local LLM Engines"
```

---

## 🏃 Development & Pipeline

```bash
# Run local tests
make test

# Ingest fresh GitHub updates
make ingest

# Generate RSS feed and static category API endpoints
make feeds

# Generate weekly markdown digest
make digest

# Run local web server
make run
```

---

## 📖 Methodology

Read our complete ranking methodology, anti-bot scoring, and velocity decay models at [`how-it-works.html`](https://siddharthakki.github.io/stackfit/how-it-works.html).