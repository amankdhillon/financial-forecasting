#!/usr/bin/env python3
"""
Main script to run all analyses
"""

from pathlib import Path
import sys

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.quarterly_analysis import analyze_individual_quarters
from src.comprehensive_analysis import run_comprehensive_analysis
from src.data_loader_with_org_id import load_all_data, analyze_organizations_by_quarter

def main():
    """Run all analyses with organization tracking"""
    
    print("FUNDING ANALYSIS SUITE")
    print("="*80)
    print("Now with Organization-Based Unique IDs")
    print("="*80)
    print()
    
    # Load data with new ORG_ID column
    print("Loading data with organization IDs...")
    quarter_data, available_files = load_all_data()
    
    if not quarter_data:
        print("No data available for analysis!")
        return
    
    # Analyze organizations across quarters
    print("\nSTEP 1: Organization Analysis Across Quarters")
    print("-"*60)
    org_analysis = analyze_organizations_by_quarter(quarter_data)
    
    for quarter, analysis in org_analysis.items():
        print(f"\n{quarter}:")
        print(f"  Total Organizations: {analysis['total_organizations']}")
        if len(analysis['top_organizations']) > 0:
            top_org = analysis['top_organizations'].iloc[0]
            print(f"  Top Spender: {analysis['top_organizations'].index[0]} "
                  f"(${top_org['Total_Spending']:,.2f})")
            most_active = analysis['most_active'].iloc[0]
            print(f"  Most Active: {analysis['most_active'].index[0]} "
                  f"({most_active['Event_Count']} events)")
    
    # Run individual quarter analysis
    print("\nSTEP 2: Individual Quarter Analysis")
    print("-"*40)
    try:
        analyze_individual_quarters()
        print("✓ Individual quarter analysis complete\n")
    except Exception as e:
        print(f"✗ Error in individual quarter analysis: {str(e)}\n")
    
    # Run comprehensive analysis
    print("STEP 3: Comprehensive Analysis")
    print("-"*40)
    try:
        run_comprehensive_analysis()
        print("✓ Comprehensive analysis complete\n")
    except Exception as e:
        print(f"✗ Error in comprehensive analysis: {str(e)}\n")
    
    print("="*80)
    print("ALL ANALYSES COMPLETE")
    print("="*80)
    print()
    print("New CSV Structure:")
    print("  Column 0: ORG_ID - Unique organization identifier")
    print("  Column 1: FIN-ID # - Original financial ID")
    print("  Column 2: ORGANIZATION - Full organization name")
    print()
    print("Check the outputs directory for visualizations and reports.")
    print("Check data/organization_id_reference.csv for organization mappings.")

if __name__ == "__main__":
    main()