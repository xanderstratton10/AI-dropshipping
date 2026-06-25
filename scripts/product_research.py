#!/usr/bin/env python3
"""
Product Research Tool for AI Dropshipping
Pulls trending data from Google Trends, scrapes AliExpress best-sellers,
and fetches TikTok hashtag trend data.
Outputs results to research_results.json
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any

import requests
from bs4 import BeautifulSoup

# ─── Configuration ───────────────────────────────────────────────────────────

RESULTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "research_results.json",
)

# TikTok RapidAPI config – set these as repo secrets / env vars
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.environ.get("RAPIDAPI_HOST", "tiktok-api23.p.rapidapi.com")

# AliExpress search config
ALIEXPRESS_SEARCH_URL = (
    "https://www.aliexpress.com/wholesale?SearchText={query}&sort=latestbest"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


# ─── Google Trends ───────────────────────────────────────────────────────────

def fetch_google_trends(keywords: list[str], timeframe: str = "now 7-d") -> dict:
    """Fetch Google Trends interest scores for a list of keywords.
    Falls back gracefully if pytrends is not installed.
    """
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=360, timeout=10)
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo="US", gprop="")
        data = pytrends.interest_over_time()
        if data.empty:
            return {"status": "empty", "keywords": keywords}
        # Return the latest row as a snapshot
        latest = data.iloc[-1].to_dict()
        latest.pop("isPartial", None)
        return {"status": "ok", "keywords": keywords, "latest_scores": latest}
    except ImportError:
        return {"status": "pytrends_not_installed", "keywords": keywords}
    except Exception as e:
        return {"status": "error", "keywords": keywords, "error": str(e)}


# ─── AliExpress Scraper ──────────────────────────────────────────────────────

def scrape_aliexpress_bestsellers(query: str, max_items: int = 20) -> list[dict]:
    """Scrape AliExpress search results for trending/best-selling products."""
    url = ALIEXPRESS_SEARCH_URL.format(query=query)
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # AliExpress listings are typically in <a> tags with product data
        # This is a best-effort scraper – AliExpress structure changes often
        for item in soup.select("a[class*='product']")[:max_items]:
            title_el = item.select_one("img[alt]")
            price_el = item.select_one("span[class*='price']")
            title = title_el.get("alt", "") if title_el else ""
            price = price_el.get_text(strip=True) if price_el else ""
            link = item.get("href", "")

            if title and not any(
                kw in title.lower()
                for kw in ["ad", "sponsored", "promoted"]
            ):
                results.append({
                    "title": title,
                    "price": price,
                    "url": f"https:{link}" if link.startswith("//") else link,
                    "source": "aliexpress",
                    "query": query,
                })

        return results if results else _aliexpress_fallback(query, max_items)

    except Exception as e:
        print(f"  [AliExpress] Error for '{query}': {e}", file=sys.stderr)
        return _aliexpress_fallback(query, max_items)


def _aliexpress_fallback(query: str, max_items: int) -> list[dict]:
    """Return a structured fallback when scraping fails."""
    return [
        {
            "title": f"Trending product in '{query}'",
            "price": "Check AliExpress directly",
            "url": ALIEXPRESS_SEARCH_URL.format(query=query),
            "source": "aliexpress_fallback",
            "query": query,
            "note": "Scrape blocked – visit URL manually",
        }
    ]


# ─── TikTok Trends (RapidAPI) ────────────────────────────────────────────────

def fetch_tiktok_hashtag_trends(hashtags: list[str]) -> list[dict]:
    """Fetch TikTok hashtag data via RapidAPI."""
    if not RAPIDAPI_KEY:
        return _tiktok_fallback(hashtags, "RAPIDAPI_KEY not set")

    results = []
    for tag in hashtags:
        try:
            url = f"https://{RAPIDAPI_HOST}/api/hashtag/{tag}/videos"
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": RAPIDAPI_HOST,
            }
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()

            results.append({
                "hashtag": tag,
                "status": "ok" if resp.ok else "error",
                "data": data,
            })
        except Exception as e:
            results.append({"hashtag": tag, "status": "error", "error": str(e)})

    return results if results else _tiktok_fallback(hashtags, "API call failed")


def _tiktok_fallback(hashtags: list[str], reason: str) -> list[dict]:
    """Return structured fallback when TikTok API is unavailable."""
    return [
        {
            "hashtag": tag,
            "status": "unavailable",
            "reason": reason,
            "note": "Set RAPIDAPI_KEY and RAPIDAPI_HOST in GitHub Secrets to enable live data",
        }
        for tag in hashtags
    ]


# ─── Trending Search Queries (for product discovery) ─────────────────────────

TRENDING_QUERIES = [
    "gadget under 20",
    "as seen on tiktok",
    "life hack product",
    "home organizer",
    "kitchen gadget",
    "travel accessory",
    "phone accessory",
    "fitness gear",
    "pet product",
    "beauty tool",
    "car accessory",
    "office desk organizer",
    "led light",
]


# ─── Main Pipeline ───────────────────────────────────────────────────────────

def run_research() -> dict[str, Any]:
    """Run the full research pipeline and return structured results."""
    print("=" * 60)
    print("AI Dropshipping – Product Research Pipeline")
    print(f"Run at: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    report: dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "google_trends": {},
        "aliexpress": {},
        "tiktok_trends": [],
        "winning_product_candidates": [],
    }

    # ── 1. Google Trends ──
    print("\n[1/3] Fetching Google Trends...")
    for q in TRENDING_QUERIES[:6]:  # Rate-limit to 6 queries
        trend_data = fetch_google_trends([q])
        report["google_trends"][q] = trend_data
        status = trend_data.get("status", "unknown")
        print(f"  {q}: {status}")

    # ── 2. AliExpress ──
    print("\n[2/3] Scraping AliExpress best-sellers...")
    for q in TRENDING_QUERIES[:6]:
        products = scrape_aliexpress_bestsellers(q, max_items=5)
        report["aliexpress"][q] = products
        print(f"  {q}: {len(products)} products found")

    # ── 3. TikTok ──
    tiktok_tags = [
        "TikTokMadeMeBuyIt",
        "dropshipping",
        "AmazonFinds",
        "productfinds",
        "gadget",
        "lifehack",
        "musthave",
    ]
    print("\n[3/3] Fetching TikTok trends...")
    tiktok_data = fetch_tiktok_hashtag_trends(tiktok_tags)
    report["tiktok_trends"] = tiktok_data
    for td in tiktok_data:
        print(f"  #{td['hashtag']}: {td['status']}")

    # ── Save ──
    with open(RESULTS_FILE, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✓ Results saved to {RESULTS_FILE}")
    return report


# ─── Analysis Helper: Identify Winning Product Candidates ────────────────────

def analyze_candidates(report: dict[str, Any]) -> list[dict]:
    """Analyze the research data to identify winning product candidates.
    This is a heuristic scorer – extend with ML as data grows.
    """
    candidates = []

    # Count trends mentions across sources
    trend_scores: dict[str, float] = {}

    # From Google Trends, look for keywords with scores > 50
    for keyword, data in report.get("google_trends", {}).items():
        if data.get("status") == "ok":
            scores = data.get("latest_scores", {})
            for kw, score in scores.items():
                if isinstance(score, (int, float)) and score > 50:
                    trend_scores[kw] = trend_scores.get(kw, 0) + score

    # From AliExpress, count unique product titles per query
    for query, products in report.get("aliexpress", {}).items():
        if len(products) >= 3:
            trend_scores[query] = trend_scores.get(query, 0) + len(products) * 10

    # Build candidate list sorted by score
    for name, score in sorted(trend_scores.items(), key=lambda x: -x[1])[:5]:
        candidates.append({
            "product_area": name,
            "trend_score": round(score, 1),
            "sources": ["google_trends", "aliexpress"],
            "recommended": score > 80,
        })

    return candidates


if __name__ == "__main__":
    report = run_research()
    candidates = analyze_candidates(report)

    report["winning_product_candidates"] = candidates

    # Re-save with candidates
    with open(RESULTS_FILE, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("\n" + "=" * 60)
    print("TOP PRODUCT CANDIDATES")
    print("=" * 60)
    for c in candidates:
        flag = "★ RECOMMENDED" if c.get("recommended") else ""
        print(f"  {c['product_area']:30s} | Score: {c['trend_score']:<8.1f} {flag}")
    print(f"\nFull report: {RESULTS_FILE}")