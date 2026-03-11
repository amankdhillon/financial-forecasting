#!/usr/bin/env python3
"""
Updated data loading utilities for the new ORG_ID column
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import DATA_DIR, get_quarter_pattern

def _parse_messy_date(series):
    """Handle the doubled datetime format: '20240927T00:00:00Z   09/27/2024 12:00 AM'
    Extracts whichever token looks like a date and parses it."""
    import re
    def extract(val):
        val = str(val)
        # Try ISO compact first (e.g. 20240927T00:00:00Z)
        m = re.search(r'(\d{8})T\d{6}Z?', val)
        if m:
            return pd.to_datetime(m.group(1), format='%Y%m%d', errors='coerce')
        # Fallback: MM/DD/YYYY
        m = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', val)
        if m:
            return pd.to_datetime(m.group(1), errors='coerce')
        return pd.NaT
    return series.apply(extract)

def load_csv_file(filepath):
    """Load and clean a single CSV file with ORG_ID column"""
    try:
        # Read CSV file
        df = pd.read_csv(filepath, header=0, dtype=str)
        
        # Expected columns after transformation:
        # ORG_ID, FIN-ID #, ORGANIZATION, NAME OF EVENT, DATE, VENUE, AWARDED, TRANSACTION ID, UPDATED
        
        # Rename columns to standard format
        column_mapping = {
            'FIN-ID #': 'ID',
            'ORGANIZATION': 'Organization',
            'NAME OF EVENT': 'Event',
            'DATE': 'Event_Date',
            'VENUE': 'Location',
            'AWARDED': 'Amount',
            'TRANSACTION ID': 'Transaction_ID',
            'UPDATED': 'Submission_Date'
        }
        df = df.rename(columns=column_mapping)

        # Add ORG_ID column as NaN if not present (fall23.csv, fall24.csv don't have it)
        if 'ORG_ID' not in df.columns:
            df['ORG_ID'] = np.nan

        # Strip leading '* ' from ID column (keeps the row — asterisk is NOT a cancellation marker)
        if 'ID' in df.columns:
            df['ID'] = df['ID'].astype(str).str.replace(r'^\*\s*', '', regex=True).str.strip()

        # Clean amount column
        df['Amount'] = (
            df['Amount'].astype(str)
            .str.replace(r'[\$,\"]', '', regex=True)
            .str.strip()
        )
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

        # Parse dates — handles both clean and doubled-datetime formats
        df['Event_Date']      = _parse_messy_date(df['Event_Date'])
        df['Submission_Date'] = _parse_messy_date(df['Submission_Date'])

        # Remove rows with invalid amounts or dates
        df = df.dropna(subset=['Amount', 'Event_Date'])
        df = df[df['Amount'] > 0]

        return df
        
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None

def analyze_organizations_by_quarter(quarter_data):
    """Analyze organization participation by quarter using ORG_ID"""
    
    org_analysis = {}
    
    for quarter_name, df in quarter_data.items():
        if df is None or len(df) == 0:
            continue
        
        # Organizations by spending using ORG_ID
        org_spending = df.groupby('ORG_ID').agg({
            'Amount': ['sum', 'count', 'mean'],
            'Organization': 'first'  # Get the full organization name
        }).round(2)
        
        org_spending.columns = ['Total_Spending', 'Event_Count', 'Avg_Per_Event', 'Full_Name']
        org_spending = org_spending.sort_values('Total_Spending', ascending=False)
        
        org_analysis[quarter_name] = {
            'top_organizations': org_spending.head(10),
            'total_organizations': len(org_spending),
            'most_active': org_spending.sort_values('Event_Count', ascending=False).head(5),
            'highest_avg': org_spending[org_spending['Event_Count'] >= 2].sort_values('Avg_Per_Event', ascending=False).head(5)
        }
    
    return org_analysis

def get_quarter_summary_enhanced(df, quarter_name):
    """Enhanced quarter summary with ORG_ID organization analysis"""
    if df is None or len(df) == 0:
        return None
    
    # Basic summary
    org_counts = df['ORG_ID'].value_counts()
    org_spending = df.groupby('ORG_ID')['Amount'].sum() if df['ORG_ID'].notna().any() else pd.Series(dtype=float)

    summary = {
        'quarter': quarter_name,
        'total_spending': df['Amount'].sum(),
        'num_events': len(df),
        'avg_per_event': df['Amount'].mean(),
        'median_per_event': df['Amount'].median(),
        'date_range': (df['Event_Date'].min(), df['Event_Date'].max()),
        'num_organizations': df['ORG_ID'].nunique(),
        'most_active_org': org_counts.index[0] if len(org_counts) > 0 else None,
        'highest_spending_org': org_spending.idxmax() if len(org_spending) > 0 else None,
    }
    
    # Top organizations by spending using ORG_ID
    org_totals = df.groupby(['ORG_ID', 'Organization']).agg({
        'Amount': 'sum',
        'Event': 'count'
    }).reset_index()
    org_totals.columns = ['ORG_ID', 'Organization_Name', 'Total_Amount', 'Event_Count']
    org_totals = org_totals.sort_values('Total_Amount', ascending=False)
    
    summary['top_organizations'] = org_totals.head(5).set_index('ORG_ID')['Total_Amount'].to_dict()
    summary['monthly_spending'] = df.groupby(df['Event_Date'].dt.to_period('M'))['Amount'].sum().to_dict()
    
    return summary

def load_all_data():
    """Load all available CSV files and organize by quarter with ORG_ID tracking"""
    available_files = {}
    quarter_data = {}
    
    # Find all CSV files
    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        return {}, {}
    
    csv_files = list(DATA_DIR.glob("*.csv"))
    
    # Exclude reference file
    csv_files = [f for f in csv_files if 'reference' not in f.name.lower()]
    
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return {}, {}
    
    print(f"Found {len(csv_files)} CSV files:")
    
    # Process each file
    for filepath in csv_files:
        filename = filepath.name
        quarter = get_quarter_pattern(filename)
        
        if quarter:
            print(f"  ✓ {filename} → {quarter}")
            df = load_csv_file(filepath)
            
            if df is not None and len(df) > 0:
                available_files[quarter] = filename
                quarter_data[quarter] = df
                
                # Print organization info
                if 'ORG_ID' in df.columns:
                    org_count = df['ORG_ID'].nunique()
                    event_count = len(df)
                    total_spending = df['Amount'].sum()
                    print(f"    {org_count} organizations, {event_count} events, ${total_spending:,.2f}")
                else:
                    print(f"    Warning: ORG_ID column not found - run add_org_ids.py first")
            else:
                print(f"    Warning: No valid data found")
        else:
            print(f"  ⚠ {filename} → Could not determine quarter")
    
    print(f"\nSuccessfully loaded {len(quarter_data)} quarters of data")
    return quarter_data, available_files

if __name__ == "__main__":
    # Test the updated data loader
    quarter_data, available_files = load_all_data()
    
    if quarter_data:
        print("\nOrganization Analysis Sample:")
        print("="*60)
        
        # Show sample from one quarter
        sample_quarter = list(quarter_data.keys())[0]
        sample_df = quarter_data[sample_quarter]
        
        if 'ORG_ID' in sample_df.columns:
            print(f"\nSample from {sample_quarter}:")
            print(f"Top 5 Organizations by spending:")
            org_spending = sample_df.groupby(['ORG_ID', 'Organization']).agg({
                'Amount': 'sum',
                'Event': 'count'
            }).reset_index()
            org_spending.columns = ['ORG_ID', 'Full_Name', 'Total_Spending', 'Event_Count']
            org_spending = org_spending.sort_values('Total_Spending', ascending=False)
            
            for _, row in org_spending.head(5).iterrows():
                print(f"  {row['ORG_ID']}: ${row['Total_Spending']:,.2f} ({row['Event_Count']} events)")
                print(f"    Full name: {row['Full_Name']}")
        else:
            print("ORG_ID column not found. Run add_org_ids.py first.")