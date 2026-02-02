#!/usr/bin/env python3
"""
Bitcoin Geopolitics Visualization Generator - Black & White Version
Clean, professional graphs with Montserrat font, no colors, no grids
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# Find and set Montserrat font
font_paths = fm.findSystemFonts()
montserrat_path = None
for fp in font_paths:
    if 'Montserrat' in fp:
        montserrat_path = fp
        break

if montserrat_path:
    fm.fontManager.addfont(montserrat_path)
    plt.rcParams['font.family'] = 'Montserrat'
else:
    plt.rcParams['font.family'] = 'sans-serif'

# Clear any cached fonts
plt.rcParams['font.sans-serif'] = ['Montserrat', 'DejaVu Sans', 'Arial']

# Set clean black & white style - NO GRID
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['text.color'] = 'black'
plt.rcParams['axes.labelcolor'] = 'black'
plt.rcParams['xtick.color'] = 'black'
plt.rcParams['ytick.color'] = 'black'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.grid'] = False
plt.rcParams['grid.alpha'] = 0
plt.rcParams['font.size'] = 11
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

OUTPUT_DIR = Path(__file__).parent / 'bw'
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    """Load all JSON data files"""
    data_dir = Path(__file__).parent.parent / 'data'

    with open(data_dir / 'hashrate_distribution.json') as f:
        hashrate = json.load(f)
    with open(data_dir / 'government_holdings.json') as f:
        government = json.load(f)
    with open(data_dir / 'paper_bitcoin.json') as f:
        paper = json.load(f)

    return hashrate, government, paper


def create_hashrate_bar_chart(hashrate_data):
    """Create bar chart of hashrate by country (disclosed vs estimated)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Global Bitcoin Hashrate Distribution by Country', fontsize=16, fontweight='bold')

    # Disclosed hashrate
    disclosed = hashrate_data['country_distribution']['disclosed']
    countries_disclosed = []
    values_disclosed = []
    for country, data in disclosed.items():
        if country not in ['description'] and isinstance(data, dict):
            countries_disclosed.append(country)
            values_disclosed.append(data['share_percent'])

    sorted_pairs = sorted(zip(values_disclosed, countries_disclosed), reverse=True)[:10]
    values_disclosed, countries_disclosed = zip(*sorted_pairs)

    # Black bars with white fill and black edge
    bars1 = ax1.barh(countries_disclosed, values_disclosed, color='white', edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Hashrate Share (%)', fontsize=12)
    ax1.set_title('Disclosed Hashrate (IP-based)', fontsize=14)
    ax1.invert_yaxis()

    for bar, val in zip(bars1, values_disclosed):
        ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
                va='center', fontsize=10)

    # Estimated actual hashrate
    estimated = hashrate_data['country_distribution']['estimated_actual']
    countries_est = []
    values_low = []
    values_mid = []
    values_high = []

    for country, data in estimated.items():
        if country not in ['description'] and isinstance(data, dict):
            countries_est.append(country)
            values_low.append(data.get('share_percent_low', 0))
            values_mid.append(data.get('share_percent_mid', 0))
            values_high.append(data.get('share_percent_high', 0))

    sorted_data = sorted(zip(values_mid, values_low, values_high, countries_est), reverse=True)[:10]
    values_mid, values_low, values_high, countries_est = zip(*sorted_data)

    y_pos = np.arange(len(countries_est))

    # Gray filled bars
    bars2 = ax2.barh(y_pos, values_mid, color='#808080', edgecolor='black', linewidth=1.5)

    # Error bars
    errors = [[m - l for m, l in zip(values_mid, values_low)],
              [h - m for m, h in zip(values_mid, values_high)]]
    ax2.errorbar(values_mid, y_pos, xerr=errors, fmt='none', color='black', capsize=4, linewidth=1.5)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(countries_est)
    ax2.set_xlabel('Hashrate Share (%)', fontsize=12)
    ax2.set_title('Estimated Actual Hashrate (VPN-adjusted)', fontsize=14)
    ax2.invert_yaxis()

    # Position labels beyond error bars
    for i, (val, val_high) in enumerate(zip(values_mid, values_high)):
        label_x = val_high + 2  # Position beyond upper error bar
        ax2.text(label_x, i, f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'hashrate_by_country_bw.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: hashrate_by_country_bw.png")


def create_mining_pool_chart(hashrate_data):
    """Create pie chart of mining pool market share"""
    fig, ax = plt.subplots(figsize=(12, 10))

    pools = hashrate_data['mining_pools']
    names = []
    shares = []
    headquarters = []

    for pool, data in pools.items():
        names.append(pool)
        shares.append(data['market_share_percent'])
        headquarters.append(data.get('headquarters', 'Unknown'))

    # Grayscale pattern - alternating fills
    colors = []
    patterns = []
    for i, hq in enumerate(headquarters):
        if 'United States' in hq:
            colors.append('white')
        elif 'China' in hq:
            colors.append('#404040')
        else:
            colors.append('#a0a0a0')

    explode = [0.02] * len(names)
    explode[0] = 0.05

    wedges, texts, autotexts = ax.pie(shares, labels=names, autopct='%1.1f%%',
                                       colors=colors, explode=explode,
                                       textprops={'fontsize': 11},
                                       wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})

    # Make text black
    for text in texts:
        text.set_color('black')
    for autotext in autotexts:
        autotext.set_color('black')

    # Legend
    us_patch = mpatches.Patch(facecolor='white', edgecolor='black', label='US-based')
    china_patch = mpatches.Patch(facecolor='#404040', edgecolor='black', label='China-based')
    other_patch = mpatches.Patch(facecolor='#a0a0a0', edgecolor='black', label='Other')
    ax.legend(handles=[us_patch, china_patch, other_patch], loc='lower right',
              frameon=True, edgecolor='black')

    ax.set_title('Bitcoin Mining Pool Market Share (2025-2026)\nColored by Pool Headquarters',
                 fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'mining_pool_share_bw.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: mining_pool_share_bw.png")


def create_government_holdings_chart(government_data):
    """Create stacked bar chart of government holdings"""
    fig, ax = plt.subplots(figsize=(14, 10))

    disclosed = government_data['disclosed_holdings']
    secret = government_data['estimated_secret_holdings']

    countries = []
    disclosed_btc = []
    secret_btc_low = []
    secret_btc_mid = []
    secret_btc_high = []

    all_countries = set()
    for country in disclosed:
        if country not in ['total_disclosed'] and isinstance(disclosed[country], dict):
            all_countries.add(country)
    for country in secret:
        if country not in ['methodology', 'total_estimated_secret'] and isinstance(secret[country], dict):
            clean_name = country.replace(' (undisclosed)', '')
            all_countries.add(clean_name)

    for country in sorted(all_countries):
        countries.append(country)
        disc = disclosed.get(country, {})
        disclosed_btc.append(disc.get('btc_held', 0) if isinstance(disc, dict) else 0)

        sec_key = country
        if country == 'United States':
            sec_key = 'United States (undisclosed)'
        sec = secret.get(sec_key, secret.get(country, {}))
        if isinstance(sec, dict):
            secret_btc_low.append(sec.get('estimated_secret_btc_low', sec.get('estimated_additional_secret_btc_low', sec.get('estimated_held_btc_low', 0))))
            secret_btc_mid.append(sec.get('estimated_secret_btc_mid', sec.get('estimated_additional_secret_btc_mid', sec.get('estimated_held_btc_mid', 0))))
            secret_btc_high.append(sec.get('estimated_secret_btc_high', sec.get('estimated_additional_secret_btc_high', sec.get('estimated_held_btc_high', 0))))
        else:
            secret_btc_low.append(0)
            secret_btc_mid.append(0)
            secret_btc_high.append(0)

    total = [d + s for d, s in zip(disclosed_btc, secret_btc_mid)]
    sorted_data = sorted(zip(total, countries, disclosed_btc, secret_btc_low, secret_btc_mid, secret_btc_high), reverse=True)
    sorted_data = sorted_data[:12]

    _, countries, disclosed_btc, secret_btc_low, secret_btc_mid, secret_btc_high = zip(*sorted_data)

    y_pos = np.arange(len(countries))

    # White bars for disclosed, gray for secret
    bars1 = ax.barh(y_pos, disclosed_btc, color='white', edgecolor='black', linewidth=1.5, label='Disclosed Holdings')
    bars2 = ax.barh(y_pos, secret_btc_mid, left=disclosed_btc, color='#808080', edgecolor='black', linewidth=1.5, label='Estimated Secret (Mid)')

    # Error bars
    secret_centers = [d + s for d, s in zip(disclosed_btc, secret_btc_mid)]
    errors = [[m - l for m, l in zip(secret_btc_mid, secret_btc_low)],
              [h - m for m, h in zip(secret_btc_mid, secret_btc_high)]]
    ax.errorbar(secret_centers, y_pos, xerr=errors, fmt='none', color='black', capsize=4, linewidth=1.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(countries)
    ax.set_xlabel('Bitcoin Holdings (BTC)', fontsize=12)
    ax.set_title('Government Bitcoin Holdings: Disclosed vs Estimated Secret\n(Error bars show estimation range)',
                 fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.legend(loc='lower right', frameon=True, edgecolor='black')

    # Calculate max extent including error bars for label positioning
    for i, (d, s, s_high) in enumerate(zip(disclosed_btc, secret_btc_mid, secret_btc_high)):
        total = d + s
        max_extent = d + s_high + 15000  # Position label beyond error bar
        if total > 0:
            ax.text(max_extent, i, f'{total:,.0f}', va='center', fontsize=10, fontweight='bold')

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'government_holdings_bw.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: government_holdings_bw.png")


def create_paper_bitcoin_chart(paper_data):
    """Create visualization of paper Bitcoin circulation"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))

    # 1. Claimed vs Verified BTC
    ax1 = axes[0, 0]
    categories = ['ETFs', 'Corporate\nTreasuries', 'Exchanges', 'Wrapped\nBTC']
    claimed = [
        paper_data['paper_bitcoin_analysis']['total_claimed_btc']['etfs'],
        paper_data['paper_bitcoin_analysis']['total_claimed_btc']['corporate_treasuries'],
        paper_data['paper_bitcoin_analysis']['total_claimed_btc']['exchanges'],
        paper_data['paper_bitcoin_analysis']['total_claimed_btc']['wrapped_btc']
    ]
    verified = [
        paper_data['paper_bitcoin_analysis']['verifiable_on_chain_btc']['etfs_verified'],
        paper_data['paper_bitcoin_analysis']['verifiable_on_chain_btc']['corporate_verified'],
        paper_data['paper_bitcoin_analysis']['verifiable_on_chain_btc']['exchanges_verified'],
        paper_data['paper_bitcoin_analysis']['verifiable_on_chain_btc']['wrapped_verified']
    ]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax1.bar(x - width/2, [c/1000 for c in claimed], width, label='Claimed',
                    color='white', edgecolor='black', linewidth=1.5)
    bars2 = ax1.bar(x + width/2, [v/1000 for v in verified], width, label='Verified On-Chain',
                    color='#808080', edgecolor='black', linewidth=1.5)

    ax1.set_ylabel('Bitcoin (thousands)', fontsize=11)
    ax1.set_title('Claimed vs Verified Bitcoin Holdings', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend(frameon=True, edgecolor='black')

    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}K',
                ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}K',
                ha='center', va='bottom', fontsize=9)

    # 2. ETF breakdown
    ax2 = axes[0, 1]
    etf_data = paper_data['bitcoin_etfs']['funds']
    etf_names = []
    etf_btc = []
    for name, data in etf_data.items():
        etf_names.append(name.replace('_', '\n'))
        etf_btc.append(data['btc_claimed'])

    # Grayscale for pie
    grays = ['white', '#d0d0d0', '#a0a0a0', '#707070', '#505050', '#303030']
    wedges, texts, autotexts = ax2.pie(etf_btc, labels=etf_names, autopct='%1.1f%%',
                                        colors=grays[:len(etf_names)],
                                        textprops={'fontsize': 9},
                                        wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})
    for text in texts:
        text.set_color('black')
    for autotext in autotexts:
        autotext.set_color('black')
    ax2.set_title('Bitcoin ETF Holdings Breakdown', fontsize=12, fontweight='bold')

    # 3. Exchange reserve confidence
    ax3 = axes[1, 0]
    exchanges = paper_data['exchange_holdings']['exchanges']
    ex_names = []
    ex_btc = []
    ex_patterns = []

    confidence_fills = {
        'very_high': 'white',
        'high': '#c0c0c0',
        'medium': '#808080',
        'low': '#404040'
    }

    for name, data in exchanges.items():
        if name != 'Other_Exchanges':
            ex_names.append(name)
            ex_btc.append(data['customer_btc_claimed'] / 1000)
            ex_patterns.append(confidence_fills.get(data.get('reserve_confidence', 'low'), '#404040'))

    bars = ax3.barh(ex_names, ex_btc, color=ex_patterns, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Customer BTC (thousands)', fontsize=11)
    ax3.set_title('Exchange Holdings & Reserve Confidence', fontsize=12, fontweight='bold')
    ax3.invert_yaxis()

    # Legend
    for conf, fill in [('Very High', 'white'), ('High', '#c0c0c0'), ('Medium', '#808080'), ('Low', '#404040')]:
        ax3.barh([], [], color=fill, edgecolor='black', label=conf)
    ax3.legend(loc='lower right', frameon=True, edgecolor='black', title='Reserve Confidence')

    # 4. Paper Bitcoin Multiplier
    ax4 = axes[1, 1]
    multipliers = paper_data['paper_bitcoin_analysis']['paper_bitcoin_multiplier']

    scenarios = ['Best Case', 'Most Likely', 'Worst Case']
    values = [multipliers['best_case']['value'],
              multipliers['most_likely']['value'],
              multipliers['worst_case']['value']]
    fills = ['white', '#808080', '#404040']

    bars = ax4.bar(scenarios, values, color=fills, edgecolor='black', linewidth=2)
    ax4.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='1:1 Backing')
    ax4.set_ylabel('Multiplier', fontsize=11)
    ax4.set_title('Paper Bitcoin Multiplier\n(1.0 = fully backed, >1.0 = more claims than BTC)',
                  fontsize=12, fontweight='bold')
    ax4.set_ylim(0.9, 1.6)

    for bar, val in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2., val + 0.02, f'{val:.2f}x',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'paper_bitcoin_analysis_bw.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: paper_bitcoin_analysis_bw.png")


def create_risk_matrix(paper_data, government_data):
    """Create risk matrix for entities"""
    fig, ax = plt.subplots(figsize=(14, 10))

    entities = [
        ('US Government', 328000, 0.1, 'government'),
        ('China (disclosed)', 194000, 0.3, 'government'),
        ('UK Government', 61000, 0.1, 'government'),
        ('Russia (est)', 80000, 0.5, 'government'),
        ('Iran (est)', 60000, 0.6, 'government'),
        ('North Korea', 15000, 0.9, 'government'),
        ('Strategy/MSTR', 687000, 0.15, 'corporate'),
        ('BlackRock IBIT', 570000, 0.05, 'etf'),
        ('Fidelity FBTC', 210000, 0.05, 'etf'),
        ('Binance', 600000, 0.35, 'exchange'),
        ('Coinbase', 450000, 0.1, 'exchange'),
        ('Kraken', 167000, 0.02, 'exchange'),
        ('OKX', 120000, 0.3, 'exchange'),
        ('Bybit', 80000, 0.4, 'exchange'),
        ('Bitfinex', 100000, 0.5, 'exchange'),
        ('Small Exchanges', 500000, 0.7, 'exchange'),
    ]

    # Marker styles for B&W differentiation
    markers = {
        'government': 'o',
        'corporate': 's',
        'etf': '^',
        'exchange': 'D'
    }

    fills = {
        'government': 'white',
        'corporate': '#404040',
        'etf': '#808080',
        'exchange': '#c0c0c0'
    }

    for name, holdings, risk, category in entities:
        size = np.log10(holdings) * 80
        ax.scatter(risk, holdings/1000, s=size, c=fills[category],
                  marker=markers[category], edgecolors='black', linewidth=1.5)

        offset = (10, 10) if holdings > 100000 else (5, 5)
        ax.annotate(name, (risk, holdings/1000), textcoords="offset points",
                   xytext=offset, fontsize=8)

    ax.set_xlabel('Fractional Reserve Risk Score (0=Safe, 1=High Risk)', fontsize=12)
    ax.set_ylabel('Bitcoin Holdings (thousands)', fontsize=12)
    ax.set_title('Risk Matrix: Holdings Size vs Fractional Reserve Risk\n(Marker size = log of holdings)',
                 fontsize=14, fontweight='bold')
    ax.set_yscale('log')
    ax.set_xlim(-0.05, 1.0)

    # Legend with markers
    for cat, marker in [('Government', 'o'), ('Corporate', 's'), ('ETF', '^'), ('Exchange', 'D')]:
        ax.scatter([], [], c=fills[cat.lower()], s=100, marker=marker,
                  edgecolors='black', linewidth=1.5, label=cat)
    ax.legend(loc='upper right', frameon=True, edgecolor='black')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'risk_matrix_bw.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: risk_matrix_bw.png")


def create_supply_distribution(government_data, paper_data):
    """Create pie chart showing Bitcoin supply distribution"""
    fig, ax = plt.subplots(figsize=(14, 10))

    total_supply = 19700000

    categories = {
        'Governments (Disclosed)': government_data['aggregate_analysis']['total_government_btc_low'] - 150000,
        'Governments (Est. Secret)': 255000,
        'ETFs': 1100000,
        'Corporate Treasuries': 900000,
        'Exchanges (Customer)': 2500000,
        'Lost/Dormant (~20%)': 3940000,
        'Retail/Other': 0
    }

    accounted = sum(categories.values())
    categories['Retail/Other'] = total_supply - accounted
    categories = {k: max(0, v) for k, v in categories.items()}

    # Grayscale colors
    grays = ['white', '#e0e0e0', '#c0c0c0', '#a0a0a0', '#808080', '#606060', '#404040']
    explode = [0.02, 0.05, 0.02, 0.02, 0.02, 0, 0]

    wedges, texts, autotexts = ax.pie(
        categories.values(),
        labels=categories.keys(),
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total_supply):,} BTC)',
        colors=grays,
        explode=explode,
        textprops={'fontsize': 9},
        wedgeprops={'edgecolor': 'black', 'linewidth': 1.5}
    )

    for text in texts:
        text.set_color('black')
    for autotext in autotexts:
        autotext.set_color('black')

    ax.set_title(f'Estimated Bitcoin Supply Distribution\n(Total: {total_supply:,} BTC)',
                 fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'supply_distribution_bw.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("Created: supply_distribution_bw.png")


def main():
    print("Loading data...")
    hashrate, government, paper = load_data()

    print(f"\nGenerating B&W visualizations to {OUTPUT_DIR}...")
    create_hashrate_bar_chart(hashrate)
    create_mining_pool_chart(hashrate)
    create_government_holdings_chart(government)
    create_paper_bitcoin_chart(paper)
    create_risk_matrix(paper, government)
    create_supply_distribution(government, paper)

    print("\nAll B&W visualizations generated successfully!")


if __name__ == "__main__":
    main()
