# Bitcoin Geopolitics Analysis

Comprehensive open-source intelligence analysis of global Bitcoin hashrate distribution, nation-state holdings (disclosed and estimated), and paper Bitcoin circulation.

## Quick Start

```bash
# Install dependencies
pip install matplotlib numpy

# Generate all visualizations
python visualizations/generate_visualizations.py       # Core analysis (color)
python visualizations/generate_visualizations_bw.py    # Core analysis (B&W)
python visualizations/generate_geopolitical_charts.py  # Geopolitical events (both)
```

## Project Structure

```
real-bitcoin/
├── data/
│   ├── hashrate_distribution.json    # Mining pools & country hashrate data
│   ├── government_holdings.json      # Disclosed + estimated secret holdings
│   ├── paper_bitcoin.json            # ETFs, exchanges, wrapped BTC analysis
│   ├── geopolitical_events.json      # Hashrate response to world events
│   ├── hashrate_by_country.csv       # Country hashrate (CSV format)
│   ├── government_holdings.csv       # Government holdings (CSV format)
│   └── paper_bitcoin_summary.csv     # Paper BTC summary (CSV format)
├── visualizations/
│   ├── generate_visualizations.py    # Core analysis charts (color)
│   ├── generate_visualizations_bw.py # Core analysis charts (B&W)
│   ├── generate_geopolitical_charts.py # Geopolitical event charts
│   ├── *.png                         # Color outputs
│   └── bw/*.png                      # Black & white outputs
└── report/
    └── BITCOIN_GEOPOLITICS_REPORT.md # Full analysis report
```

## Runtime Instructions

### Prerequisites

- Python 3.8+
- matplotlib
- numpy

### Generating Visualizations

```bash
# Color versions (dark theme)
cd /path/to/real-bitcoin
python visualizations/generate_visualizations.py

# Black & white versions (Montserrat font, print-ready)
python visualizations/generate_visualizations_bw.py
```

Outputs are saved to `visualizations/` and `visualizations/bw/`.

### Reading the Data

```python
import json

# Load hashrate data
with open('data/hashrate_distribution.json') as f:
    hashrate = json.load(f)

# Access mining pool share
print(hashrate['mining_pools']['Foundry_USA']['market_share_percent'])  # 33.5

# Access country estimates
print(hashrate['country_distribution']['estimated_actual']['China']['share_percent_mid'])  # 21.0
```

---

## For Autonomous Agents (Ralph/Swarm)

This section provides guidance for Claude instances running autonomously to extend this research.

### Current State of Research

| Area | Completeness | Confidence | Priority for Extension |
|------|--------------|------------|------------------------|
| Mining pool market share | 90% | High | Low |
| Country hashrate (disclosed) | 85% | Medium | Medium |
| Country hashrate (VPN-adjusted) | 60% | Low-Medium | **High** |
| Government holdings (disclosed) | 95% | High | Low |
| Government holdings (secret) | 40% | Low | **High** |
| ETF holdings | 95% | High | Low |
| Exchange reserves | 70% | Medium | **High** |
| Paper Bitcoin multiplier | 50% | Low-Medium | **High** |

### Research Extension Roadmap

#### Priority 1: Improve Confidence Levels

1. **Verify on-chain data**
   - Fetch actual wallet addresses for disclosed government holdings
   - Cross-reference ETF custody addresses with on-chain balances
   - Track Kraken/Binance Proof of Reserve wallet addresses

2. **Update with real-time data**
   - Query CoinGlass API for current ETF holdings
   - Scrape hashrate data from Hashrate Index
   - Check Cambridge CBECI for updated country distribution

3. **Triangulate secret holding estimates**
   - Search for new evidence of state mining operations
   - Track sanctions-related wallet clusters
   - Analyze mining pool payout patterns

#### Priority 2: New Research Dimensions

1. **Historical analysis**
   - Chart hashrate migration over time (2017-2026)
   - Track government accumulation curves
   - Correlate with regulatory events

2. **Whale wallet analysis**
   - Identify large unknown wallets
   - Cluster analysis for potential state actors
   - Track dormant wallet reactivation

3. **Mining economics**
   - Calculate break-even prices by country
   - Map stranded energy to mining potential
   - Model future hashrate distribution

4. **Systemic risk modeling**
   - Simulate bank run scenarios
   - Model contagion from exchange failures
   - Stress test custody concentration

#### Priority 3: Data Pipeline Automation

1. **Build scrapers for**
   - SEC ETF filings (daily holdings)
   - Exchange Proof of Reserve pages
   - Mining pool statistics
   - Blockchain explorer APIs

