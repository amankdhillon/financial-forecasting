#!/usr/bin/env python3
"""
Add unique Organization ID column to CSV files
Keeps existing FIN-ID # column intact
"""

import pandas as pd
import os
from pathlib import Path
import re
import shutil

# Configuration
DATA_DIR = Path('data')
BACKUP_DIR = Path('data_backup')

def clean_organization_name(org_name):
    """Clean organization name to create a valid ID"""
    if pd.isna(org_name) or org_name == '':
        return 'UNKNOWN'
    
    # Remove special characters and spaces, convert to uppercase
    clean_name = re.sub(r'[^\w\s]', '', str(org_name))
    clean_name = re.sub(r'\s+', '_', clean_name.strip())
    clean_name = clean_name.upper()
    
    # Handle common abbreviations and clean up
    clean_name = clean_name.replace('ASSOCIATION', 'ASSOC')
    clean_name = clean_name.replace('STUDENT', 'STU')
    clean_name = clean_name.replace('ORGANIZATION', 'ORG')
    clean_name = clean_name.replace('COMPUTING', 'COMP')
    clean_name = clean_name.replace('ENGINEERING', 'ENG')
    clean_name = clean_name.replace('SCIENCE', 'SCI')
    
    # Truncate if too long
    if len(clean_name) > 30:
        clean_name = clean_name[:30]
    
    return clean_name

def create_organization_mapping(all_csv_files):
    """Create a mapping from organization names to unique IDs"""
    
    print("Analyzing all organizations across all files...")
    
    organizations = set()
    
    # Collect all unique organizations
    for filepath in all_csv_files:
        print(f"  Reading {filepath.name}...")
        try:
            df = pd.read_csv(filepath, header=0)
            if 'ORGANIZATION' in df.columns:
                orgs = df['ORGANIZATION'].dropna().unique()
                organizations.update(orgs)
        except Exception as e:
            print(f"    Error reading {filepath}: {e}")
    
    print(f"\nFound {len(organizations)} unique organizations")
    
    # Create mapping with sequential IDs
    org_mapping = {}
    org_counter = {}
    
    for org in sorted(organizations):
        clean_id = clean_organization_name(org)
        
        # Handle duplicates by adding counter
        if clean_id in org_counter:
            org_counter[clean_id] += 1
            final_id = f"{clean_id}_{org_counter[clean_id]:02d}"
        else:
            org_counter[clean_id] = 0
            final_id = f"{clean_id}_{org_counter[clean_id]+1:02d}"
            org_counter[clean_id] = 1
        
        org_mapping[org] = final_id
    
    return org_mapping

def transform_csv_file(filepath, org_mapping):
    """Transform a single CSV file by adding Organization ID column"""
    
    print(f"Transforming {filepath.name}...")
    
    try:
        # Read the file
        df = pd.read_csv(filepath, header=0)
        
        # Check if ORGANIZATION column exists
        if 'ORGANIZATION' not in df.columns:
            print(f"  Warning: ORGANIZATION column not found in {filepath.name}")
            return False
        
        # Create new Organization ID column
        org_ids = []
        
        for idx, row in df.iterrows():
            org_name = row['ORGANIZATION']
            
            if pd.isna(org_name) or org_name == '':
                org_id = 'UNKNOWN_01'
            else:
                org_id = org_mapping.get(org_name, 'UNKNOWN_01')
            
            org_ids.append(org_id)
        
        # Insert Organization ID as the first column
        df.insert(0, 'ORG_ID', org_ids)
        
        # Save the transformed file
        df.to_csv(filepath, index=False)
        
        print(f"  ✓ Added ORG_ID column with {len(set(org_ids))} unique organizations")
        return True
        
    except Exception as e:
        print(f"  ✗ Error transforming {filepath}: {e}")
        return False

def create_organization_reference(org_mapping, output_path):
    """Create a reference file showing organization ID mappings"""
    
    print(f"\nCreating organization reference file: {output_path}")
    
    # Create DataFrame with mapping
    ref_data = []
    for org_name, org_id in sorted(org_mapping.items()):
        ref_data.append({
            'Organization_ID': org_id,
            'Organization_Name': org_name
        })
    
    ref_df = pd.DataFrame(ref_data)
    ref_df.to_csv(output_path, index=False)
    
    print(f"  ✓ Created reference with {len(ref_df)} organizations")

def backup_files(csv_files, backup_dir):
    """Create backup of original files"""
    
    print(f"Creating backup in {backup_dir}...")
    backup_dir.mkdir(exist_ok=True)
    
    for filepath in csv_files:
        backup_path = backup_dir / filepath.name
        
        try:
            shutil.copy2(filepath, backup_path)
            print(f"  ✓ Backed up {filepath.name}")
        except Exception as e:
            print(f"  ✗ Error backing up {filepath.name}: {e}")

def main():
    """Main transformation function"""
    
    print("="*80)
    print("ADDING ORGANIZATION ID COLUMN TO CSV FILES")
    print("="*80)
    
    # Find all CSV files
    if not DATA_DIR.exists():
        print(f"Error: Data directory {DATA_DIR} not found!")
        return
    
    csv_files = list(DATA_DIR.glob("*.csv"))
    # Exclude any existing reference files
    csv_files = [f for f in csv_files if 'reference' not in f.name.lower()]
    
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return
    
    print(f"Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  - {f.name}")
    
    # Create backup
    backup_files(csv_files, BACKUP_DIR)
    
    # Create organization mapping
    org_mapping = create_organization_mapping(csv_files)
    
    # Transform each file
    print("\n" + "="*60)
    print("TRANSFORMING FILES")
    print("="*60)
    
    success_count = 0
    for filepath in csv_files:
        if transform_csv_file(filepath, org_mapping):
            success_count += 1
    
    # Create reference file
    ref_path = DATA_DIR / 'organization_id_reference.csv'
    create_organization_reference(org_mapping, ref_path)
    
    # Summary
    print("\n" + "="*80)
    print("TRANSFORMATION COMPLETE")
    print("="*80)
    print(f"Successfully transformed: {success_count}/{len(csv_files)} files")
    print(f"Total organizations: {len(org_mapping)}")
    print(f"Backup created in: {BACKUP_DIR}")
    print(f"Reference file: {ref_path}")
    
    # Show examples
    print("\nExample Organization IDs:")
    print("-" * 40)
    for i, (org_name, org_id) in enumerate(sorted(org_mapping.items())[:10]):
        print(f"{org_id:<25} → {org_name}")
        if i == 9 and len(org_mapping) > 10:
            print(f"... and {len(org_mapping) - 10} more")
    
    print("\nNew CSV structure:")
    print("  Column 0: ORG_ID (NEW - unique organization identifier)")
    print("  Column 1: FIN-ID # (unchanged)")
    print("  Column 2: ORGANIZATION (unchanged)")
    print("  ... (all other columns unchanged)")

if __name__ == "__main__":
    main()