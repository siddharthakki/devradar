#!/usr/bin/env python3
"""
DevRadar Terminal CLI
Query live breakout open-source projects right from your shell.
Usage: python cli.py [--top 10] [--category "Local LLM Engines"]
"""
import argparse, json, urllib.request

DATA_URL = "https://raw.githubusercontent.com/siddharthakki/devradar/main/data/repos.json"

def main():
    parser = argparse.ArgumentParser(description="DevRadar Terminal Client")
    parser.add_argument("--top", type=int, default=10, help="Number of repositories to display")
    parser.add_argument("--category", type=str, default=None, help="Filter by category")
    args = parser.parse_args()

    try:
        req = urllib.request.Request(DATA_URL, headers={"User-Agent": "devradar-cli"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error fetching DevRadar data: {e}")
        return

    repos = data.get("repositories", [])
    if args.category:
        repos = [r for r in repos if args.category.lower() in r.get("category", "").lower()]

    print("\n\033[1;36m🛰️  DEVRADAR — BREAKOUT OPEN-SOURCE LEADERBOARD\033[0m\n")
    print(f"{'Stars':<10} {'24h Velocity':<14} {'Authenticity':<14} {'Repository':<35} {'Specs'}")
    print("-" * 90)

    for r in repos[:args.top]:
        stars = f"⭐ {r.get('stars', 0):,}"
        v24 = f"+{r.get('stars_24h', 0)} 24h"
        auth = f"🛡️ {r.get('authenticity_score', 95)}%"
        name = r.get("full_name", r.get("name", "Unknown"))[:34]
        hw = r.get("hardware_req", "Minimal")
        print(f"{stars:<10} {v24:<14} {auth:<14} {name:<35} {hw}")

    print("\nExplore full visual dashboard: https://siddharthakki.github.io/devradar/\n")

if __name__ == "__main__":
    main()