2. **Create update scripts**
   - `scripts/update_hashrate.py`
   - `scripts/update_etf_holdings.py`
   - `scripts/update_exchange_reserves.py`
   - `scripts/verify_government_wallets.py`

3. **Automate report generation**
   - Daily data refresh
   - Weekly report regeneration
   - Confidence interval updates

### How to Extend (for Claude agents)

When continuing this research:

```markdown
1. READ the existing data files first to understand current state
2. SEARCH the web for updated/new information
3. VERIFY claims with multiple sources
4. UPDATE JSON files with new data + confidence levels
5. REGENERATE visualizations
6. UPDATE the report with new findings
7. COMMIT with clear description of what changed
```

### Key Sources to Query

| Source | URL | Data Type |
|--------|-----|-----------|
| Cambridge CBECI | ccaf.io/cbnsi/cbeci | Hashrate by country |
| Hashrate Index | hashrateindex.com | Mining pool stats |
| CoinGlass | coinglass.com/bitcoin-etf | ETF holdings |
| BitcoinTreasuries | bitcointreasuries.net | Corporate/govt holdings |
| Arkham Intelligence | arkhamintel.io | Wallet attribution |
| DeFiLlama | defillama.com | Wrapped BTC TVL |
| Glassnode | glassnode.com | On-chain metrics |
| CryptoQuant | cryptoquant.com | Exchange reserves |

### Confidence Level Guidelines

When adding estimates, use this framework:

| Level | Criteria | Example |
|-------|----------|---------|
| **Very High** | On-chain verified, multiple sources | Kraken PoR (114.9%) |
| **High** | Official disclosure, audited | US govt 328K BTC |
| **Medium** | Reputable source, partial verification | China 21% hashrate |
| **Low** | Single source, extrapolation | Russia secret holdings |
| **Speculative** | Inference only, no direct evidence | CIA mining operations |

Always include:
- `_low`, `_mid`, `_high` range estimates
- `confidence` field
- `evidence` array with sources
- `last_updated` timestamp

### Example: Adding New Data

```python
# In government_holdings.json, to add a new country:
"New_Country": {
    "btc_held": 5000,
    "usd_value_millions": 420,
    "source": "seizure",
    "acquisition_details": "Darknet marketplace takedown 2025",
    "status": "held",
    "confidence": "high",
    "evidence": [
        "Court filing XYZ-2025",
        "Blockchain explorer TX abc123"
    ],
    "wallet_addresses": ["bc1q..."],
    "last_updated": "2026-02-15"
}
```

---

## Geopolitical Events Analysis

Analysis of how Bitcoin hashrate responded to 5 major world events:

| Event | Date | Hashrate Drop | Recovery |
|-------|------|---------------|----------|
| **US Airstrikes on Iran** | June 2025 | -27.3% | 5 days |
| **China Mining Ban** | May-Jul 2021 | -53.3% | 180 days |
| **Kazakhstan Protests** | Jan 2022 | -13.7% | 7 days |
| **Russia-Ukraine War** | Feb 2022 | -26.9% | 30 days |
| **Texas Winter Storms** | Jan 2024/2026 | -25% to -40% | 3-4 days |

### Iran Mining Claim Analysis

**Claim:** "Iran was mining Bitcoin and Trump bombed the mining centers"

**Verdict:** PARTIALLY VALIDATED

- ✓ Iran legalized BTC mining in 2019
- ✓ IRGC operated mining facilities
- ✓ Iran had 3-4.5% of global hashrate
- ✓ Hashrate dropped 27% within hours of strikes
- ✗ Mining facilities were not directly targeted (nuclear enrichment sites were)
- ✗ Full 27% drop exceeds Iran's ~3% contribution

See `data/geopolitical_events.json` and `visualizations/iran_mining_analysis.png` for details.

---

## Key Findings Summary

| Metric | Value | Confidence |
|--------|-------|------------|
| China's actual hashrate | 15-25% (vs 0% disclosed) | Medium |
| Total govt BTC (disclosed + secret) | 800K-1.1M (4-5.5% of supply) | Low-Medium |
| Paper Bitcoin multiplier | 1.15x | Medium |
| Estimated phantom BTC | ~700,000 | Low |

See `report/BITCOIN_GEOPOLITICS_REPORT.md` for full analysis.

---

## Contributing

This is an open research project. Extensions welcome in:
- New data sources
- Improved estimation methodologies
- On-chain verification
- Historical analysis
- Visualization improvements

## License

Open source research. Data derived from public sources. Estimates are clearly marked as such.

---

*Last updated: 2026-02-02*
