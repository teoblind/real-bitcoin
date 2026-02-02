#!/usr/bin/env python3
"""
Bitcoin Geopolitics Visualization Generator
Generates maps, charts, and diagrams for hashrate, government holdings, and paper Bitcoin analysis
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = '#1a1a2e'
plt.rcParams['axes.facecolor'] = '#16213e'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['axes.edgecolor'] = 'white'
plt.rcParams['font.size'] = 10

OUTPUT_DIR = Path(__file__).parent


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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    fig.suptitle('Global Bitcoin Hashrate Distribution by Country', fontsize=16, fontweight='bold', color='white', y=0.98)

    # Disclosed hashrate
    disclosed = hashrate_data['country_distribution']['disclosed']
    countries_disclosed = []
    values_disclosed = []
    for country, data in disclosed.items():
        if country not in ['description'] and isinstance(data, dict):
            countries_disclosed.append(country)
            values_disclosed.append(data['share_percent'])

    # Sort by value
    sorted_pairs = sorted(zip(values_disclosed, countries_disclosed), reverse=True)[:10]
    values_disclosed, countries_disclosed = zip(*sorted_pairs)

    colors_disclosed = plt.cm.Blues(np.linspace(0.4, 0.9, len(countries_disclosed)))
    bars1 = ax1.barh(countries_disclosed, values_disclosed, color=colors_disclosed)
    ax1.set_xlabel('Hashrate Share (%)', fontsize=12)
    ax1.set_title('Disclosed Hashrate (IP-based)', fontsize=14, color='white')
    ax1.invert_yaxis()
    ax1.set_xlim(0, max(values_disclosed) * 1.25)  # Extend x-axis for labels

    for bar, val in zip(bars1, values_disclosed):
        ax1.text(val + 1.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
                va='center', color='white', fontsize=10, fontweight='bold')

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

    # Sort by mid value
    sorted_data = sorted(zip(values_mid, values_low, values_high, countries_est), reverse=True)[:10]
    values_mid, values_low, values_high, countries_est = zip(*sorted_data)

    y_pos = np.arange(len(countries_est))

    # Plot bars with error ranges
    colors_est = plt.cm.Oranges(np.linspace(0.4, 0.9, len(countries_est)))
    bars2 = ax2.barh(y_pos, values_mid, color=colors_est)

    # Add error bars for range
    errors = [[m - l for m, l in zip(values_mid, values_low)],
              [h - m for m, h in zip(values_mid, values_high)]]
    ax2.errorbar(values_mid, y_pos, xerr=errors, fmt='none', color='white', capsize=4, linewidth=1.5, alpha=0.7)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(countries_est)
    ax2.set_xlabel('Hashrate Share (%)', fontsize=12)
    ax2.set_title('Estimated Actual Hashrate (VPN-adjusted)', fontsize=14, color='white')
    ax2.invert_yaxis()
    ax2.set_xlim(0, max(values_high) + 18)  # Extend x-axis significantly for labels

    # Position labels above error bars (slight offset up)
    for i, (val, val_high) in enumerate(zip(values_mid, values_high)):
        label_x = val_high + 2
        ax2.text(label_x, i - 0.15, f'{val:.1f}%', va='bottom', color='white', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'hashrate_by_country.png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print("Created: hashrate_by_country.png")


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

    # Color by region
    colors = []
    for hq in headquarters:
        if 'United States' in hq:
            colors.append('#4169E1')  # Blue for US
        elif 'China' in hq:
            colors.append('#DC143C')  # Red for China
        else:
            colors.append('#32CD32')  # Green for others

    explode = [0.02] * len(names)
    explode[0] = 0.05  # Explode largest

    wedges, texts, autotexts = ax.pie(shares, labels=names, autopct='%1.1f%%',
                                       colors=colors, explode=explode,
                                       textprops={'color': 'white', 'fontsize': 11})

    # Create legend for regions
    us_patch = mpatches.Patch(color='#4169E1', label='US-based')
    china_patch = mpatches.Patch(color='#DC143C', label='China-based')
    other_patch = mpatches.Patch(color='#32CD32', label='Other')
    ax.legend(handles=[us_patch, china_patch, other_patch], loc='lower right',
              facecolor='#16213e', edgecolor='white', labelcolor='white')

    ax.set_title('Bitcoin Mining Pool Market Share (2025-2026)\nColored by Pool Headquarters',
                 fontsize=14, fontweight='bold', color='white')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'mining_pool_share.png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print("Created: mining_pool_share.png")


def create_government_holdings_chart(government_data):
    """Create stacked bar chart of government holdings: disclosed vs estimated secret"""
    fig, ax = plt.subplots(figsize=(14, 10))

    # Prepare data
    disclosed = government_data['disclosed_holdings']
    secret = government_data['estimated_secret_holdings']

    countries = []
    disclosed_btc = []
    secret_btc_low = []
    secret_btc_mid = []
    secret_btc_high = []

    # Countries with both disclosed and secret estimates
    all_countries = set()
    for country in disclosed:
        if country not in ['total_disclosed'] and isinstance(disclosed[country], dict):
            all_countries.add(country)
    for country in secret:
        if country not in ['methodology', 'total_estimated_secret'] and isinstance(secret[country], dict):
            # Clean up country name
            clean_name = country.replace(' (undisclosed)', '')
            all_countries.add(clean_name)

    for country in sorted(all_countries):
        countries.append(country)

        # Get disclosed amount
        disc = disclosed.get(country, {})
        disclosed_btc.append(disc.get('btc_held', 0) if isinstance(disc, dict) else 0)

        # Get secret estimates
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

    # Sort by total (disclosed + mid estimate)
    total = [d + s for d, s in zip(disclosed_btc, secret_btc_mid)]
    sorted_data = sorted(zip(total, countries, disclosed_btc, secret_btc_low, secret_btc_mid, secret_btc_high), reverse=True)
    sorted_data = sorted_data[:12]  # Top 12

    _, countries, disclosed_btc, secret_btc_low, secret_btc_mid, secret_btc_high = zip(*sorted_data)

    y_pos = np.arange(len(countries))

    # Plot stacked bars
    bars1 = ax.barh(y_pos, disclosed_btc, color='#4169E1', label='Disclosed Holdings')
    bars2 = ax.barh(y_pos, secret_btc_mid, left=disclosed_btc, color='#DC143C', alpha=0.7, label='Estimated Secret (Mid)')

    # Add error bars for secret range
    secret_centers = [d + s for d, s in zip(disclosed_btc, secret_btc_mid)]
    errors = [[m - l for m, l in zip(secret_btc_mid, secret_btc_low)],
              [h - m for m, h in zip(secret_btc_mid, secret_btc_high)]]
    ax.errorbar(secret_centers, y_pos, xerr=errors, fmt='none', color='white', capsize=4, linewidth=1.5, alpha=0.7)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(countries)
    ax.set_xlabel('Bitcoin Holdings (BTC)', fontsize=12)
    ax.set_title('Government Bitcoin Holdings: Disclosed vs Estimated Secret\n(Error bars show estimation range)',
                 fontsize=14, fontweight='bold', color='white')
    ax.invert_yaxis()

    # Calculate max extent for x-axis limit
    max_total = max([d + h for d, h in zip(disclosed_btc, secret_btc_high)])
    ax.set_xlim(0, max_total + 200000)  # Extend x-axis significantly for labels

    # Add value labels - position above error bars (slight offset up)
    for i, (d, s, s_high) in enumerate(zip(disclosed_btc, secret_btc_mid, secret_btc_high)):
        total = d + s
        max_extent = d + s_high + 10000
        if total > 0:
            ax.text(max_extent, i - 0.15, f'{total:,.0f}', va='bottom', color='white', fontsize=10, fontweight='bold')

    # Format x-axis with thousands separator
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Legend below the chart
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2,
              facecolor='#16213e', edgecolor='white', labelcolor='white')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'government_holdings.png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print("Created: government_holdings.png")


def create_paper_bitcoin_chart(paper_data):
    """Create visualization of paper Bitcoin circulation"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))

    # 1. Claimed vs Verified BTC by category
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

    bars1 = ax1.bar(x - width/2, [c/1000 for c in claimed], width, label='Claimed', color='#FF6B6B')
    bars2 = ax1.bar(x + width/2, [v/1000 for v in verified], width, label='Verified On-Chain', color='#4ECDC4')

    ax1.set_ylabel('Bitcoin (thousands)', fontsize=11)
    ax1.set_title('Claimed vs Verified Bitcoin Holdings', fontsize=12, fontweight='bold', color='white')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend(facecolor='#16213e', edgecolor='white', labelcolor='white')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}K',
                ha='center', va='bottom', color='white', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}K',
                ha='center', va='bottom', color='white', fontsize=9)

    # 2. ETF breakdown
    ax2 = axes[0, 1]
    etf_data = paper_data['bitcoin_etfs']['funds']
    etf_names = []
    etf_btc = []
    for name, data in etf_data.items():
        etf_names.append(name.replace('_', '\n'))
        etf_btc.append(data['btc_claimed'])

    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(etf_names)))
    ax2.pie(etf_btc, labels=etf_names, autopct='%1.1f%%', colors=colors,
            textprops={'color': 'white', 'fontsize': 9})
    ax2.set_title('Bitcoin ETF Holdings Breakdown', fontsize=12, fontweight='bold', color='white')

    # 3. Exchange reserve confidence
    ax3 = axes[1, 0]
    exchanges = paper_data['exchange_holdings']['exchanges']
    ex_names = []
    ex_btc = []
    ex_confidence = []

    confidence_colors = {
        'very_high': '#00FF00',
        'high': '#90EE90',
        'medium': '#FFD700',
        'low': '#FF6347'
    }

    for name, data in exchanges.items():
        if name != 'Other_Exchanges':
            ex_names.append(name)
            ex_btc.append(data['customer_btc_claimed'] / 1000)
            ex_confidence.append(confidence_colors.get(data.get('reserve_confidence', 'low'), '#FF6347'))

    bars = ax3.barh(ex_names, ex_btc, color=ex_confidence)
    ax3.set_xlabel('Customer BTC (thousands)', fontsize=11)
    ax3.set_title('Exchange Holdings & Reserve Confidence', fontsize=12, fontweight='bold', color='white')
    ax3.invert_yaxis()

    # Legend for confidence
    for conf, color in confidence_colors.items():
        ax3.plot([], [], 's', color=color, label=conf.replace('_', ' ').title())
    ax3.legend(loc='lower right', facecolor='#16213e', edgecolor='white', labelcolor='white', title='Reserve Confidence')

    # 4. Paper Bitcoin Multiplier gauge
    ax4 = axes[1, 1]
    multipliers = paper_data['paper_bitcoin_analysis']['paper_bitcoin_multiplier']

    scenarios = ['Best Case', 'Most Likely', 'Worst Case']
    values = [multipliers['best_case']['value'],
              multipliers['most_likely']['value'],
              multipliers['worst_case']['value']]
    colors = ['#00FF00', '#FFD700', '#FF6347']

    bars = ax4.bar(scenarios, values, color=colors, edgecolor='white', linewidth=2)
    ax4.axhline(y=1.0, color='white', linestyle='--', alpha=0.5, label='1:1 Backing')
    ax4.set_ylabel('Multiplier', fontsize=11)
    ax4.set_title('Paper Bitcoin Multiplier\n(1.0 = fully backed, >1.0 = more claims than BTC)',
                  fontsize=12, fontweight='bold', color='white')
    ax4.set_ylim(0.9, 1.6)

    for bar, val in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2., val + 0.02, f'{val:.2f}x',
                ha='center', va='bottom', color='white', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'paper_bitcoin_analysis.png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print("Created: paper_bitcoin_analysis.png")


