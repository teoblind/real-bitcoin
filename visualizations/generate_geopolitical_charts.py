#!/usr/bin/env python3
"""
Bitcoin Hashrate Response to Geopolitical Events
Generates visualizations showing how hashrate responded to major world events
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
BW_DIR = OUTPUT_DIR / 'bw'
BW_DIR.mkdir(exist_ok=True)


def load_data():
    data_dir = Path(__file__).parent.parent / 'data'
    with open(data_dir / 'geopolitical_events.json') as f:
        return json.load(f)


def setup_color_style():
    """Setup dark theme with colors"""
    plt.rcParams['figure.facecolor'] = '#1a1a2e'
    plt.rcParams['axes.facecolor'] = '#16213e'
    plt.rcParams['text.color'] = 'white'
    plt.rcParams['axes.labelcolor'] = 'white'
    plt.rcParams['xtick.color'] = 'white'
    plt.rcParams['ytick.color'] = 'white'
    plt.rcParams['axes.edgecolor'] = 'white'
    plt.rcParams['axes.grid'] = False
    plt.rcParams['font.size'] = 11


def setup_bw_style():
    """Setup clean B&W style with Montserrat"""
    font_paths = fm.findSystemFonts()
    for fp in font_paths:
        if 'Montserrat' in fp:
            fm.fontManager.addfont(fp)
            plt.rcParams['font.family'] = 'Montserrat'
            break

    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['text.color'] = 'black'
    plt.rcParams['axes.labelcolor'] = 'black'
    plt.rcParams['xtick.color'] = 'black'
    plt.rcParams['ytick.color'] = 'black'
    plt.rcParams['axes.edgecolor'] = 'black'
    plt.rcParams['axes.grid'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['font.size'] = 11


def create_event_comparison_chart(data, bw=False):
    """Bar chart comparing hashrate drops across all events"""
    if bw:
        setup_bw_style()
        suffix = '_bw'
        colors = ['white', '#c0c0c0', '#808080', '#606060', '#404040']
        edge_color = 'black'
        text_color = 'black'
        bg_color = 'white'
    else:
        setup_color_style()
        suffix = ''
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        edge_color = 'white'
        text_color = 'white'
        bg_color = '#1a1a2e'

    fig, ax = plt.subplots(figsize=(14, 8))

    events = data['events']
    names = []
    drops = []
    recoveries = []

    for e in events:
        name = e['name'].replace(' & ', '\n& ').replace('Curtailment', '\nCurtailment')
        if len(name) > 30:
            words = name.split()
            mid = len(words) // 2
            name = ' '.join(words[:mid]) + '\n' + ' '.join(words[mid:])
        names.append(name)
        drops.append(e['hashrate_drop_percent'])
        recoveries.append(e['recovery_time_days'])

    x = np.arange(len(names))
    width = 0.6

    bars = ax.bar(x, drops, width, color=colors, edgecolor=edge_color, linewidth=2)

    ax.set_ylabel('Hashrate Drop (%)', fontsize=12)
    ax.set_title('Bitcoin Hashrate Response to Geopolitical Events\nPercentage Drop from Pre-Event Levels',
                 fontsize=14, fontweight='bold', color=text_color)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylim(0, 60)

    # Add value labels and recovery time
    for bar, drop, recovery in zip(bars, drops, recoveries):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{drop:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold', color=text_color)
        ax.text(bar.get_x() + bar.get_width()/2., height/2,
                f'{recovery}d recovery',
                ha='center', va='center', fontsize=9, color='black' if not bw else 'white')

    plt.tight_layout()

    out_dir = BW_DIR if bw else OUTPUT_DIR
    plt.savefig(out_dir / f'geopolitical_hashrate_drops{suffix}.png', dpi=150,
                bbox_inches='tight', facecolor=bg_color, edgecolor='none')
    plt.close()
    print(f"Created: geopolitical_hashrate_drops{suffix}.png")


def create_timeline_chart(data, bw=False):
    """Timeline showing hashrate changes during each event"""
    if bw:
        setup_bw_style()
        suffix = '_bw'
        line_colors = ['black', '#606060', '#909090', '#b0b0b0', '#404040']
        bg_color = 'white'
        text_color = 'black'
    else:
        setup_color_style()
        suffix = ''
        line_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        bg_color = '#1a1a2e'
        text_color = 'white'

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    events = data['events']

    for idx, event in enumerate(events):
        ax = axes[idx]

        timeline = event['timeline']
        times = list(range(len(timeline)))
        hashrates = [t['hashrate_eh'] for t in timeline]
        labels = [t['event'][:20] + '...' if len(t['event']) > 20 else t['event'] for t in timeline]

        # Normalize to percentage of initial
        initial = hashrates[0]
        pct_hashrates = [(h / initial) * 100 for h in hashrates]

        line_style = '-' if not bw else '-'
        marker = 'o' if not bw else 's'

        ax.plot(times, pct_hashrates, line_style, color=line_colors[idx % len(line_colors)],
                linewidth=2.5, marker=marker, markersize=8,
                markerfacecolor='white' if bw else line_colors[idx % len(line_colors)],
                markeredgecolor='black' if bw else 'white', markeredgewidth=1.5)

        # Add horizontal line at 100%
        ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)

        # Mark the bottom
        min_idx = pct_hashrates.index(min(pct_hashrates))
        ax.annotate(f'{min(pct_hashrates):.1f}%',
                   xy=(min_idx, min(pct_hashrates)),
                   xytext=(min_idx, min(pct_hashrates) - 8),
                   ha='center', fontsize=10, fontweight='bold', color=text_color)

        ax.set_xticks(times)
        ax.set_xticklabels([str(i) for i in times], fontsize=8)
        ax.set_xlabel('Event Timeline Stage', fontsize=10)
        ax.set_ylabel('Hashrate (% of initial)', fontsize=10)

        title = event['name']
        if len(title) > 35:
            title = title[:32] + '...'
        ax.set_title(f"{title}\n{event['date']}", fontsize=11, fontweight='bold', color=text_color)

        ax.set_ylim(min(pct_hashrates) - 15, 105)

    # Remove empty subplot
    axes[5].axis('off')

    # Add summary text in empty space
    summary_text = """KEY FINDINGS:

