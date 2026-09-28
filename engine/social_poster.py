"""
StackFit Automated Social Broadcast Engine
Autonomous multi-platform distribution to 𝕏 (Twitter), Bluesky, Discord, Slack, Telegram, and Reddit.
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://siddharthakki.github.io/stackfit/"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "repos.json")

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("repositories", [])

def format_spiker_post(repos):
    """Generate high-converting post for the top 24h breakout tool."""
    spikers = sorted(repos, key=lambda x: x.get("stars_24h", 0), reverse=True)
    if not spikers:
        return None
    top = spikers[0]
    second = spikers[1] if len(spikers) > 1 else None

    name = top.get("full_name") or top.get("name")
    short_name = top.get("name")
    v24 = top.get("stars_24h", 0)
    verdict = top.get("verdict", "")
    replaces = top.get("replaces", "Incumbents")
    hw = top.get("hardware_alert") or top.get("hardware_req", "Minimal CPU")
    stars = top.get("stars", 0)
    repo_url = f"{BASE_URL}#repo/{urllib.parse.quote(short_name.lower())}"

    # Twitter / Bluesky format (<300 chars)
    short_text = (
        f"⚡ Today's #1 Open-Source Mover: {short_name} (+{v24} in 24h)\n\n"
        f"Verdict: {verdict}\n"
        f"• Replaces: {replaces}\n"
        f"• Hardware: {hw}\n\n"
        f"Explore full architecture specs without star vanity:\n"
        f"{repo_url}\n\n"
        f"#OpenSource #DevTools #AI"
    )

    # Long markdown format (Discord, Slack, Reddit)
    long_markdown = (
        f"### ⚡ Today's StackFit Radar Spiker: [{name}]({top.get('url', repo_url)})\n\n"
        f"> **Architectural Verdict:** {verdict}\n\n"
        f"- **24h Momentum:** `+{v24:,} stars` (Total: ★ {stars:,})\n"
        f"- **Replaces:** `{replaces}`\n"
        f"- **Hardware Floor:** `{hw}`\n"
        f"- **Why this week:** {top.get('why_this_week', 'Breakout velocity')}\n\n"
        f"Explore interactive side-by-side comparison & hardware advisor at [StackFit]({BASE_URL})"
    )

    return {
        "title": f"⚡ Today's #1 Spiking Tool: {name} (+{v24} 24h)",
        "short_text": short_text,
        "long_markdown": long_markdown,
        "repo": top
    }

def format_stack_post():
    """Generate post highlighting a recommended deployable stack."""
    short_text = (
        f"🛠️ Stack of the Day: Private Local AI Assistant\n\n"
        f"• Engine: Ollama (Apple Silicon & CPU quant)\n"
        f"• Storage: Qdrant (Rust vector DB, zero lock-in)\n"
        f"• Interface: LibreChat (ChatGPT clone with native MCP)\n\n"
        f"1-click docker-compose & hardware specs:\n"
        f"{BASE_URL}\n\n"
        f"#SelfHosted #Docker #LocalAI #DevTools"
    )
    return {
        "title": "🛠️ Stack of the Day: Private Local AI Assistant",
        "short_text": short_text,
        "long_markdown": short_text
    }

# ----------------- DISPATCHERS -----------------

def post_to_bluesky(text):
    """Post to Bluesky via AT Protocol HTTP API."""
    handle = os.environ.get("BLUESKY_HANDLE")
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not handle or not password:
        return {"status": "skipped", "message": "Missing BLUESKY_HANDLE or BLUESKY_APP_PASSWORD"}

    try:
        # Create session
        session_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
        session_payload = json.dumps({"identifier": handle, "password": password}).encode("utf-8")
        req = urllib.request.Request(session_url, data=session_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            session = json.loads(resp.read().decode("utf-8"))

        access_jwt = session["accessJwt"]
        did = session["did"]

        # Post record
        record_url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        post_payload = json.dumps({
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text[:300],
                "createdAt": now_iso
            }
        }).encode("utf-8")

        post_req = urllib.request.Request(
            record_url,
            data=post_payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {access_jwt}"}
        )
        with urllib.request.urlopen(post_req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return {"status": "success", "uri": res.get("uri")}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def post_to_discord(content_dict):
    """Post rich embed to Discord webhook."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return {"status": "skipped", "message": "Missing DISCORD_WEBHOOK_URL"}

    repo = content_dict.get("repo", {})
    payload = {
        "content": "⚡ **StackFit Daily Breakout Broadcast**",
        "embeds": [{
            "title": content_dict.get("title", "StackFit Radar Update"),
            "url": BASE_URL,
            "description": repo.get("verdict", content_dict.get("short_text")),
            "color": 16103435, # Amber
            "fields": [
                {"name": "Replaces", "value": repo.get("replaces", "Incumbents"), "inline": True},
                {"name": "24h Move", "value": f"+{repo.get('stars_24h', 0):,}", "inline": True},
                {"name": "Hardware", "value": repo.get("hardware_alert", "Minimal CPU"), "inline": False}
            ],
            "footer": {"text": "StackFit • Architectural Matchmaker without Star Vanity"}
        }]
    }

    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "StackFitBroadcast/1.0"}
        )
        with urllib.request.urlopen(req) as resp:
            return {"status": "success", "code": resp.status}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def post_to_slack(content_dict):
    """Post Block Kit alert to Slack webhook."""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL") or os.environ.get("STACKFIT_WEBHOOK_URL")
    if not webhook_url:
        return {"status": "skipped", "message": "Missing SLACK_WEBHOOK_URL"}

    payload = {"text": content_dict.get("short_text", "")}
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            return {"status": "success", "code": resp.status}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def post_to_twitter(text):
    """Post to Twitter via OAuth 1.0a credentials if configured."""
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    token = os.environ.get("TWITTER_ACCESS_TOKEN")
    token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, token, token_secret]):
        return {"status": "skipped", "message": "Missing Twitter/X API credentials (TWITTER_API_KEY, TWITTER_ACCESS_TOKEN, etc.)"}

    try:
        import hmac
        import hashlib
        import base64
        import time
        import secrets

        url = "https://api.twitter.com/2/tweets"
        method = "POST"
        nonce = secrets.token_hex(16)
        timestamp = str(int(time.time()))

        params = {
            "oauth_consumer_key": api_key,
            "oauth_nonce": nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": timestamp,
            "oauth_token": token,
            "oauth_version": "1.0"
        }

        # Build base signature string
        sorted_params = "&".join(f"{k}={urllib.parse.quote(params[k], safe='')}" for k in sorted(params))
        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
        signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}".encode("utf-8")
        signature = base64.b64encode(hmac.new(signing_key, base_string.encode("utf-8"), hashlib.sha1).digest()).decode("utf-8")
        params["oauth_signature"] = signature

        auth_header = "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(params[k], safe="")}"' for k in sorted(params))
        payload = json.dumps({"text": text[:280]}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": auth_header}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ----------------- MAIN CLI -----------------

def main():
    parser = argparse.ArgumentParser(description="StackFit Automated Social Broadcast Engine")
    parser.add_argument("--topic", choices=["spiker", "stack"], default="spiker", help="Type of post to generate")
    parser.add_argument("--dry-run", action="store_true", help="Print post copy without broadcasting")
    parser.add_argument("--post", action="store_true", help="Broadcast to all configured social channels")
    args = parser.parse_args()

    repos = load_data()
    content = format_spiker_post(repos) if args.topic == "spiker" else format_stack_post()

    print("\n" + "=" * 60)
    print("⚡ STACKFIT SOCIAL BROADCAST PREVIEW")
    print("=" * 60)
    print(f"\n[SHORT POST (𝕏 / Bluesky)]:\n{content['short_text']}")
    print(f"\n[LONG POST (Discord / Slack / Reddit)]:\n{content['long_markdown']}")
    print("=" * 60 + "\n")

    if args.dry_run or not args.post:
        print("💡 Dry run mode complete. Run with '--post' to broadcast to configured APIs.")
        return

    print("🚀 Broadcasting across configured networks...")

    # 1. Bluesky
    res_bsky = post_to_bluesky(content["short_text"])
    print(f"• Bluesky: {res_bsky['status']} {res_bsky.get('message', res_bsky.get('uri', ''))}")

    # 2. Twitter / 𝕏
    res_tw = post_to_twitter(content["short_text"])
    print(f"• 𝕏 / Twitter: {res_tw['status']} {res_tw.get('message', res_tw.get('data', ''))}")

    # 3. Discord
    res_dc = post_to_discord(content)
    print(f"• Discord: {res_dc['status']} {res_dc.get('message', '')}")

    # 4. Slack
    res_sl = post_to_slack(content)
    print(f"• Slack: {res_sl['status']} {res_sl.get('message', '')}")

if __name__ == "__main__":
    main()
