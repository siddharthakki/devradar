"""
DevRadar RSS & Static API Exporter
Generates standard RSS 2.0 XML and split category API endpoints.
"""
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime

BASE_URL = "https://siddharthakki.github.io/devradar"

def generate_rss_and_endpoints():
    data_path = os.path.join("data", "repos.json")
    if not os.path.exists(data_path):
        print("data/repos.json not found, skipping distribution generation.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    repos = data.get("repositories", [])
    now = datetime.now(timezone.utc)
    pub_date_str = format_datetime(now)

    # ------------------ RSS 2.0 FEED ------------------
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "DevRadar // Breakout Open Source Pulse"
    ET.SubElement(channel, "link").text = BASE_URL
    ET.SubElement(channel, "description").text = "Hourly stream tracking high-velocity, authentic GitHub projects across 20 high-signal disciplines."
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = pub_date_str

    # Top 15 breakout tools
    breakout_items = sorted(repos, key=lambda x: x.get("trending_score", 0), reverse=True)[:15]

    for r in breakout_items:
        item = ET.SubElement(channel, "item")
        full_name = r.get("full_name") or r.get("name") or "Unknown"
        ET.SubElement(item, "title").text = f"[{r.get('category', 'Core')}] {full_name} (+{r.get('stars_24h', 0)} 24h)"
        ET.SubElement(item, "link").text = r.get("url", BASE_URL)
        ET.SubElement(item, "guid").text = r.get("url", full_name)
        ET.SubElement(item, "pubDate").text = pub_date_str
        
        desc = (
            f"<p>{r.get('description', '')}</p>"
            f"<ul>"
            f"<li><b>Stars:</b> ⭐ {r.get('stars', 0):,} (+{r.get('stars_24h', 0)} in 24h)</li>"
            f"<li><b>Authenticity:</b> {r.get('authenticity_score', 95)}% Organic</li>"
            f"<li><b>Hardware Viability:</b> {r.get('hardware_req', 'Minimal')}</li>"
            f"<li><b>Quick Run:</b> <code>{r.get('quick_run', 'git clone ' + r.get('url', ''))}</code></li>"
            f"</ul>"
        )
        ET.SubElement(item, "description").text = desc

    tree = ET.ElementTree(rss)
    feed_path = os.path.join("data", "feed.xml")
    tree.write(feed_path, encoding="utf-8", xml_declaration=True)
    print(f"Generated {feed_path}")

    # ------------------ STATIC API SLICES ------------------
    api_dir = os.path.join("data", "v1")
    cat_dir = os.path.join(api_dir, "categories")
    os.makedirs(cat_dir, exist_ok=True)

    # 1. meta.json
    meta = {
        "version": "1.0",
        "generated_at": now.isoformat(),
        "total_repositories": len(repos),
        "endpoints": {
            "all": f"{BASE_URL}/data/repos.json",
            "rss": f"{BASE_URL}/data/feed.xml",
            "categories": f"{BASE_URL}/data/v1/categories/"
        }
    }
    with open(os.path.join(api_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # 2. Category files
    categories = set(r.get("category") for r in repos if r.get("category"))
    for cat in categories:
        safe_name = cat.lower().replace(" & ", "-").replace(" ", "-").replace("/", "-")
        cat_items = [r for r in repos if r.get("category") == cat]
        payload = {
            "category": cat,
            "count": len(cat_items),
            "updated_at": now.isoformat(),
            "repositories": cat_items
        }
        with open(os.path.join(cat_dir, f"{safe_name}.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    print(f"Generated API endpoints across {len(categories)} categories.")

if __name__ == "__main__":
    generate_rss_and_endpoints()
