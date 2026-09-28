#!/usr/bin/env python3
"""
StackFit Webhook Dispatcher
Dispatches high-velocity breakout alerts and weekly digests to Slack or Discord.
Usage: python engine/notify.py [--test] [--webhook <URL>]
"""
import json
import os
import sys
import urllib.request
import urllib.error

def send_webhook(webhook_url, payload):
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "StackFit-Dispatcher/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"Webhook HTTP error: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"Webhook failed: {e}")
        return False

def build_slack_payload(top_mover, watched=None):
    watched = watched or []
    name = top_mover.get("full_name") or top_mover.get("name")
    verdict = top_mover.get("verdict", "")
    replaces = top_mover.get("replaces", "Incumbent tools")
    stars = top_mover.get("stars", 0)
    v24 = top_mover.get("stars_24h", 0)
    hw = top_mover.get("hardware_alert") or top_mover.get("hardware_req", "Minimal CPU")
    url = top_mover.get("url", "https://siddharthakki.github.io/stackfit/")

    text = f"⚡ *StackFit Architectural Alert: Spiking Today (+{v24} 24h)*\n"
    text += f"*<{url}|{name}>* &bull; ★ {stars:,}\n"
    text += f"> {verdict}\n"
    text += f"*Replaces:* `{replaces}` | *Hardware:* `{hw}`\n"
    text += f"Explore live interactive stack: <https://siddharthakki.github.io/stackfit/|StackFit Matchmaker>"

    return {"text": text}

def main():
    webhook_url = os.environ.get("STACKFIT_WEBHOOK_URL") or os.environ.get("SLACK_WEBHOOK_URL")
    if len(sys.argv) > 1 and sys.argv[1] == "--webhook" and len(sys.argv) > 2:
        webhook_url = sys.argv[2]

    if not webhook_url:
        print("No STACKFIT_WEBHOOK_URL or SLACK_WEBHOOK_URL environment variable found. Skipping webhook.")
        return

    data_path = os.path.join("data", "repos.json")
    if not os.path.exists(data_path):
        print("data/repos.json not found.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    repos = data.get("repositories", [])
    if not repos:
        print("No repositories available to dispatch.")
        return

    # Sort by 24h momentum
    top_mover = sorted(repos, key=lambda x: x.get("stars_24h", 0), reverse=True)[0]
    payload = build_slack_payload(top_mover)

    success = send_webhook(webhook_url, payload)
    if success:
        print(f"Successfully dispatched StackFit alert to webhook for {top_mover.get('name')}.")
    else:
        print("Failed to dispatch alert to webhook.")

if __name__ == "__main__":
    main()
