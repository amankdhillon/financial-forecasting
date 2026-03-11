#!/usr/bin/env python3
"""
Individual Quarter Analysis and Visualization
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# Import configuration and data loader
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import OUTPUT_DIR, PLOT_CONFIG
from src.data_loader_with_org_id import load_all_data, get_quarter_summary_enhanced as get_quarter_summary

# Set plotting style
sns.set_style(PLOT_CONFIG['style'])
plt.rcParams['figure.dpi'] = PLOT_CONFIG['figure_dpi']
plt.rcParams['savefig.dpi'] = PLOT_CONFIG['save_dpi']
plt.rcParams['font.size'] = PLOT_CONFIG['font_size']

def create_quarter_plot(df, quarter_name, save_path):
    """Create time-series plot for a single quarter"""
    
    # Sort by date and create cumulative spending
    df_sorted = df.sort_values('Event_Date').copy()
    df_sorted['Cumulative_Spending'] = df_sorted['Amount'].cumsum()
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Top plot: Cumulative spending over time
    ax1.plot(df_sorted['Event_Date'], df_sorted['Cumulative_Spending'], 
             marker='o', markersize=3, linewidth=2, color='#1f77b4')
    ax1.set_title(f'{quarter_name} - Cumulative Spending Over Time', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Cumulative Spending ($)')
    ax1.grid(True, alpha=0.3)
    
    # Format y-axis as currency
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Bottom plot: Daily spending (bar chart)
    daily_spending = df_sorted.groupby(df_sorted['Event_Date'].dt.date)['Amount'].sum()
    ax2.bar(daily_spending.index, daily_spending.values, alpha=0.7, color='#ff7f0e')
    ax2.set_title('Daily Spending', fontsize=12)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Daily Spending ($)')
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Rotate x-axis labels
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    
    return save_path

def analyze_individual_quarters():
    """Analyze and visualize each quarter individually"""
    
    print("="*80)
    print("INDIVIDUAL QUARTER ANALYSIS")
    print("="*80)
    
    # Load data
    quarter_data, available_files = load_all_data()
    
    if not quarter_data:
        print("No data available for analysis!")
        return
    
    # Create individual quarter subdirectory
    quarter_output_dir = OUTPUT_DIR / 'individual_quarters'
    quarter_output_dir.mkdir(exist_ok=True)
    
    print(f"\nGenerating individual quarter visualizations...")
    print("-"*60)
    
    results = []
    
    for quarter_name, df in quarter_data.items():
        try:
            # Generate summary
            summary = get_quarter_summary(df, quarter_name)
            
            if summary:
                # Create plot
                plot_filename = f"{quarter_name.lower()}_analysis.png"
                save_path = quarter_output_dir / plot_filename
                
                create_quarter_plot(df, quarter_name, save_path)
                
                print(f"✓ {quarter_name}: ${summary['total_spending']:,.2f} "
                      f"({summary['num_events']} events)")
                
                results.append(summary)
            
        except Exception as e:
            print(f"✗ Error processing {quarter_name}: {str(e)}")
    
    # Print summary
    print("-"*60)
    print("\nQUARTER SUMMARY:")
    print("="*80)
    
    for result in sorted(results, key=lambda x: x['total_spending'], reverse=True):
        date_range = f"{result['date_range'][0].strftime('%m/%d/%Y')} to {result['date_range'][1].strftime('%m/%d/%Y')}"
        print(f"\n{result['quarter']}:")
        print(f"  Total Spending: ${result['total_spending']:,.2f}")
        print(f"  Number of Events: {result['num_events']}")
        print(f"  Average per Event: ${result['avg_per_event']:,.2f}")
        print(f"  Date Range: {date_range}")
    
    print(f"\n✓ Individual quarter plots saved to: {quarter_output_dir}")
    
    return results

if __name__ == "__main__":
    analyze_individual_quarters()