def create_risk_matrix(paper_data, government_data):
    """Create risk matrix for entities"""
    fig, ax = plt.subplots(figsize=(14, 10))

    # Define entities with holdings and risk scores
    entities = [
        # (name, holdings_btc, fractional_reserve_risk, category)
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

    # Calculate composite risk score
    for i, (name, holdings, risk, category) in enumerate(entities):
        # Size normalized (log scale)
        size = np.log10(holdings) * 100

        # Color by category
        colors = {
            'government': '#4169E1',
            'corporate': '#32CD32',
            'etf': '#9370DB',
            'exchange': '#FF6347'
        }

        ax.scatter(risk, holdings/1000, s=size, c=colors[category], alpha=0.7, edgecolors='white', linewidth=1)

        # Label
        offset = (10, 10) if holdings > 100000 else (5, 5)
        ax.annotate(name, (risk, holdings/1000), textcoords="offset points",
                   xytext=offset, fontsize=8, color='white')

    ax.set_xlabel('Fractional Reserve Risk Score (0=Safe, 1=High Risk)', fontsize=12)
    ax.set_ylabel('Bitcoin Holdings (thousands)', fontsize=12)
    ax.set_title('Risk Matrix: Holdings Size vs Fractional Reserve Risk\n(Bubble size = log of holdings)',
                 fontsize=14, fontweight='bold', color='white')
    ax.set_yscale('log')
    ax.set_xlim(-0.05, 1.0)

    # Legend
    for cat, color in {'Government': '#4169E1', 'Corporate': '#32CD32',
                       'ETF': '#9370DB', 'Exchange': '#FF6347'}.items():
        ax.scatter([], [], c=color, s=100, label=cat, alpha=0.7)
    ax.legend(loc='upper right', facecolor='#16213e', edgecolor='white', labelcolor='white')

    # Risk zones
    ax.axvspan(0, 0.2, alpha=0.1, color='green', label='Low Risk')
    ax.axvspan(0.2, 0.5, alpha=0.1, color='yellow')
    ax.axvspan(0.5, 1.0, alpha=0.1, color='red')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'risk_matrix.png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print("Created: risk_matrix.png")


def create_supply_distribution(government_data, paper_data):
    """Create pie chart showing Bitcoin supply distribution"""
    fig, ax = plt.subplots(figsize=(14, 10))

    total_supply = 19700000

    # Categories
    categories = {
        'Governments (Disclosed)': government_data['aggregate_analysis']['total_government_btc_low'] - 150000,  # Just disclosed
        'Governments (Est. Secret)': 255000,  # Mid estimate of secret
        'ETFs': 1100000,
        'Corporate Treasuries': 900000,
        'Exchanges (Customer)': 2500000,
        'Lost/Dormant (~20%)': 3940000,
        'Retail/Other': 0  # Will calculate
    }

    # Calculate remaining
    accounted = sum(categories.values())
    categories['Retail/Other'] = total_supply - accounted

    # Remove negative values
    categories = {k: max(0, v) for k, v in categories.items()}

    colors = ['#4169E1', '#DC143C', '#9370DB', '#32CD32', '#FF6347', '#696969', '#FFD700']
    explode = [0.02, 0.05, 0.02, 0.02, 0.02, 0, 0]

    wedges, texts, autotexts = ax.pie(
        categories.values(),
        labels=categories.keys(),
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total_supply):,} BTC)',
        colors=colors,
        explode=explode,
        textprops={'color': 'white', 'fontsize': 9}
    )

    ax.set_title(f'Estimated Bitcoin Supply Distribution\n(Total: {total_supply:,} BTC)',
                 fontsize=14, fontweight='bold', color='white')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'supply_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print("Created: supply_distribution.png")


def main():
    print("Loading data...")
    hashrate, government, paper = load_data()

    print("\nGenerating visualizations...")
    create_hashrate_bar_chart(hashrate)
    create_mining_pool_chart(hashrate)
    create_government_holdings_chart(government)
    create_paper_bitcoin_chart(paper)
    create_risk_matrix(paper, government)
    create_supply_distribution(government, paper)

    print("\nAll visualizations generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
