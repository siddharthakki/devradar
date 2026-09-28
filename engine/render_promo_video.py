"""
StackFit 30-Second Viral Promo Video Generator
Renders broadcast-quality 1080p landscape (16:9) and vertical (9:16) videos with
Kokoro neural studio narration, synchronized kinetic captions, tech synth beat,
and high-contrast dark mode developer aesthetics.
"""
import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

AUDIO_PATH = "scratch/final_voiceover_mix.wav"
OUTPUT_16X9 = "assets/stackfit_promo_16x9.mp4"
OUTPUT_9X16 = "assets/stackfit_promo_vertical.mp4"

# Timeline beats (seconds)
BEATS = [
    {"start": 0.0,  "end": 6.4,  "scene": 1, "caption": "GitHub stars are broken. Bot farms and VC hype have turned repo discovery into a vanity contest."},
    {"start": 6.4,  "end": 13.2, "scene": 2, "caption": "You clone a repo, only to find it needs four A100 GPUs and 48 gigabytes of VRAM just to boot."},
    {"start": 13.2, "end": 22.3, "scene": 3, "caption": "Meet StackFit: the open-source matchmaker that indexes 147 tools by what they replace and run on."},
    {"start": 22.3, "end": 27.2, "scene": 4, "caption": "Pick your laptop specs and get tested, one-click docker-compose stacks in seconds."},
    {"start": 27.2, "end": 32.8, "scene": 5, "caption": "Stop guessing. Start building. Explore StackFit at siddharthakki.github.io/stackfit."}
]
TOTAL_DURATION = 32.76
FPS = 30
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)

# Fonts
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# ----------------- 16:9 LANDSCAPE RENDERER (1920x1080) -----------------