• China Ban (2021): Largest drop at 53%
  - Caused permanent geographic shift

• Iran Strikes (2025): 27% drop in hours
  - Validates state mining claims

• Kazakhstan (2022): 14% from internet kill
  - Shows vulnerability to centralized control

• Texas Storms: 25-40% drops
  - Voluntary curtailment model works

• Russia-Ukraine: Limited direct impact
  - Mining resilient to sanctions"""

    axes[5].text(0.1, 0.9, summary_text, transform=axes[5].transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                color=text_color)

    plt.suptitle('Hashrate Timeline During Geopolitical Events',
                 fontsize=16, fontweight='bold', color=text_color, y=1.02)
    plt.tight_layout()

    out_dir = BW_DIR if bw else OUTPUT_DIR
    plt.savefig(out_dir / f'geopolitical_timelines{suffix}.png', dpi=150,
                bbox_inches='tight', facecolor=bg_color, edgecolor='none')
    plt.close()
    print(f"Created: geopolitical_timelines{suffix}.png")


def create_iran_analysis_chart(data, bw=False):
    """Detailed analysis of Iran bombing claim"""
    if bw:
        setup_bw_style()
        suffix = '_bw'
        colors = {'drop': '#808080', 'iran': 'white', 'other': '#c0c0c0'}
        bg_color = 'white'
        text_color = 'black'
        edge = 'black'
    else:
        setup_color_style()
        suffix = ''
        colors = {'drop': '#FF6B6B', 'iran': '#4ECDC4', 'other': '#45B7D1'}
        bg_color = '#1a1a2e'
        text_color = 'white'
        edge = 'white'

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))

    iran_event = data['events'][0]  # Iran is first event

    # Chart 1: Hashrate drop breakdown
    ax1 = axes[0]
    total_drop = iran_event['hashrate_before_eh'] - iran_event['hashrate_low_eh']
    iran_contribution = iran_event['analysis']['direct_iran_contribution_eh']
    other_factors = total_drop - iran_contribution

    categories = ['Total Drop', 'Iran Direct', 'Other Factors']
    values = [total_drop, iran_contribution, other_factors]

    bars = ax1.bar(categories, values, color=[colors['drop'], colors['iran'], colors['other']],
                   edgecolor=edge, linewidth=2)
    ax1.set_ylabel('Hashrate (EH/s)', fontsize=12)
    ax1.set_title('Hashrate Drop Breakdown\nJune 21-22, 2025', fontsize=12, fontweight='bold', color=text_color)

    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2., val + 5,
                f'{val:.0f} EH/s', ha='center', fontsize=11, fontweight='bold', color=text_color)

    # Chart 2: Iran's historical hashrate share
    ax2 = axes[1]
    years = ['2019', '2020', '2021', '2022', '2023', '2024', '2025\n(pre)', '2025\n(post)']
    iran_share = [2.0, 3.5, 4.5, 4.0, 3.5, 3.1, 3.1, 0.5]

    bar_colors = [colors['iran']] * 6 + [colors['iran'], colors['drop']]
    bars = ax2.bar(years, iran_share, color=bar_colors, edgecolor=edge, linewidth=1.5)
    ax2.set_ylabel('Share of Global Hashrate (%)', fontsize=12)
    ax2.set_title("Iran's Bitcoin Mining Share Over Time", fontsize=12, fontweight='bold', color=text_color)
    ax2.set_ylim(0, 6)

    # Add annotation for ban legalization
    ax2.annotate('Mining\nlegalized', xy=(0, 2.0), xytext=(0.5, 4.5),
                arrowprops=dict(arrowstyle='->', color=text_color), fontsize=9, color=text_color)
    ax2.annotate('US\nstrikes', xy=(7, 0.5), xytext=(6.5, 2.5),
                arrowprops=dict(arrowstyle='->', color=text_color), fontsize=9, color=text_color)

    # Chart 3: Verdict visualization
    ax3 = axes[2]
    ax3.axis('off')

    verdict_text = """
    CLAIM ANALYSIS
    ══════════════════════════════════════

    Claim: "Iran was mining Bitcoin and
           Trump bombed the mining centers"

    ══════════════════════════════════════

    VERDICT: PARTIALLY VALIDATED ⚠️

    ══════════════════════════════════════

    ✓ CONFIRMED:
    • Iran legalized BTC mining (2019)
    • IRGC operated mining facilities
    • Iran had 3-4.5% of global hashrate
    • Hashrate dropped 27% post-strikes
    • 60,000-200,000 BTC mined total

    ✗ NOT CONFIRMED:
    • Mining facilities directly targeted
    • Full 27% drop attributable to Iran
    • Nuclear sites used for mining power

    ══════════════════════════════════════

    Iran contributed ~28.5 EH/s (3.1%)
    Total drop was ~257 EH/s (27%)
    Gap likely: collateral disruption,
    regional internet, market factors
    """

    ax3.text(0.05, 0.95, verdict_text, transform=ax3.transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            color=text_color,
            bbox=dict(boxstyle='round', facecolor=colors['other'] if not bw else '#f0f0f0',
                     edgecolor=edge, alpha=0.8))

    plt.suptitle('Iran Bitcoin Mining & US Airstrikes Analysis',
                 fontsize=16, fontweight='bold', color=text_color, y=1.02)
    plt.tight_layout()

    out_dir = BW_DIR if bw else OUTPUT_DIR
    plt.savefig(out_dir / f'iran_mining_analysis{suffix}.png', dpi=150,
                bbox_inches='tight', facecolor=bg_color, edgecolor='none')
    plt.close()
    print(f"Created: iran_mining_analysis{suffix}.png")


def create_geographic_shift_chart(data, bw=False):
    """Show how hashrate geography shifted after events"""
    if bw:
        setup_bw_style()
        suffix = '_bw'
        colors_before = ['white', '#e0e0e0', '#c0c0c0', '#a0a0a0', '#808080']
        colors_after = ['#404040', '#505050', '#606060', '#707070', '#808080']
        bg_color = 'white'
        text_color = 'black'
        edge = 'black'
    else:
        setup_color_style()
        suffix = ''
        colors_before = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        colors_after = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        bg_color = '#1a1a2e'
        text_color = 'white'
        edge = 'white'

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Before China ban (2021)
    ax1 = axes[0]
    countries_before = ['China', 'United States', 'Kazakhstan', 'Russia', 'Other']
    shares_before = [65, 7, 7, 7, 14]

    wedges1, texts1, autotexts1 = ax1.pie(shares_before, labels=countries_before,
                                           autopct='%1.0f%%', colors=colors_before,
                                           wedgeprops={'edgecolor': edge, 'linewidth': 1.5},
                                           textprops={'color': text_color})
    ax1.set_title('Global Hashrate Distribution\nPre-China Ban (May 2021)',
                  fontsize=14, fontweight='bold', color=text_color)

    # After events (2026)
    ax2 = axes[1]
    countries_after = ['United States', 'China (covert)', 'Kazakhstan', 'Russia', 'Other']
    shares_after = [38, 21, 12, 7, 22]

    wedges2, texts2, autotexts2 = ax2.pie(shares_after, labels=countries_after,
                                           autopct='%1.0f%%', colors=colors_after,
                                           wedgeprops={'edgecolor': edge, 'linewidth': 1.5},
                                           textprops={'color': text_color})
    ax2.set_title('Global Hashrate Distribution\nPost-Events (Feb 2026)',
                  fontsize=14, fontweight='bold', color=text_color)

    # Make text visible
    for texts in [texts1, texts2, autotexts1, autotexts2]:
        for text in texts:
            text.set_color(text_color if not bw else 'black')

    plt.suptitle('Geopolitical Events Reshaped Bitcoin Mining Geography',
                 fontsize=16, fontweight='bold', color=text_color, y=1.02)
    plt.tight_layout()

    out_dir = BW_DIR if bw else OUTPUT_DIR
    plt.savefig(out_dir / f'hashrate_geographic_shift{suffix}.png', dpi=150,
                bbox_inches='tight', facecolor=bg_color, edgecolor='none')
    plt.close()
    print(f"Created: hashrate_geographic_shift{suffix}.png")


def create_recovery_analysis_chart(data, bw=False):
    """Analyze recovery patterns across events"""
    if bw:
        setup_bw_style()
        suffix = '_bw'
        bg_color = 'white'
        text_color = 'black'
        scatter_color = 'black'
        edge = 'black'
    else:
        setup_color_style()
        suffix = ''
        bg_color = '#1a1a2e'
        text_color = 'white'
        scatter_color = '#4ECDC4'
        edge = 'white'

    fig, ax = plt.subplots(figsize=(12, 8))

    events = data['events']

    drops = []
    recoveries = []
    names = []
    event_types = []

    for e in events:
        drops.append(e['hashrate_drop_percent'])
        recoveries.append(e['recovery_time_days'])
        names.append(e['name'][:25])
        event_types.append(e['type'])

    # Size by hashrate before event
    sizes = [e['hashrate_before_eh'] / 3 for e in events]

    if bw:
        markers = {'military_action': 'o', 'regulatory_ban': 's', 'civil_unrest': '^',
                   'war_sanctions': 'D', 'energy_crisis': 'p'}
        for i, (d, r, n, t, s) in enumerate(zip(drops, recoveries, names, event_types, sizes)):
            ax.scatter(r, d, s=s, c='white', marker=markers.get(t, 'o'),
                      edgecolors='black', linewidth=2)
    else:
        colors_map = {'military_action': '#FF6B6B', 'regulatory_ban': '#4ECDC4',
                      'civil_unrest': '#45B7D1', 'war_sanctions': '#96CEB4',
                      'energy_crisis': '#FFEAA7'}
        for i, (d, r, n, t, s) in enumerate(zip(drops, recoveries, names, event_types, sizes)):
            ax.scatter(r, d, s=s, c=colors_map.get(t, '#FFFFFF'),
                      edgecolors='white', linewidth=1.5, alpha=0.8)

    # Add labels
    for i, (d, r, n) in enumerate(zip(drops, recoveries, names)):
        offset = (10, 5) if i != 1 else (10, -15)  # Adjust China label
        ax.annotate(n, (r, d), textcoords="offset points", xytext=offset,
                   fontsize=9, color=text_color)

    ax.set_xlabel('Recovery Time (Days)', fontsize=12)
    ax.set_ylabel('Hashrate Drop (%)', fontsize=12)
    ax.set_title('Event Severity vs Recovery Time\n(Bubble size = network hashrate at time of event)',
                 fontsize=14, fontweight='bold', color=text_color)

    # Add quadrant labels
    ax.axhline(y=25, color='gray', linestyle='--', alpha=0.3)
    ax.axvline(x=30, color='gray', linestyle='--', alpha=0.3)
    ax.text(5, 55, 'SEVERE\nQUICK RECOVERY', fontsize=10, color=text_color, alpha=0.5)
    ax.text(100, 55, 'SEVERE\nSLOW RECOVERY', fontsize=10, color=text_color, alpha=0.5)
    ax.text(5, 10, 'MILD\nQUICK', fontsize=10, color=text_color, alpha=0.5)

    # Legend for event types
    if bw:
        for etype, marker in markers.items():
            ax.scatter([], [], c='white', marker=marker, s=100, edgecolors='black',
                      linewidth=2, label=etype.replace('_', ' ').title())
    else:
        for etype, color in colors_map.items():
            ax.scatter([], [], c=color, s=100, edgecolors='white',
                      label=etype.replace('_', ' ').title())

    ax.legend(loc='upper right', frameon=True, edgecolor=edge,
              facecolor=bg_color if not bw else 'white',
              labelcolor=text_color)

    ax.set_xlim(0, 200)
    ax.set_ylim(0, 60)

    plt.tight_layout()

    out_dir = BW_DIR if bw else OUTPUT_DIR
    plt.savefig(out_dir / f'event_recovery_analysis{suffix}.png', dpi=150,
                bbox_inches='tight', facecolor=bg_color, edgecolor='none')
    plt.close()
    print(f"Created: event_recovery_analysis{suffix}.png")


def main():
    print("Loading geopolitical events data...")
    data = load_data()

    print("\nGenerating color visualizations...")
    create_event_comparison_chart(data, bw=False)
    create_timeline_chart(data, bw=False)
    create_iran_analysis_chart(data, bw=False)
    create_geographic_shift_chart(data, bw=False)
    create_recovery_analysis_chart(data, bw=False)

    print("\nGenerating B&W visualizations...")
    create_event_comparison_chart(data, bw=True)
    create_timeline_chart(data, bw=True)
    create_iran_analysis_chart(data, bw=True)
    create_geographic_shift_chart(data, bw=True)
    create_recovery_analysis_chart(data, bw=True)

    print("\nAll geopolitical charts generated!")


if __name__ == "__main__":
    main()
