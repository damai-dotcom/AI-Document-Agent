#!/bin/bash

# Confluence Finder - Data Import Script
# Purpose: Import data from data/confluence_export.json into vector database

echo "==================================="
echo "Confluence Finder Data Import Script"
echo "==================================="

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found. Please install Python 3.8+ first"
    exit 1
fi

# Ensure we're in the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check dependencies
if [ ! -d "backend/venv" ]; then
    echo "Warning: Virtual environment not found. Using system Python..."
    PYTHON_CMD="python3"
else
    echo "Using virtual environment..."
    source backend/venv/bin/activate
    PYTHON_CMD="python"
fi

# Check if export file exists
if [ ! -f "data/confluence_export.json" ]; then
    echo "Error: data/confluence_export.json file not found"
    echo "Please ensure the file exists in the project's data directory"
    exit 1
fi

# Check backend directory
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found"
    exit 1
fi

# Check data_importer.py
if [ ! -f "backend/data_importer.py" ]; then
    echo "Error: backend/data_importer.py file not found"
    exit 1
fi

echo "Starting data import..."
echo "Data source: data/confluence_export.json"
echo "==================================="

# 执行导入
time $PYTHON_CMD backend/data_importer.py import

if [ $? -eq 0 ]; then
    echo "==================================="
    echo "✅ Data import successful!"
    echo "==================================="
else
    echo "==================================="
    echo "❌ Data import failed!"
    echo "==================================="
    exit 1
fi

# Deactivate virtual environment if used
if [ -d "backend/venv" ]; then
    deactivate
fi