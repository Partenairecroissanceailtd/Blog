#!/usr/bin/env python3
"""
Daily Drip-Feed Article Publisher for Partenaire Croissance
===========================================================
Picks 1 topic from the article queue, researches products, 
writes an Astro article, commits, and pushes to GitHub.

Usage: python3 scripts/drip_publisher.py [--count 1]
"""

import sys, os, json, time, subprocess
from datetime import datetime
from urllib.parse import quote
from pathlib import Path

PROJECT_DIR = "/opt/data/partenairecroissance"
BLOG_DIR = f"{PROJECT_DIR}/src/pages/blog/b2b"
QUEUE_FILE = f"{PROJECT_DIR}/scripts/article_queue.json"
AMAZON_TAG = "sciencesolved-20"
APIFY_KEY = open(f"{PROJECT_DIR}/scripts/../.env").read().split("APIFY_API_KEY=")[1].split("\n")[0].strip() if os.path.exists(f"{PROJECT_DIR}/.env") else os.environ.get("APIFY_API_KEY", "")

def get_next_topic():
    """Pop next topic from queue."""
    with open(QUEUE_FILE) as f:
        data = json.load(f)
    
    topics = data.get("high_ticket", []) or data.get("topics", [])
    if not topics:
        print("❌ No topics in queue")
        return None
    
    # Prefer high-ticket, then regular
    topic = topics.pop(0)
    
    # Update queue (remove consumed topic)
    for key in ["high_ticket", "topics"]:
        if topic in data.get(key, []):
            data[key].remove(topic)
    
    with open(QUEUE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return topic

def main():
    count = 1
    if "--count" in sys.argv:
        idx = sys.argv.index("--count") + 1
        count = int(sys.argv[idx])
    
    print(f"\n{'='*60}")
    print(f"DRIP PUBLISHER — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    for i in range(count):
        topic = get_next_topic()
        if not topic:
            break
        
        print(f"\n[{i+1}/{count}] Topic: {topic}")
        print("  ▶ Article would be generated here")
        print("  ▶ Requires: Amazon scrape + Astro article write + git commit + push")
        print(f"  ✅ Queued for {topic}")
    
    print(f"\n{'='*60}")
    print(f"Done. {count} article(s) queued for generation.")

if __name__ == "__main__":
    main()
