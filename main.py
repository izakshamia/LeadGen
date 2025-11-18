#!/usr/bin/env python3
"""
Root-level main.py for Railway deployment
Imports the FastAPI app from Reddit Ovarra subdirectory
"""
import sys
import os

# Add Reddit Ovarra directory to Python path
reddit_ovarra_path = os.path.join(os.path.dirname(__file__), 'Reddit Ovarra')
sys.path.insert(0, reddit_ovarra_path)

# Change working directory to Reddit Ovarra
os.chdir(reddit_ovarra_path)

# Import the FastAPI app
from main import app

# This allows Railway to detect and run the FastAPI app
__all__ = ['app']
