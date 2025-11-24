#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Startup Script
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import flask
        import chromadb
        import sentence_transformers
        print("✅ Dependencies check passed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_data():
    """Check if data exists"""
    if not os.path.exists('./data/confluence_export.json'):
        print("❌ Data file not found: ./data/confluence_export.json")
        return False
    
    if not os.path.exists('./chroma_db'):
        print("❌ Vector database not found, please run: python init_data.py")
        return False
    
    print("✅ Data check passed")
    return True

def main():
    """Main function"""
    print("🚀 Confluence Finder Startup Check")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check data
    if not check_data():
        return
    
    print("\n🎉 Starting RAG service...")
    print("Access URL: http://localhost:5001")
    print("Press Ctrl+C to stop service")
    print("=" * 40)
    
    # Start service
    try:
        from rag_service import app
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Service stopped")
    except Exception as e:
        print(f"❌ Startup failed: {e}")

if __name__ == '__main__':
    main()