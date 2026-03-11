#!/usr/bin/env python3
"""
Comprehensive Funding Analysis and Visualization
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# Import configuration and data loader
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import OUTPUT_DIR, PLOT_CONFIG, ACADEMIC_STRUCTURE
from src.data_loader_with_org_id import load_all_data, get_quarter_summary_enhanced as get_quarter_summary

# Set plotting style
sns.set_style(PLOT_CONFIG['style'])
sns.set_palette(PLOT_CONFIG['palette'])
plt.rcParams['figure.dpi'] = PLOT_CONFIG['figure_dpi']
plt.rcParams['savefig.dpi'] = PLOT_CONFIG['save_dpi']
plt.rcParams['font.size'] = PLOT_CONFIG['font_size']

def create_academic_year_summary(quarter_data):
    """Create summary data for each academic year"""
    year_summary = {}
    
    for year, quarters in ACADEMIC_STRUCTURE.items():
        year_data = {
            'quarters': {},
            'total_spending': 0,
            'total_events': 0,
            'available_quarters': []
        }
        
        for quarter in quarters:
            if quarter in quarter_data:
                df = quarter_data[quarter]
                quarter_summary = get_quarter_summary(df, quarter)
                
                if quarter_summary:
                    year_data['quarters'][quarter] = quarter_summary
                    year_data['total_spending'] += quarter_summary['total_spending']
                    year_data['total_events'] += quarter_summary['num_events']
                    year_data['available_quarters'].append(quarter)
        
        if year_data['available_quarters']:
            year_summary[year] = year_data
    
    return year_summary

def plot_quarterly_spending(quarter_data, year_summary):
    """Create quarterly spending visualization"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    # Prepare data for plotting
    quarters = []
    spending = []
    colors = []
    
    # Define colors for each academic year
    year_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    color_map = {}
    
    for i, year in enumerate(sorted(year_summary.keys())):
        color_map[year] = year_colors[i % len(year_colors)]
    
    for year in sorted(year_summary.keys()):
        for quarter in ACADEMIC_STRUCTURE[year]:
            if quarter in quarter_data:
                summary = get_quarter_summary(quarter_data[quarter], quarter)
                if summary:
                    quarters.append(quarter.replace('_', ' '))
                    spending.append(summary['total_spending'])
                    colors.append(color_map[year])
    
    # Create bar plot
    bars = ax.bar(quarters, spending, color=colors, alpha=0.8)
    
    # Customize plot
    ax.set_title('Quarterly Spending Analysis', fontsize=16, fontweight='bold')
    ax.set_xlabel('Quarter', fontsize=12)
    ax.set_ylabel('Total Spending ($)', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    
    # Rotate x-axis labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1000:.0f}K', ha='center', va='bottom', fontsize=9)
    
    # Create legend for academic years
    legend_elements = []
    for year, color in color_map.items():
        legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.8, label=year))
    ax.legend(handles=legend_elements, title='Academic Year', loc='upper left')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '1_quarterly_spending.png', bbox_inches='tight')
    plt.close()

