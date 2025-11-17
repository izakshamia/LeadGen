#!/usr/bin/env python3
"""
View subreddit analytics and performance metrics
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subreddit_analytics import SubredditAnalytics, analyze_pipeline_results
import argparse


def main():
    parser = argparse.ArgumentParser(description="View subreddit analytics")
    parser.add_argument('--update', action='store_true',
                        help='Update analytics from latest pipeline results')
    parser.add_argument('--top', type=int, default=10,
                        help='Number of top subreddits to show (default: 10)')
    parser.add_argument('--export', help='Export stats to JSON file')
    args = parser.parse_args()
    
    if args.update:
        print("🔄 Updating analytics from pipeline results...")
        analyze_pipeline_results()
    else:
        analytics = SubredditAnalytics()
        analytics.print_report()
        
        if args.export:
            import json
            with open(args.export, 'w') as f:
                json.dump(analytics.stats, f, indent=2)
            print(f"\n✅ Stats exported to {args.export}")


if __name__ == "__main__":
    main()
