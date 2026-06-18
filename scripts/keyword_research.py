#!/usr/bin/env python3
"""
Frugal Keyword Research Tool for Partenaire Croissance
======================================================
Uses free Google Autocomplete API (no API key needed) + optional Apify Google SERP scraper
to validate niche demand before writing articles.

Usage:
  python3 keyword_research.py "best tool box"          # Single keyword
  python3 keyword_research.py --batch niches.txt       # Batch from file
  python3 keyword_research.py --apify                  # Also run Apify SERP check
"""

import urllib.request, json, sys, os, time
from urllib.parse import quote

APIFY_KEY = os.environ.get("APIFY_API_KEY", "")

def google_autocomplete(seed: str, limit: int = 10) -> list:
    """Free: Google Autocomplete API — returns related search queries."""
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={quote(seed)}"
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        data = json.loads(resp.read().decode())
        suggestions = [s for s in data[1][:limit]] if len(data) > 1 else []
        return suggestions
    except Exception as e:
        print(f"  ⚠ Autocomplete error: {e}")
        return []

def google_serp_check(niche: str) -> dict:
    """Paid (Apify credits): SERP analysis — PAA, related, competitors."""
    if not APIFY_KEY:
        return {"error": "No APIFY_API_KEY set"}
    
    payload = json.dumps({
        "queries": niche,
        "maxPagesPerQuery": 1,
        "resultsLanguage": "en",
        "countryCode": "us"
    })
    
    url = f"https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items?token={APIFY_KEY}"
    try:
        resp = urllib.request.urlopen(
            urllib.request.Request(url, data=payload.encode(), headers={'Content-Type': 'application/json'}, method='POST'),
            timeout=120
        )
        items = json.loads(resp.read().decode())
        serp = items[0] if items else {}
        return {
            "organic_count": len(serp.get("organicResults", [])),
            "paa_count": len(serp.get("peopleAlsoAsk", [])),
            "related_count": len(serp.get("relatedSearches", [])),
            "has_ads": len(serp.get("ads", [])) > 0,
            "top_titles": [r.get("title","")[:80] for r in serp.get("organicResults", [])[:5]],
            "paa_questions": [q.get("question", "") for q in serp.get("peopleAlsoAsk", [])[:5]],
        }
    except Exception as e:
        return {"error": str(e)}

def analyze_niche(niche: str, use_apify: bool = False) -> dict:
    """Full niche analysis with demand scoring."""
    result = {"niche": niche, "score": 0, "max_score": 3}
    
    # 1. Autocomplete check (free)
    suggestions = google_autocomplete(niche)
    result["autocomplete_suggestions"] = suggestions
    result["autocomplete_count"] = len(suggestions)
    if len(suggestions) >= 8:
        result["score"] += 3
    elif len(suggestions) >= 5:
        result["score"] += 2
    elif len(suggestions) >= 2:
        result["score"] += 1
    
    # Update max when Apify is used
    if use_apify:
        result["max_score"] = 8
        serp = google_serp_check(niche)
        result["serp"] = serp
        if not serp.get("error"):
            if serp.get("paa_count", 0) >= 3:
                result["score"] += 2
            if serp.get("related_count", 0) >= 5:
                result["score"] += 2
            if serp.get("organic_count", 0) >= 5:
                result["score"] += 1
    
    # Auto-grade
    pct = (result["score"] / result["max_score"]) * 100 if result["max_score"] > 0 else 0
    if pct >= 70:
        result["grade"] = "✅ HIGH — Write articles"
    elif pct >= 40:
        result["grade"] = "⚠️ MEDIUM — Check products available"
    else:
        result["grade"] = "❌ LOW — Skip niche"
    
    return result

def main():
    use_apify = "--apify" in sys.argv
    
    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch") + 1
        with open(sys.argv[idx]) as f:
            niches = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        niches = [sys.argv[1]]
    else:
        print("Usage: keyword_research.py <keyword> [--apify]")
        print("       keyword_research.py --batch niches.txt [--apify]")
        sys.exit(1)
    
    print(f"{'='*60}")
    print(f"KEYWORD RESEARCH — {len(niches)} niches")
    print(f"{'='*60}")
    
    for niche in niches:
        print(f"\n--- Analyzing: {niche} ---")
        result = analyze_niche(niche, use_apify)
        
        print(f"  Score: {result['score']}/{result['max_score']} — {result['grade']}")
        print(f"  Autocomplete suggestions: {result['autocomplete_count']}")
        for s in result.get("autocomplete_suggestions", [])[:5]:
            print(f"    • {s}")
        
        if "serp" in result and not result["serp"].get("error"):
            s = result["serp"]
            print(f"  PAA questions: {s.get('paa_count', 0)}")
            print(f"  Related searches: {s.get('related_count', 0)}")
            print(f"  Has ads: {s.get('has_ads', False)}")
        
        time.sleep(0.5)  # Rate limit for free API
    
    print(f"\n{'='*60}")
    print("Done.")

if __name__ == "__main__":
    main()
