#!/usr/bin/env python3
"""
Configuration settings for funding analysis
"""

import os
from pathlib import Path

# Base directory (where this script is located)
BASE_DIR = Path(__file__).parent.parent

# Data and output directories
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'outputs'
CONFIG_DIR = BASE_DIR / 'config'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Column names for CSV files
COLUMN_NAMES = [
    'ID', 'Organization', 'Event', 'Event_Date', 
    'Location', 'Amount', 'Unknown', 'Submission_Date'
]

# Academic year structure (Fall -> Winter -> Spring)
ACADEMIC_STRUCTURE = {
    '2025-26': ['Fall_25', 'Winter_26', 'Spring_26'],
    '2024-25': ['Fall_24', 'Winter_25', 'Spring_25'],
    '2023-24': ['Fall_23', 'Winter_24', 'Spring_24'],
    '2022-23': ['Fall_22', 'Winter_23', 'Spring_23'],
    '2021-22': ['Fall_21', 'Winter_22', 'Spring_22'],
    '2020-21': ['Fall_20', 'Winter_21', 'Spring_21'],
}

# Plot styling
PLOT_CONFIG = {
    'style': 'whitegrid',
    'palette': 'husl',
    'figure_dpi': 100,
    'save_dpi': 300,
    'font_size': 10
}

def get_quarter_pattern(filename):
    """Extract quarter pattern from filename — handles both spaced and compact names."""
    # Normalise: lowercase, remove dashes, collapse whitespace
    f = filename.lower().replace('-', ' ').replace('_', ' ')

    # Map longest/most-specific patterns first so 'winter 24' beats 'winter'
    patterns = [
        # with space variants (from "Funding Total..." filenames)
        ('spring 25', 'Spring_25'), ('winter 25', 'Winter_25'), ('fall 25', 'Fall_25'),
        ('spring 24', 'Spring_24'), ('winter 24', 'Winter_24'), ('fall 24', 'Fall_24'),
        ('spring 23', 'Spring_23'), ('winter 23', 'Winter_23'), ('fall 23', 'Fall_23'),
        # compact variants (from simple filenames like fall24.csv)
        ('spring25',  'Spring_25'), ('winter25',  'Winter_25'), ('fall25',  'Fall_25'),
        ('spring24',  'Spring_24'), ('winter24',  'Winter_24'), ('fall24',  'Fall_24'),
        ('spring23',  'Spring_23'), ('winter23',  'Winter_23'), ('fall23',  'Fall_23'),
    ]

    for pattern, quarter in patterns:
        if pattern in f:
            return quarter

    return None