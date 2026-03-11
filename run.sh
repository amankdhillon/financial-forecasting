#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=============================================="
echo "  FUNDING ANALYSIS SUITE"
echo "=============================================="
echo ""

# ── Step 1: Python analysis ──────────────────────
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

echo "Step 1: Installing Python dependencies..."
pip3 install -q -r requirements.txt

echo ""
echo "Step 2: Running all analyses (8 quarters)..."
python3 main.py

echo ""
echo "Step 3: Regenerating dashboard JSON from CSVs..."
python3 generate_dashboard_data.py

echo ""
echo "=============================================="
echo "  DATA REFRESH COMPLETE"
echo "=============================================="
echo ""
echo "Outputs saved to: outputs/ and public/dashboard_data.json"
echo ""
echo "To view/reload the dashboard run:  ./start.sh"
echo ""
