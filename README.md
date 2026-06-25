# AI Dropshipping – Product Research Tool

Automated product research pipeline for winning dropshipping products. Pulls data from Google Trends, scrapes AliExpress best-sellers, and fetches TikTok trend data — then scores and identifies top product candidates.

## Features

- **Google Trends** — Real-time interest scores for trending product keywords
- **AliExpress Scraper** — Best-effort scraping of trending products by category
- **TikTok Trends** — Hashtag data via RapidAPI (requires API key)
- **Candidate Scoring** — Heuristic analysis to surface winning product opportunities
- **Daily Automation** — GitHub Actions runs the pipeline every day

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/xanderstratton10/AI-dropshipping.git
   cd AI-dropshipping
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Set TikTok API credentials**
   ```bash
   export RAPIDAPI_KEY="your-rapidapi-key"
   export RAPIDAPI_HOST="tiktok-api23.p.rapidapi.com"
   ```
   Get an API key from [RapidAPI – TikTok API](https://rapidapi.com/).

## Usage

**Run a one-off research scan:**
```bash
python scripts/product_research.py
```

**Output:** `research_results.json` in the project root with full data and candidate rankings.

## GitHub Actions (Daily Schedule)

The workflow in `.github/workflows/daily_research.yml` runs daily at 6:00 UTC.

To enable TikTok data in CI, add these repository secrets:
- `RAPIDAPI_KEY` — Your RapidAPI key
- `RAPIDAPI_HOST` — The API host (default: `tiktok-api23.p.rapidapi.com`)

## Output Format

```json
{
  "generated_at": "2026-06-25T06:00:00Z",
  "google_trends": { ... },
  "aliexpress": { ... },
  "tiktok_trends": [ ... ],
  "winning_product_candidates": [
    {
      "product_area": "kitchen gadget",
      "trend_score": 95.0,
      "sources": ["google_trends", "aliexpress"],
      "recommended": true
    }
  ]
}
```

## Extending

Add new trending queries in `scripts/product_research.py` under `TRENDING_QUERIES`. Add more scoring logic in `analyze_candidates()`. Drop in additional data sources (Amazon best-sellers, Etsy trends) by adding new fetcher functions to the pipeline.

## License

Internal use — built for the AI Dropshipping business.