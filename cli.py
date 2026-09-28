#!/usr/bin/env python3
"""
StackFit Terminal CLI
Query live breakout open-source projects, architectural verdicts & hardware requirements right from your shell.
Usage: python cli.py [--top 10] [--category "Local LLM Engines"]
"""
import argparse, json, urllib.request, os, sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

DATA_URL = "https://raw.githubusercontent.com/siddharthakki/devradar/main/data/repos.json"

def main():
    parser = argparse.ArgumentParser(description="StackFit Terminal Client")
    parser.add_argument("--top", type=int, default=10, help="Number of repositories to display")
    parser.add_argument("--category", type=str, default=None, help="Filter by category")
    parser.add_argument("--daily", action="store_true", help="Display daily briefing organized by stack/discipline")
    parser.add_argument("--local", action="store_true", help="Read from local data/repos.json")
    args = parser.parse_args()

    data = None
    if args.local or os.path.exists("data/repos.json"):
        try:
            with open("data/repos.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    if not data:
        try:
            req = urllib.request.Request(DATA_URL, headers={"User-Agent": "stackfit-cli"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error fetching StackFit data: {e}")
            return

    repos = data.get("repositories", [])

    if args.daily:
        from collections import defaultdict
        by_cat = defaultdict(list)
        for r in repos:
            by_cat[r.get('category', 'Other')].append(r)

        print("\n\033[1;33m⚡ STACKFIT DAILY STACK RADAR — WHAT'S NEW TODAY\033[0m")
        print("\033[0;90mTop daily breakthroughs across every core AI & software discipline.\033[0m\n")

        for cat, items in sorted(by_cat.items()):
            items.sort(key=lambda x: (x.get('stars_24h', 0) or 0), reverse=True)
            top = items[0]
            print(f"\033[1;36m▶ {cat.upper()}\033[0m")
            print(f"  \033[1;37m{top.get('name')}\033[0m \033[0;32m(+{top.get('stars_24h')} 24h)\033[0m  ★ {top.get('stars', 0):,}  \033[0;35m[{top.get('signal_badge', '').upper()}]\033[0m")
            print(f"  • \033[1;33mVerdict:\033[0m {top.get('verdict')}")
            print(f"  • \033[1;90mReplaces:\033[0m {top.get('replaces')}")
            print(f"  • \033[1;90mHardware:\033[0m {top.get('hardware_alert') or top.get('hardware_req')}")
            if len(items) > 1:
                others = [f"{o.get('name')} (+{o.get('stars_24h')})" for o in items[1:3]]
                print(f"  • \033[0;90mAlso trending:\033[0m {', '.join(others)}")
            print()

        print("Explore live interactive stacks: https://siddharthakki.github.io/devradar/\n")
        return

    if args.category:
        repos = [r for r in repos if args.category.lower() in r.get("category", "").lower()]

    print("\n\033[1;33m⚡ STACKFIT — ARCHITECTURAL VERDICTS & BREAKOUT RADAR\033[0m")
    print("\033[0;90mFind the open-source tool you actually need — by what it replaces and runs on.\033[0m\n")
    print(f"{'Stars':<9} {'24h Move':<12} {'Signal':<11} {'Repository':<26} {'Replaces':<20} {'Hardware'}")
    print("-" * 105)

    for r in repos[:args.top]:
        stars = f"★ {r.get('stars', 0):,}"
        v24 = f"+{r.get('stars_24h', 0)} 24h"
        sig = f"[{r.get('signal_badge', 'climber').upper()}]"
        name = (r.get("name") or "Unknown")[:24]
        rep = (r.get("replaces") or "Incumbents")[:18]
        hw = (r.get("hardware_alert") or r.get("hardware_req") or "Minimal")[:22]
        print(f"{stars:<9} {v24:<12} {sig:<11} {name:<26} {rep:<20} {hw}")

    print("\nExplore live interactive stack builder: https://siddharthakki.github.io/devradar/\n")

if __name__ == "__main__":
    main()