def render_frame_16x9(frame_idx):
    t = frame_idx / FPS
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (12, 10, 9)) # Radar Dark
    draw = ImageDraw.Draw(img)

    # Subtle background grid & pulse
    pulse = (math.sin(t * 3) + 1) / 2
    accent_gold = (245, 158, 11)
    accent_green = (16, 185, 129)
    accent_red = (239, 68, 68)
    text_main = (245, 245, 244)
    text_muted = (168, 162, 158)
    card_bg = (28, 25, 23)
    border_col = (41, 37, 36)

    # Find current beat
    cur_beat = BEATS[-1]
    for b in BEATS:
        if b["start"] <= t < b["end"]:
            cur_beat = b
            break
    scene = cur_beat["scene"]
    scene_progress = (t - cur_beat["start"]) / (cur_beat["end"] - cur_beat["start"])

    # Top Brand Bar
    draw.rectangle([(0, 0), (w, 60)], fill=(18, 15, 14))
    draw.line([(0, 60), (w, 60)], fill=border_col, width=2)
    f_brand = get_font(FONT_BOLD, 22)
    draw.text((60, 18), "STACKFIT", font=f_brand, fill=text_main)
    draw.text((180, 18), "// ARCHITECTURAL RADAR", font=get_font(FONT_MONO, 18), fill=accent_gold)
    draw.text((w - 380, 20), "• 147 Verified Tools • Updated Daily", font=get_font(FONT_MONO, 16), fill=text_muted)

    # SCENE 1: THE PROBLEM (GITHUB STARS ARE BROKEN)
    if scene == 1:
        f_hero = get_font(FONT_BOLD, 64)
        draw.text((100, 140), "GITHUB STARS ARE BROKEN", font=f_hero, fill=accent_red)

        f_sub = get_font(FONT_REG, 28)
        draw.text((100, 225), "Cumulative lifetime stars are an unreliable vanity metric.", font=f_sub, fill=text_muted)

        # Card 1: The Broken Model
        draw.rounded_rectangle([(100, 310), (900, 720)], radius=20, fill=card_bg, outline=accent_red, width=3)
        draw.text((140, 350), "❌ THE VANITY STAR TRAP", font=get_font(FONT_BOLD, 26), fill=accent_red)
        draw.text((140, 410), "Repo: abandoned-framework-2020", font=get_font(FONT_MONO, 22), fill=text_main)
        draw.text((140, 460), "★ 85,400 Stars (Cumulative)", font=get_font(FONT_BOLD, 32), fill=(251, 191, 36))
        draw.text((140, 520), "• Last commit: 4 years ago (DEAD)", font=get_font(FONT_MONO, 20), fill=accent_red)
        draw.text((140, 560), "• Bot farm star bursts: Detected", font=get_font(FONT_MONO, 20), fill=accent_red)
        draw.text((140, 610), "Status: Legacy bloatware pushed to front page", font=get_font(FONT_REG, 20), fill=text_muted)

        # Card 2: The High Velocity Reality
        draw.rounded_rectangle([(1000, 310), (1800, 720)], radius=20, fill=card_bg, outline=accent_green, width=3)
        draw.text((1040, 350), "✅ TRUE ARCHITECTURAL VELOCITY", font=get_font(FONT_BOLD, 26), fill=accent_green)
        draw.text((1040, 410), "Repo: sgl-project / sglang", font=get_font(FONT_MONO, 22), fill=text_main)
        draw.text((1040, 460), "+1,500 Stars in last 24h", font=get_font(FONT_BOLD, 32), fill=accent_green)
        draw.text((1040, 520), "• Pushed 2 hours ago (ALIVE)", font=get_font(FONT_MONO, 20), fill=accent_green)
        draw.text((1040, 560), "• Verdict: Alt to vLLM (RadixAttention 3x faster)", font=get_font(FONT_REG, 20), fill=text_main)
        draw.text((1040, 610), "Status: Verified high-velocity adoption", font=get_font(FONT_REG, 20), fill=text_muted)

    # SCENE 2: THE HARDWARE REALITY CHECK
    elif scene == 2:
        draw.text((100, 140), "THE HARDWARE REALITY CHECK", font=get_font(FONT_BOLD, 64), fill=accent_gold)
        draw.text((100, 225), "Will your laptop or workstation actually run it?", font=get_font(FONT_REG, 28), fill=text_muted)

        # 3 Hardware Tier Cards
        tiers = [
            {"title": "CPU / Low RAM", "sub": "Runs on any laptop", "color": accent_green, "tool": "qdrant / llama.cpp (quantized)", "req": "Minimal RAM (4GB)", "x1": 100, "x2": 600},
            {"title": "Mac M-Series", "sub": "Apple Silicon (Metal)", "color": (56, 189, 248), "tool": "Ollama / LibreChat / MLX", "req": "Unified Memory 16GB-32GB", "x1": 660, "x2": 1160},
            {"title": "CUDA Clusters", "sub": "24GB+ VRAM required", "color": (236, 72, 153), "tool": "vLLM / ComfyUI / SGLang", "req": "⚡ Needs RTX 4090 or A100", "x1": 1220, "x2": 1720},
        ]
        for t_info in tiers:
            draw.rounded_rectangle([(t_info["x1"], 310), (t_info["x2"], 720)], radius=20, fill=card_bg, outline=t_info["color"], width=3)
            draw.text((t_info["x1"] + 30, 350), t_info["title"], font=get_font(FONT_BOLD, 28), fill=t_info["color"])
            draw.text((t_info["x1"] + 30, 400), t_info["sub"], font=get_font(FONT_REG, 20), fill=text_muted)
            draw.line([(t_info["x1"] + 30, 440), (t_info["x2"] - 30, 440)], fill=border_col, width=1)
            draw.text((t_info["x1"] + 30, 470), "Verified Tools:", font=get_font(FONT_MONO, 18), fill=text_muted)
            draw.text((t_info["x1"] + 30, 510), t_info["tool"], font=get_font(FONT_BOLD, 22), fill=text_main)
            draw.text((t_info["x1"] + 30, 580), "Floor Viability:", font=get_font(FONT_MONO, 18), fill=text_muted)
            draw.text((t_info["x1"] + 30, 620), t_info["req"], font=get_font(FONT_MONO, 20), fill=t_info["color"])

    # SCENE 3: MEET STACKFIT (THE MATCHMAKER)
    elif scene == 3:
        draw.text((100, 130), "MEET STACKFIT: THE MATCHMAKER", font=get_font(FONT_BOLD, 60), fill=accent_gold)
        draw.text((100, 215), "147+ Verified Repos • Architectural Verdicts • Incumbent Replacements", font=get_font(FONT_REG, 26), fill=text_muted)

        # 3 Real StackFit Cards
        repos = [
            {"cat": "RAG ENGINES", "name": "HKUDS / LightRAG", "verdict": "⚡ Alt to Microsoft GraphRAG — dual-level retrieval that is 10x faster & cheaper.", "v24": "+580 24h", "hw": "CPU + Local LLM"},
            {"cat": "LOCAL LLM ENGINES", "name": "sgl-project / sglang", "verdict": "⚡ Alt to vLLM — RadixAttention prefix caching delivers 3-5x higher throughput.", "v24": "+1,500 24h", "hw": "16GB-24GB+ CUDA"},
            {"cat": "VECTOR DATABASES", "name": "qdrant / qdrant", "verdict": "⚡ Alt to Pinecone — Rust-native vector search with zero cloud lock-in.", "v24": "+482 24h", "hw": "Runs on CPU / Low RAM"}
        ]
        for i, r in enumerate(repos):
            y1 = 280 + (i * 155)
            y2 = y1 + 140
            draw.rounded_rectangle([(100, y1), (1800, y2)], radius=16, fill=card_bg, outline=border_col, width=2)
            draw.rectangle([(100, y1), (112, y2)], fill=accent_gold)
            draw.text((135, y1 + 18), r["cat"], font=get_font(FONT_MONO, 16), fill=accent_gold)
            draw.text((360, y1 + 16), r["name"], font=get_font(FONT_BOLD, 24), fill=text_main)
            draw.text((135, y1 + 54), r["verdict"], font=get_font(FONT_REG, 20), fill=text_main)
            draw.text((135, y1 + 94), f"Hardware: {r['hw']}", font=get_font(FONT_MONO, 17), fill=text_muted)
            draw.rounded_rectangle([(1600, y1 + 45), (1760, y1 + 95)], radius=10, fill=(6, 43, 34), outline=accent_green, width=1)
            draw.text((1620, y1 + 58), r["v24"], font=get_font(FONT_BOLD, 22), fill=accent_green)

    # SCENE 4: HERO STACK ADVISOR
    elif scene == 4:
        draw.text((100, 140), "HERO STACK ADVISOR", font=get_font(FONT_BOLD, 64), fill=accent_green)
        draw.text((100, 225), "Select your laptop specs & engineering goal → Tested docker-compose.yml", font=get_font(FONT_REG, 28), fill=text_muted)

        # Input & Output boxes
        draw.rounded_rectangle([(100, 310), (800, 720)], radius=20, fill=card_bg, outline=border_col, width=2)
        draw.text((140, 350), "1. SELECT YOUR HARDWARE", font=get_font(FONT_BOLD, 24), fill=accent_gold)
        draw.rounded_rectangle([(140, 400), (760, 470)], radius=12, fill=(12, 10, 9), outline=accent_gold, width=2)
        draw.text((160, 422), "💻 Hardware Floor: Apple Silicon (Mac M3 / 16GB)", font=get_font(FONT_MONO, 18), fill=text_main)

        draw.text((140, 510), "2. ENGINEERING GOAL", font=get_font(FONT_BOLD, 24), fill=accent_gold)
        draw.rounded_rectangle([(140, 560), (760, 630)], radius=12, fill=(12, 10, 9), outline=accent_gold, width=2)
        draw.text((160, 582), "🎯 Intent: Private Local Code Assistant", font=get_font(FONT_MONO, 18), fill=text_main)

        # Output side
        draw.rounded_rectangle([(850, 310), (1800, 720)], radius=20, fill=card_bg, outline=accent_green, width=3)
        draw.text((890, 350), "⚡ OPTIMAL TESTED DEPLOYABLE STACK", font=get_font(FONT_BOLD, 24), fill=accent_green)
        draw.text((890, 405), "• Engine: Ollama (Q4_K_M quant on Metal GPU)", font=get_font(FONT_MONO, 20), fill=text_main)
        draw.text((890, 445), "• Vector DB: Qdrant (HNSW index in memory)", font=get_font(FONT_MONO, 20), fill=text_main)
        draw.text((890, 485), "• Workspace: LibreChat (ChatGPT clone with native MCP)", font=get_font(FONT_MONO, 20), fill=text_main)

        draw.rounded_rectangle([(890, 550), (1450, 640)], radius=12, fill=accent_green)
        draw.text((930, 578), "📋 COPY docker-compose.yml", font=get_font(FONT_BOLD, 28), fill=(12, 10, 9))
        draw.text((1480, 582), "One-Click Deploy", font=get_font(FONT_MONO, 20), fill=accent_green)

    # SCENE 5: CALL TO ACTION
    else:
        draw.text((w//2 - 450, 160), "STOP GUESSING. START BUILDING.", font=get_font(FONT_BOLD, 54), fill=accent_gold)
        draw.text((w//2 - 320, 240), "Find the open-source tools you actually need.", font=get_font(FONT_REG, 28), fill=text_muted)

        # Big URL Banner
        glow = int(20 + 20 * pulse)
        draw.rounded_rectangle([(300, 340), (1620, 540)], radius=25, fill=card_bg, outline=accent_gold, width=4)
        draw.text((360, 410), "siddharthakki.github.io/stackfit/", font=get_font(FONT_BOLD, 58), fill=text_main)

        # Features list
        draw.text((420, 600), "✓ 147+ Verified Repos", font=get_font(FONT_MONO, 24), fill=accent_green)
        draw.text((820, 600), "✓ No Vanity Stars", font=get_font(FONT_MONO, 24), fill=accent_green)
        draw.text((1220, 600), "✓ 100% Free & Open Source", font=get_font(FONT_MONO, 24), fill=accent_green)

        draw.text((w//2 - 160, 690), "⭐ Star on GitHub", font=get_font(FONT_BOLD, 30), fill=text_muted)

    # Kinetic Captions at Bottom
    caption_bg = (18, 15, 14)
    draw.rectangle([(0, 880), (w, 1060)], fill=caption_bg)
    draw.line([(0, 880), (w, 880)], fill=border_col, width=2)
    f_cap = get_font(FONT_BOLD, 28)
    draw.text((100, 930), f'"{cur_beat["caption"]}"', font=f_cap, fill=text_main)

    # Animated Progress Bar
    prog_pct = min(1.0, t / TOTAL_DURATION)
    draw.rectangle([(0, 1070), (w, 1080)], fill=(28, 25, 23))
    draw.rectangle([(0, 1070), (int(w * prog_pct), 1080)], fill=accent_gold)

    return np.array(img)

# ----------------- 9:16 VERTICAL RENDERER (1080x1920) -----------------

def render_frame_9x16(frame_idx):
    t = frame_idx / FPS
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), (12, 10, 9))
    draw = ImageDraw.Draw(img)

    accent_gold = (245, 158, 11)
    accent_green = (16, 185, 129)
    accent_red = (239, 68, 68)
    text_main = (245, 245, 244)
    text_muted = (168, 162, 158)
    card_bg = (28, 25, 23)
    border_col = (41, 37, 36)

    cur_beat = BEATS[-1]
    for b in BEATS:
        if b["start"] <= t < b["end"]:
            cur_beat = b
            break
    scene = cur_beat["scene"]

    # Top Brand Header
    draw.rectangle([(0, 0), (w, 120)], fill=(18, 15, 14))
    draw.line([(0, 120), (w, 120)], fill=border_col, width=2)
    draw.text((60, 42), "STACKFIT", font=get_font(FONT_BOLD, 38), fill=text_main)
    draw.text((290, 48), "// RADAR", font=get_font(FONT_MONO, 28), fill=accent_gold)

    # SCENE 1 (VERTICAL)
    if scene == 1:
        draw.text((60, 200), "GITHUB STARS", font=get_font(FONT_BOLD, 64), fill=accent_red)
        draw.text((60, 280), "ARE BROKEN.", font=get_font(FONT_BOLD, 64), fill=accent_red)
        draw.text((60, 370), "Bot farms & hype push dead repos.", font=get_font(FONT_REG, 30), fill=text_muted)

        draw.rounded_rectangle([(60, 470), (1020, 920)], radius=24, fill=card_bg, outline=accent_red, width=4)
        draw.text((100, 520), "❌ THE VANITY TRAP", font=get_font(FONT_BOLD, 34), fill=accent_red)
        draw.text((100, 590), "★ 85,000 Cumulative Stars", font=get_font(FONT_BOLD, 42), fill=(251, 191, 36))
        draw.text((100, 670), "• Abandoned in 2021 (DEAD)", font=get_font(FONT_MONO, 28), fill=accent_red)
        draw.text((100, 730), "• High-velocity tools buried", font=get_font(FONT_REG, 28), fill=text_muted)
        draw.text((100, 790), "• Algorithm rewards legacy inertia", font=get_font(FONT_REG, 28), fill=text_muted)

        draw.rounded_rectangle([(60, 980), (1020, 1430)], radius=24, fill=card_bg, outline=accent_green, width=4)
        draw.text((100, 1030), "✅ STACKFIT MOMENTUM", font=get_font(FONT_BOLD, 34), fill=accent_green)
        draw.text((100, 1100), "+1,500 Stars in 24h", font=get_font(FONT_BOLD, 42), fill=accent_green)
        draw.text((100, 1180), "• Commit pushed 3h ago", font=get_font(FONT_MONO, 28), fill=accent_green)
        draw.text((100, 1240), "• Tested architecture verdicts", font=get_font(FONT_REG, 28), fill=text_main)
        draw.text((100, 1300), "• Real developer adoption", font=get_font(FONT_REG, 28), fill=text_muted)

    # SCENE 2 (VERTICAL)
    elif scene == 2:
        draw.text((60, 200), "THE HARDWARE", font=get_font(FONT_BOLD, 64), fill=accent_gold)
        draw.text((60, 280), "REALITY CHECK", font=get_font(FONT_BOLD, 64), fill=accent_gold)
        draw.text((60, 370), "Can your laptop actually run it?", font=get_font(FONT_REG, 30), fill=text_muted)

        hws = [
            {"name": "🧠 CPU Only / Low RAM", "color": accent_green, "tool": "Runs on any laptop (4GB RAM)"},
            {"name": "💻 Mac M-Series (Metal)", "color": (56, 189, 248), "tool": "Apple Silicon (16GB-32GB)"},
            {"name": "⚡ 24GB+ CUDA Clusters", "color": (236, 72, 153), "tool": "Needs A100 or RTX 4090"}
        ]
        for i, h_info in enumerate(hws):
            y = 480 + (i * 300)
            draw.rounded_rectangle([(60, y), (1020, y + 260)], radius=24, fill=card_bg, outline=h_info["color"], width=4)
            draw.text((100, y + 40), h_info["name"], font=get_font(FONT_BOLD, 36), fill=h_info["color"])
            draw.text((100, y + 110), h_info["tool"], font=get_font(FONT_MONO, 28), fill=text_main)
            draw.text((100, y + 170), "Tagged explicitly on every tool", font=get_font(FONT_REG, 24), fill=text_muted)

    # SCENE 3 (VERTICAL)
    elif scene == 3:
        draw.text((60, 200), "MEET STACKFIT", font=get_font(FONT_BOLD, 64), fill=accent_gold)
        draw.text((60, 280), "THE MATCHMAKER", font=get_font(FONT_BOLD, 64), fill=text_main)
        draw.text((60, 370), "What it replaces & what it runs on.", font=get_font(FONT_REG, 30), fill=text_muted)

        tools = [
            {"cat": "LOCAL LLM ENGINES", "name": "sglang (+1,500 24h)", "rep": "Replaces: vLLM (RadixAttention)"},
            {"cat": "RAG ENGINES", "name": "LightRAG (+580 24h)", "rep": "Replaces: Microsoft GraphRAG"},
            {"cat": "VECTOR DBS", "name": "Qdrant (+482 24h)", "rep": "Replaces: Pinecone (Zero lock-in)"},
            {"cat": "AI CHAT UI", "name": "LibreChat (+315 24h)", "rep": "Replaces: ChatGPT Team / Bedrock"}
        ]
        for i, t_info in enumerate(tools):
            y = 470 + (i * 225)
            draw.rounded_rectangle([(60, y), (1020, y + 195)], radius=20, fill=card_bg, outline=border_col, width=2)
            draw.rectangle([(60, y), (74, y + 195)], fill=accent_gold)
            draw.text((100, y + 25), t_info["cat"], font=get_font(FONT_MONO, 22), fill=accent_gold)
            draw.text((100, y + 65), t_info["name"], font=get_font(FONT_BOLD, 34), fill=text_main)
            draw.text((100, y + 125), t_info["rep"], font=get_font(FONT_REG, 26), fill=accent_green)

    # SCENE 4 (VERTICAL)
    elif scene == 4:
        draw.text((60, 200), "HERO STACK", font=get_font(FONT_BOLD, 64), fill=accent_green)
        draw.text((60, 280), "ADVISOR", font=get_font(FONT_BOLD, 64), fill=accent_green)
        draw.text((60, 370), "Select specs → 1-click docker-compose", font=get_font(FONT_REG, 30), fill=text_muted)

        draw.rounded_rectangle([(60, 480), (1020, 1380)], radius=24, fill=card_bg, outline=accent_green, width=4)
        draw.text((100, 530), "TESTED PRIVATE AI STACK", font=get_font(FONT_BOLD, 36), fill=accent_green)
        draw.text((100, 610), "Target: Mac M3 / 16GB VRAM", font=get_font(FONT_MONO, 28), fill=accent_gold)
        draw.line([(100, 670), (980, 670)], fill=border_col, width=2)
        draw.text((100, 710), "1. Ollama (Local LLM Inference)", font=get_font(FONT_BOLD, 30), fill=text_main)
        draw.text((100, 790), "2. Qdrant (Rust Vector Database)", font=get_font(FONT_BOLD, 30), fill=text_main)
        draw.text((100, 870), "3. LibreChat (Multi-model UI)", font=get_font(FONT_BOLD, 30), fill=text_main)

        draw.rounded_rectangle([(100, 990), (980, 1130)], radius=16, fill=accent_green)
        draw.text((180, 1035), "📋 COPY docker-compose.yml", font=get_font(FONT_BOLD, 34), fill=(12, 10, 9))
        draw.text((100, 1200), "✓ Tested & deployable in 30 seconds", font=get_font(FONT_MONO, 26), fill=text_muted)

    # SCENE 5 (VERTICAL)
    else:
        draw.text((60, 280), "STOP GUESSING.", font=get_font(FONT_BOLD, 68), fill=text_main)
        draw.text((60, 370), "START BUILDING.", font=get_font(FONT_BOLD, 68), fill=accent_gold)

        draw.rounded_rectangle([(60, 520), (1020, 980)], radius=24, fill=card_bg, outline=accent_gold, width=4)
        draw.text((100, 580), "EXPLORE STACKFIT:", font=get_font(FONT_BOLD, 32), fill=accent_gold)
        draw.text((100, 670), "siddharthakki.github.io", font=get_font(FONT_BOLD, 42), fill=text_main)
        draw.text((100, 740), "/stackfit/", font=get_font(FONT_BOLD, 46), fill=accent_gold)
        draw.text((100, 840), "• 147+ Verified Tools", font=get_font(FONT_MONO, 28), fill=accent_green)
        draw.text((100, 900), "• 100% Free & Open-Source", font=get_font(FONT_MONO, 28), fill=accent_green)

        draw.rounded_rectangle([(160, 1080), (920, 1210)], radius=16, fill=(18, 15, 14), outline=accent_gold, width=2)
        draw.text((260, 1125), "⭐ Star on GitHub", font=get_font(FONT_BOLD, 38), fill=accent_gold)

    # Captions at Bottom (Vertical)
    draw.rectangle([(0, 1540), (w, 1880)], fill=(18, 15, 14))
    draw.line([(0, 1540), (w, 1540)], fill=border_col, width=2)
    draw.text((60, 1600), f'"{cur_beat["caption"]}"', font=get_font(FONT_BOLD, 32), fill=text_main)

    # Progress bar
    prog_pct = min(1.0, t / TOTAL_DURATION)
    draw.rectangle([(0, 1890), (w, 1920)], fill=(28, 25, 23))
    draw.rectangle([(0, 1890), (int(w * prog_pct), 1920)], fill=accent_gold)

    return np.array(img)

def render_video(is_vertical=False):
    output_file = OUTPUT_9X16 if is_vertical else OUTPUT_16X9
    res = "1080x1920" if is_vertical else "1920x1080"
    renderer = render_frame_9x16 if is_vertical else render_frame_16x9
    mode_name = "9:16 Vertical (Shorts/TikTok/Reels)" if is_vertical else "16:9 Landscape (YouTube/Twitter/LinkedIn)"

    print(f"\n🎬 Rendering {mode_name} to {output_file}...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", res, "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO_PATH,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_file
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(TOTAL_FRAMES):
        frame = renderer(i)
        proc.stdin.write(frame.tobytes())
        if i % 150 == 0:
            print(f"  Frame {i}/{TOTAL_FRAMES} ({(i/TOTAL_FRAMES)*100:.1f}%)")

    proc.stdin.close()
    proc.wait()
    print(f"✅ Generated {output_file} successfully! (Exit code: {proc.returncode})")

def main():
    if not os.path.exists(AUDIO_PATH):
        print(f"Error: audio not found at {AUDIO_PATH}")
        sys.exit(1)

    os.makedirs("assets", exist_ok=True)
    # Render Landscape (16:9)
    render_video(is_vertical=False)
    # Render Vertical (9:16)
    render_video(is_vertical=True)

if __name__ == "__main__":
    main()
