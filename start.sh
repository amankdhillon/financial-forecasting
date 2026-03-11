#!/bin/bash
# Starts the Vite dev server for the dashboard.
# Edit as_funding_dashboard.jsx freely — changes appear instantly in the browser.
# Run ./run.sh first if you've updated CSV data files.
set -e
cd "$(dirname "$0")"

if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found — install from https://nodejs.org"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "Installing JS dependencies (first run only)..."
    npm install
fi

echo "Starting dashboard at http://localhost:5173"
echo "Edit as_funding_dashboard.jsx and the browser updates automatically."
echo "Press Ctrl+C to stop."
echo ""
npm run dev