def plot_academic_year_totals(year_summary):
    """Create academic year total spending visualization"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Prepare data
    years = list(year_summary.keys())
    totals = [year_summary[year]['total_spending'] for year in years]
    event_counts = [year_summary[year]['total_events'] for year in years]
    
    # Spending totals
    bars1 = ax1.bar(years, totals, alpha=0.8, color='steelblue')
    ax1.set_title('Total Spending by Academic Year', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Total Spending ($)')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1000:.0f}K', ha='center', va='bottom')
    
    # Event counts
    bars2 = ax2.bar(years, event_counts, alpha=0.8, color='orange')
    ax2.set_title('Total Events by Academic Year', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of Events')
    
    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '2_academic_year_totals.png', bbox_inches='tight')
    plt.close()

def plot_spending_trends(quarter_data):
    """Create spending trend analysis"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Prepare data
    quarters = []
    spending = []
    events = []
    
    for quarter_name, df in quarter_data.items():
        summary = get_quarter_summary(df, quarter_name)
        if summary:
            quarters.append(quarter_name.replace('_', ' '))
            spending.append(summary['total_spending'])
            events.append(summary['num_events'])
    
    # Sort by academic year order
    quarter_order = []
    for year in sorted(ACADEMIC_STRUCTURE.keys()):
        for quarter in ACADEMIC_STRUCTURE[year]:
            if quarter in [q.replace(' ', '_') for q in quarters]:
                quarter_order.append(quarter.replace('_', ' '))
    
    # Reorder data
    ordered_spending = []
    ordered_events = []
    for quarter in quarter_order:
        idx = quarters.index(quarter)
        ordered_spending.append(spending[idx])
        ordered_events.append(events[idx])
    
    # Spending trend
    ax1.plot(quarter_order, ordered_spending, marker='o', linewidth=2, markersize=6)
    ax1.set_title('Spending Trends Over Time', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Total Spending ($)')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Event count trend
    ax2.plot(quarter_order, ordered_events, marker='s', linewidth=2, markersize=6, color='orange')
    ax2.set_title('Event Count Trends Over Time', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Quarter')
    ax2.set_ylabel('Number of Events')
    ax2.grid(True, alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '3_spending_trends.png', bbox_inches='tight')
    plt.close()

def generate_summary_report(quarter_data, year_summary, available_files):
    """Generate comprehensive text summary report"""
    
    report_path = OUTPUT_DIR / 'comprehensive_analysis_report.txt'
    
    with open(report_path, 'w') as f:
        f.write("COMPREHENSIVE FUNDING ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        
        # Overall summary
        total_spending = sum(year_summary[year]['total_spending'] for year in year_summary)
        total_events = sum(year_summary[year]['total_events'] for year in year_summary)
        
        f.write("OVERVIEW:\n")
        f.write("-"*40 + "\n")
        f.write(f"Total Academic Years Analyzed: {len(year_summary)}\n")
        f.write(f"Total Quarters Available: {len(quarter_data)}\n")
        f.write(f"Total Spending: ${total_spending:,.2f}\n")
        f.write(f"Total Events: {total_events}\n")
        f.write(f"Average per Event: ${total_spending/total_events:.2f}\n\n")
        
        # Academic year breakdown
        f.write("ACADEMIC YEAR BREAKDOWN:\n")
        f.write("-"*40 + "\n")
        for year in sorted(year_summary.keys()):
            data = year_summary[year]
            f.write(f"\n{year}:\n")
            f.write(f"  Total Spending: ${data['total_spending']:,.2f}\n")
            f.write(f"  Total Events: {data['total_events']}\n")
            f.write(f"  Available Quarters: {len(data['available_quarters'])}/3\n")
            f.write(f"  Quarters: {', '.join(data['available_quarters'])}\n")
        
        # Quarter-by-quarter details
        f.write("\n\nQUARTER-BY-QUARTER DETAILS:\n")
        f.write("-"*40 + "\n")
        
        for quarter_name, df in quarter_data.items():
            summary = get_quarter_summary(df, quarter_name)
            if summary:
                f.write(f"\n{quarter_name.replace('_', ' ')}:\n")
                f.write(f"  Total Spending: ${summary['total_spending']:,.2f}\n")
                f.write(f"  Number of Events: {summary['num_events']}\n")
                f.write(f"  Average per Event: ${summary['avg_per_event']:,.2f}\n")
                f.write(f"  Median per Event: ${summary['median_per_event']:,.2f}\n")
                f.write(f"  Date Range: {summary['date_range'][0].strftime('%m/%d/%Y')} to {summary['date_range'][1].strftime('%m/%d/%Y')}\n")
                f.write(f"  Top 3 Organizations:\n")
                for i, (org, amount) in enumerate(list(summary['top_organizations'].items())[:3]):
                    f.write(f"    {i+1}. {org}: ${amount:,.2f}\n")
    
    print(f"✓ Comprehensive report saved to: {report_path}")

def run_comprehensive_analysis():
    """Main function to run comprehensive analysis"""
    
    print("="*80)
    print("COMPREHENSIVE FUNDING ANALYSIS")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    quarter_data, available_files = load_all_data()
    
    if not quarter_data:
        print("No data available for analysis!")
        return
    
    print(f"✓ Loaded {len(quarter_data)} quarters of data\n")
    
    # Create academic year summary
    print("Creating academic year summary...")
    year_summary = create_academic_year_summary(quarter_data)
    print("✓ Academic year summary created\n")
    
    # Generate visualizations
    print("Generating visualizations...")
    print("-"*60)
    
    plot_quarterly_spending(quarter_data, year_summary)
    print("✓ Quarterly spending plot saved")
    
    plot_academic_year_totals(year_summary)
    print("✓ Academic year totals plot saved")
    
    plot_spending_trends(quarter_data)
    print("✓ Spending trends plot saved")
    
    # Generate summary report
    print("\nGenerating comprehensive report...")
    generate_summary_report(quarter_data, year_summary, available_files)
    
    print("\n" + "="*80)
    print("COMPREHENSIVE ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll outputs saved to: {OUTPUT_DIR}")
    print("\nGenerated files:")
    print("  1. 1_quarterly_spending.png - Quarterly spending comparison")
    print("  2. 2_academic_year_totals.png - Academic year totals")
    print("  3. 3_spending_trends.png - Spending and event trends")
    print("  4. comprehensive_analysis_report.txt - Detailed text report")
    print("  5. individual_quarters/ - Individual quarter analyses")
    print("="*80)

if __name__ == "__main__":
    run_comprehensive_analysis()