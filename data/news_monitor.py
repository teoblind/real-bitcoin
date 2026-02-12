#!/usr/bin/env python3
"""
Bitcoin News Monitor - Uses Perplexity API to track events impacting
country-level Bitcoin holdings and hashrate estimates.
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent

# Event categories to monitor
MONITORING_QUERIES = [
    "Bitcoin seizure government {country} last 7 days",
    "Bitcoin mining ban regulation {country} last 7 days",
    "Bitcoin hashrate drop {country} last 7 days",
    "cryptocurrency exchange hack theft last 7 days",
    "government Bitcoin purchase strategic reserve last 7 days",
    "Bitcoin mining facility shutdown {country} last 7 days",
]

# Countries to monitor
COUNTRIES = [
    "United States", "China", "Russia", "Iran", "North Korea",
    "United Kingdom", "Germany", "El Salvador", "Bhutan", "Ukraine",
    "Kazakhstan", "Venezuela", "Saudi Arabia"
]


def query_perplexity(query: str, api_key: str) -> dict:
    """Query Perplexity API for news/information."""
    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {
                "role": "system",
                "content": """You are a Bitcoin news analyst. Extract structured data about events
                that impact country-level Bitcoin holdings or hashrate. Return JSON only.

                For each relevant event found, return:
                {
                    "events": [
                        {
                            "date": "YYYY-MM-DD",
                            "country": "Country name",
                            "event_type": "seizure|sale|purchase|mining_shutdown|hack|regulation",
                            "btc_amount": number or null,
                            "hashrate_impact_percent": number or null,
                            "description": "Brief description",
                            "source": "Source name",
                            "confidence": "high|medium|low"
                        }
                    ]
                }

                If no relevant events found, return: {"events": []}"""
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    return response.json()


def parse_perplexity_response(response: dict) -> list:
    """Parse Perplexity response and extract events."""
    try:
        content = response["choices"][0]["message"]["content"]

        # Try to extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())
        return data.get("events", [])
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


def check_holdings_news(api_key: str, countries: list = None) -> dict:
    """Check for news about Bitcoin holdings changes."""
    if countries is None:
        countries = COUNTRIES

    all_events = []

    # Query for general Bitcoin news
    general_queries = [
        "government Bitcoin seizure confiscation last 7 days 2026",
        "country Bitcoin strategic reserve purchase last 7 days 2026",
        "cryptocurrency exchange hack theft Bitcoin last 7 days 2026",
        "Bitcoin ETF holdings change institutional last 7 days 2026",
    ]

    for query in general_queries:
        try:
            response = query_perplexity(query, api_key)
            events = parse_perplexity_response(response)
            all_events.extend(events)
        except Exception as e:
            print(f"Error querying '{query}': {e}")

    # Query for specific countries with significant mining/holdings
    priority_countries = ["China", "Russia", "Iran", "United States", "North Korea"]
    for country in priority_countries:
        query = f"Bitcoin mining hashrate {country} news changes last 7 days 2026"
        try:
            response = query_perplexity(query, api_key)
            events = parse_perplexity_response(response)
            all_events.extend(events)
        except Exception as e:
            print(f"Error querying country '{country}': {e}")

    # Deduplicate events
    seen = set()
    unique_events = []
    for event in all_events:
        key = (event.get("date"), event.get("country"), event.get("event_type"))
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    return {
        "last_updated": datetime.now().isoformat(),
        "events": unique_events
    }


def check_corporate_holdings(api_key: str) -> dict:
    """Check for corporate Bitcoin treasury updates."""

    query = """Find the latest Bitcoin holdings for major corporate treasuries as of today.
    Include: MicroStrategy (MSTR), Marathon Digital (MARA), Riot Platforms, CleanSpark,
    Tesla, Block (Square), Coinbase corporate holdings, Metaplanet, Semler Scientific.

    Return JSON:
    {
        "corporate_holdings": [
            {
                "company": "Company name",
                "ticker": "TICKER",
                "btc_held": number,
                "last_updated": "YYYY-MM-DD",
                "recent_change_btc": number or null,
                "change_description": "bought/sold X BTC" or null,
                "source": "source name",
                "confidence": "high|medium|low"
            }
        ],
        "total_corporate_btc": number
    }"""

    try:
        response = query_perplexity(query, api_key)
        content = response["choices"][0]["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())
    except Exception as e:
        return {"error": str(e), "corporate_holdings": [], "total_corporate_btc": 0}


def check_etf_holdings(api_key: str) -> dict:
    """Check for Bitcoin ETF holdings updates."""

    query = """Find the latest Bitcoin ETF holdings as of today.
    Include: BlackRock IBIT, Fidelity FBTC, Grayscale GBTC, ARK 21Shares ARKB,
    Bitwise BITB, VanEck HODL, Invesco BTCO, Franklin EZBC.

    Return JSON:
    {
        "etf_holdings": [
            {
                "fund_name": "Fund name",
                "ticker": "TICKER",
                "btc_held": number,
                "aum_usd": number or null,
                "daily_flow_btc": number or null,
                "weekly_flow_btc": number or null,
                "custodian": "Custodian name",
                "confidence": "high|medium|low"
            }
        ],
        "total_etf_btc": number,
        "net_weekly_flow_btc": number
    }"""

    try:
        response = query_perplexity(query, api_key)
        content = response["choices"][0]["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())
    except Exception as e:
        return {"error": str(e), "etf_holdings": [], "total_etf_btc": 0}


def check_exchange_reserves(api_key: str) -> dict:
    """Check for exchange Bitcoin reserve updates."""

    query = """Find the latest Bitcoin exchange reserves/holdings as of today.
    Include: Binance, Coinbase, Kraken, OKX, Bybit, Bitfinex, Crypto.com, KuCoin.
    Note any proof-of-reserve audits or concerns.

    Return JSON:
    {
        "exchange_reserves": [
            {
                "exchange": "Exchange name",
                "btc_reserves": number,
                "last_por_date": "YYYY-MM-DD" or null,
                "por_verified": true/false,
                "reserve_ratio": number or null,
                "recent_outflows_btc": number or null,
                "concerns": "any red flags" or null,
                "confidence": "high|medium|low"
            }
        ],
        "total_exchange_btc": number,
        "exchanges_with_verified_por": number
    }"""

    try:
        response = query_perplexity(query, api_key)
        content = response["choices"][0]["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())
    except Exception as e:
        return {"error": str(e), "exchange_reserves": [], "total_exchange_btc": 0}


def check_wrapped_btc(api_key: str) -> dict:
    """Check for wrapped Bitcoin supply."""

    query = """Find the current supply of wrapped Bitcoin across chains.
    Include: WBTC (Ethereum), cbBTC (Coinbase), tBTC, renBTC, sBTC (Stacks),
    and any other major wrapped BTC tokens.

    Return JSON:
    {
        "wrapped_btc": [
            {
                "token": "Token name",
                "chain": "Blockchain",
                "btc_locked": number,
                "custodian": "Custodian" or "decentralized",
                "audited": true/false,
                "confidence": "high|medium|low"
            }
        ],
        "total_wrapped_btc": number
    }"""

    try:
        response = query_perplexity(query, api_key)
        content = response["choices"][0]["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())
    except Exception as e:
        return {"error": str(e), "wrapped_btc": [], "total_wrapped_btc": 0}


def calculate_paper_bitcoin(api_key: str, government_btc: int = None) -> dict:
    """
    Calculate total paper Bitcoin vs actual circulating supply.

    Paper Bitcoin = All claimed BTC (governments + corporates + ETFs + exchanges + wrapped)
    If total claims > circulating supply, we have fractional reserve (red flag)

    Multiplier = Total Claimed / Circulating Supply
    - 1.0 = perfectly backed
    - >1.0 = more claims than actual BTC exists (fractional reserve)
    - <1.0 = some BTC unaccounted for (lost coins, etc.)
    """

    CIRCULATING_SUPPLY = 19_700_000  # Approximate as of 2026

    print("Fetching corporate holdings...")
    corporate = check_corporate_holdings(api_key)

    print("Fetching ETF holdings...")
    etfs = check_etf_holdings(api_key)

    print("Fetching exchange reserves...")
    exchanges = check_exchange_reserves(api_key)

    print("Fetching wrapped BTC...")
    wrapped = check_wrapped_btc(api_key)

    # Load government holdings from local data if not provided
    if government_btc is None:
        try:
            with open(DATA_DIR / "government_holdings.json") as f:
                gov_data = json.load(f)
                # Sum disclosed + estimated secret (mid)
                government_btc = gov_data.get("aggregate_analysis", {}).get("total_government_btc_mid", 900000)
        except:
            government_btc = 900000  # Fallback estimate

    # Calculate totals
    corporate_total = corporate.get("total_corporate_btc", 0)
    etf_total = etfs.get("total_etf_btc", 0)
    exchange_total = exchanges.get("total_exchange_btc", 0)
    wrapped_total = wrapped.get("total_wrapped_btc", 0)

    total_claimed = government_btc + corporate_total + etf_total + exchange_total + wrapped_total

    # Calculate multiplier
    multiplier = total_claimed / CIRCULATING_SUPPLY if CIRCULATING_SUPPLY > 0 else 0

    # Determine risk level
    if multiplier <= 1.0:
        risk_level = "low"
        risk_description = "Total claims within circulating supply"
    elif multiplier <= 1.15:
        risk_level = "medium"
        risk_description = "Slight overclaiming - possible fractional reserves at some exchanges"
    elif multiplier <= 1.3:
        risk_level = "high"
        risk_description = "Significant overclaiming - likely fractional reserves"
    else:
        risk_level = "critical"
        risk_description = "Major overclaiming - systemic fractional reserve risk"

    # Calculate phantom BTC (claims that can't be backed)
    phantom_btc = max(0, total_claimed - CIRCULATING_SUPPLY)

    result = {
        "timestamp": datetime.now().isoformat(),
        "circulating_supply": CIRCULATING_SUPPLY,

        "holdings_breakdown": {
            "government_btc": government_btc,
            "corporate_btc": corporate_total,
            "etf_btc": etf_total,
            "exchange_btc": exchange_total,
            "wrapped_btc": wrapped_total
        },

        "total_claimed_btc": total_claimed,
        "paper_bitcoin_multiplier": round(multiplier, 3),
        "phantom_btc": phantom_btc,

        "risk_assessment": {
            "level": risk_level,
            "description": risk_description,
            "phantom_btc_percent": round((phantom_btc / CIRCULATING_SUPPLY) * 100, 2) if CIRCULATING_SUPPLY > 0 else 0
        },

        "detailed_data": {
            "corporate": corporate,
            "etfs": etfs,
            "exchanges": exchanges,
            "wrapped": wrapped
        },

        "supply_distribution_percent": {
            "government": round((government_btc / CIRCULATING_SUPPLY) * 100, 2),
            "corporate": round((corporate_total / CIRCULATING_SUPPLY) * 100, 2),
            "etfs": round((etf_total / CIRCULATING_SUPPLY) * 100, 2),
            "exchanges": round((exchange_total / CIRCULATING_SUPPLY) * 100, 2),
            "wrapped": round((wrapped_total / CIRCULATING_SUPPLY) * 100, 2),
            "unaccounted": round(((CIRCULATING_SUPPLY - total_claimed) / CIRCULATING_SUPPLY) * 100, 2)
        }
    }

    return result


def check_hashrate_news(api_key: str) -> dict:
    """Check for news about hashrate changes."""
    all_events = []

    queries = [
        "Bitcoin hashrate drop spike network last 7 days 2026",
        "Bitcoin mining shutdown country last 7 days 2026",
        "Bitcoin mining facility power outage last 7 days 2026",
        "China Bitcoin mining crackdown underground last 7 days 2026",
        "Iran Bitcoin mining IRGC last 7 days 2026",
        "Russia Bitcoin mining regulation last 7 days 2026",
        "Kazakhstan Bitcoin mining internet last 7 days 2026",
        "Texas Bitcoin mining grid curtailment last 7 days 2026",
    ]

    for query in queries:
        try:
            response = query_perplexity(query, api_key)
            events = parse_perplexity_response(response)
            all_events.extend(events)
        except Exception as e:
            print(f"Error querying '{query}': {e}")

    # Deduplicate
    seen = set()
    unique_events = []
    for event in all_events:
        key = (event.get("date"), event.get("country"), event.get("description", "")[:50])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    return {
        "last_updated": datetime.now().isoformat(),
        "events": unique_events
    }


def generate_update_suggestions(events: list) -> list:
    """Generate suggestions for updating JSON data files based on events."""
    suggestions = []

    for event in events:
        if event.get("confidence") != "high":
            continue

        event_type = event.get("event_type")
        country = event.get("country")
        btc_amount = event.get("btc_amount")
        hashrate_impact = event.get("hashrate_impact_percent")

        if event_type == "seizure" and btc_amount:
            suggestions.append({
                "file": "government_holdings.json",
                "action": "increase",
                "country": country,
                "field": "btc_held",
                "amount": btc_amount,
                "reason": event.get("description")
            })

        elif event_type == "sale" and btc_amount:
            suggestions.append({
                "file": "government_holdings.json",
                "action": "decrease",
                "country": country,
                "field": "btc_held",
                "amount": btc_amount,
                "reason": event.get("description")
            })

        elif event_type == "mining_shutdown" and hashrate_impact:
            suggestions.append({
                "file": "hashrate_distribution.json",
                "action": "decrease",
                "country": country,
                "field": "share_percent_mid",
                "amount": hashrate_impact,
                "reason": event.get("description")
            })

        elif event_type == "hack" and btc_amount:
            suggestions.append({
                "file": "paper_bitcoin.json",
                "action": "flag",
                "entity": event.get("description"),
                "amount": btc_amount,
                "reason": "Exchange hack - verify reserves"
            })

    return suggestions


def run_full_check(api_key: str, save_results: bool = True, include_paper_bitcoin: bool = False) -> dict:
    """Run a full news check and return results."""
    print("Checking Bitcoin holdings news...")
    holdings_news = check_holdings_news(api_key)

    print("Checking hashrate news...")
    hashrate_news = check_hashrate_news(api_key)

    # Combine all events
    all_events = holdings_news["events"] + hashrate_news["events"]

    # Generate update suggestions
    suggestions = generate_update_suggestions(all_events)

    results = {
        "last_updated": datetime.now().isoformat(),
        "holdings_events": holdings_news["events"],
        "hashrate_events": hashrate_news["events"],
        "update_suggestions": suggestions,
        "total_events_found": len(all_events),
        "high_confidence_events": len([e for e in all_events if e.get("confidence") == "high"])
    }

    # Optionally include paper Bitcoin analysis
    if include_paper_bitcoin:
        print("\nCalculating paper Bitcoin...")
        paper_bitcoin = calculate_paper_bitcoin(api_key)
        results["paper_bitcoin_analysis"] = paper_bitcoin

    if save_results:
        output_path = DATA_DIR / "news_updates.json"
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_path}")

    return results


def get_live_summary(api_key: str) -> dict:
    """Get a quick summary of current Bitcoin landscape for dashboard."""
    query = """Provide current Bitcoin metrics as of today:
    1. Current global hashrate (EH/s)
    2. Any major hashrate changes in past 24 hours
    3. Any government Bitcoin seizures or sales this week
    4. Any major exchange incidents
    5. Bitcoin price

    Return as JSON:
    {
        "timestamp": "ISO timestamp",
        "global_hashrate_eh": number,
        "hashrate_24h_change_percent": number,
        "btc_price_usd": number,
        "alerts": ["list of significant events"],
        "data_confidence": "high|medium|low"
    }"""

    try:
        response = query_perplexity(query, api_key)
        content = response["choices"][0]["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


# FastAPI endpoint for dashboard integration (optional)
def create_api_app():
    """Create FastAPI app for dashboard integration."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
        return None

    app = FastAPI(title="Bitcoin News Monitor API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/live-summary")
    async def live_summary():
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not set")
        return get_live_summary(api_key)

    @app.get("/api/news-check")
    async def news_check():
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not set")
        return run_full_check(api_key, save_results=False)

    @app.get("/api/paper-bitcoin")
    async def paper_bitcoin():
        """Calculate paper Bitcoin multiplier - total claims vs circulating supply."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not set")
        return calculate_paper_bitcoin(api_key)

    @app.get("/api/corporate-holdings")
    async def corporate_holdings():
        """Get current corporate Bitcoin treasury holdings."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not set")
        return check_corporate_holdings(api_key)

    @app.get("/api/etf-holdings")
    async def etf_holdings():
        """Get current Bitcoin ETF holdings."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not set")
        return check_etf_holdings(api_key)

    @app.get("/api/exchange-reserves")
    async def exchange_reserves():
        """Get exchange Bitcoin reserves and proof-of-reserve status."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not set")
        return check_exchange_reserves(api_key)

    @app.get("/api/latest-updates")
    async def latest_updates():
        updates_path = DATA_DIR / "news_updates.json"
        if updates_path.exists():
            with open(updates_path) as f:
                return json.load(f)
        return {"error": "No updates file found. Run news check first."}

    return app


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bitcoin News Monitor")
    parser.add_argument("--api-key", help="Perplexity API key (or set PERPLEXITY_API_KEY env var)")
    parser.add_argument("--live", action="store_true", help="Get live summary only")
    parser.add_argument("--paper", action="store_true", help="Calculate paper Bitcoin multiplier")
    parser.add_argument("--corporate", action="store_true", help="Get corporate holdings only")
    parser.add_argument("--etfs", action="store_true", help="Get ETF holdings only")
    parser.add_argument("--exchanges", action="store_true", help="Get exchange reserves only")
    parser.add_argument("--full", action="store_true", help="Full check including paper Bitcoin")
    parser.add_argument("--serve", action="store_true", help="Start API server")
    parser.add_argument("--port", type=int, default=8000, help="API server port")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("PERPLEXITY_API_KEY")

    if args.serve:
        app = create_api_app()
        if app:
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=args.port)
    elif not api_key:
        print("Error: API key required. Use --api-key or set PERPLEXITY_API_KEY")
        exit(1)
    elif args.live:
        result = get_live_summary(api_key)
        print(json.dumps(result, indent=2))
    elif args.paper:
        print("Calculating paper Bitcoin multiplier...\n")
        result = calculate_paper_bitcoin(api_key)
        print(json.dumps(result, indent=2))

        # Print summary
        print(f"\n{'='*60}")
        print("PAPER BITCOIN SUMMARY")
        print(f"{'='*60}")
        print(f"Circulating Supply:     {result['circulating_supply']:,} BTC")
        print(f"Total Claimed:          {result['total_claimed_btc']:,} BTC")
        print(f"Paper Bitcoin Multiplier: {result['paper_bitcoin_multiplier']}x")
        print(f"Phantom BTC:            {result['phantom_btc']:,} BTC")
        print(f"Risk Level:             {result['risk_assessment']['level'].upper()}")
        print(f"{'='*60}")
    elif args.corporate:
        result = check_corporate_holdings(api_key)
        print(json.dumps(result, indent=2))
    elif args.etfs:
        result = check_etf_holdings(api_key)
        print(json.dumps(result, indent=2))
    elif args.exchanges:
        result = check_exchange_reserves(api_key)
        print(json.dumps(result, indent=2))
    elif args.full:
        result = run_full_check(api_key, include_paper_bitcoin=True)
        print(f"\nFound {result['total_events_found']} events")
        print(f"High confidence events: {result['high_confidence_events']}")
        if result['update_suggestions']:
            print("\nSuggested updates:")
            for s in result['update_suggestions']:
                print(f"  - {s['file']}: {s['action']} {s.get('field', '')} for {s.get('country', s.get('entity', ''))}")
        if 'paper_bitcoin_analysis' in result:
            pb = result['paper_bitcoin_analysis']
            print(f"\nPaper Bitcoin Multiplier: {pb['paper_bitcoin_multiplier']}x")
            print(f"Risk Level: {pb['risk_assessment']['level'].upper()}")
    else:
        result = run_full_check(api_key)
        print(f"\nFound {result['total_events_found']} events")
        print(f"High confidence events: {result['high_confidence_events']}")
        if result['update_suggestions']:
            print("\nSuggested updates:")
            for s in result['update_suggestions']:
                print(f"  - {s['file']}: {s['action']} {s.get('field', '')} for {s.get('country', s.get('entity', ''))}")
