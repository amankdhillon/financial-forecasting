#!/usr/bin/env python3
"""
EXAMPLE: How to modify the scripts for your local environment

This file shows you exactly what to change in the main scripts
to run them on your own computer.
"""

# =============================================================================
# STEP 1: Change these paths to match YOUR computer
# =============================================================================

# Where your CSV files are located
DATA_DIR = "./data"  # Current directory/data folder
# Examples:
# DATA_DIR = "C:/Users/YourName/Documents/funding_data"  # Windows
# DATA_DIR = "/Users/yourname/Documents/funding_data"    # Mac
# DATA_DIR = "/home/yourname/funding_data"                # Linux

# Where you want graphs saved
OUTPUT_DIR = "./outputs"  # Current directory/outputs folder
# Examples:
# OUTPUT_DIR = "C:/Users/YourName/Documents/funding_graphs"  # Windows
# OUTPUT_DIR = "/Users/yourname/Documents/funding_graphs"    # Mac
# OUTPUT_DIR = "/home/yourname/funding_graphs"                # Linux

# =============================================================================
# STEP 2: Make sure these folders exist (or script will create them)
# =============================================================================

import os
from pathlib import Path

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# =============================================================================
# STEP 3: Run your script!
# =============================================================================

print("="*80)
print("TESTING CONFIGURATION")
print("="*80)
print(f"\nData Directory: {DATA_DIR}")
print(f"Output Directory: {OUTPUT_DIR}")
print()

# Check if data directory exists
if os.path.exists(DATA_DIR):
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    print(f"✓ Data directory exists")
    print(f"  Found {len(csv_files)} CSV file(s):")
    for f in csv_files:
        print(f"    • {f}")
else:
    print(f"✗ Data directory does NOT exist: {DATA_DIR}")
    print(f"  Create it and add your CSV files there!")

print()

# Check if output directory exists
if os.path.exists(OUTPUT_DIR):
    print(f"✓ Output directory exists: {OUTPUT_DIR}")
else:
    print(f"✓ Output directory will be created: {OUTPUT_DIR}")

print()
print("="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Copy DATA_DIR and OUTPUT_DIR paths from above")
print("2. Open 'individual_quarter_plots.py'")
print("3. Replace the DATA_DIR and OUTPUT_DIR variables at the top")
print("4. Do the same for 'funding_visualization_model.py'")
print("5. Run the scripts!")
print("="*80)

# =============================================================================
# QUICK TEST: Show how to load one CSV file
# =============================================================================

if os.path.exists(DATA_DIR):
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    if csv_files:
        print("\nQUICK TEST - Loading first CSV file...")
        print("-"*80)
        
        import pandas as pd
        
        test_file = os.path.join(DATA_DIR, csv_files[0])
        print(f"File: {csv_files[0]}")
        
        try:
            df = pd.read_csv(test_file, header=None)
            print(f"✓ Successfully loaded!")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print("\nFirst few rows:")
            print(df.head(3))
        except Exception as e:
            print(f"✗ Error loading file: {e}")