#!/usr/bin/env python3
"""
Railway start script - changes to Reddit Ovarra directory and starts uvicorn
"""
import os
import sys

# Change to the Reddit Ovarra directory
os.chdir('Reddit Ovarra')

# Add the directory to Python path
sys.path.insert(0, os.getcwd())

# Import and run uvicorn
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
