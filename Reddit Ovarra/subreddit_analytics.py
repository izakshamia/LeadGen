#!/usr/bin/env python3
"""
Subreddit Analytics and Discovery
Tracks performance metrics and discovers new related subreddits
"""

import json
import os
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict


class SubredditAnalytics:
    def __init__(self, stats_file: str = "subreddit_stats.json"):
        self.stats_file = stats_file
        self.stats = self.load_stats()
    
    def load_stats(self) -> Dict:
        """Load existing stats from file"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {
            "subreddits": {},
            "last_updated": None,
            "total_runs": 0
        }
    
    def save_stats(self):
        """Save stats to file"""
        self.stats["last_updated"] = datetime.now().isoformat()
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def update_subreddit_stats(self, subreddit: str, posts_scraped: int, relevant_posts: int):
        """Update statistics for a subreddit"""
        if subreddit not in self.stats["subreddits"]:
            self.stats["subreddits"][subreddit] = {
                "total_posts": 0,
                "total_relevant": 0,
                "runs": 0,
                "conversion_rate": 0.0,
                "first_seen": datetime.now().isoformat(),
                "last_scraped": None
            }
        
        sub_stats = self.stats["subreddits"][subreddit]
        sub_stats["total_posts"] += posts_scraped
        sub_stats["total_relevant"] += relevant_posts
        sub_stats["runs"] += 1
        sub_stats["last_scraped"] = datetime.now().isoformat()
        
        # Calculate conversion rate
        if sub_stats["total_posts"] > 0:
            sub_stats["conversion_rate"] = round(
                sub_stats["total_relevant"] / sub_stats["total_posts"], 3
            )
        
        self.stats["total_runs"] += 1
        self.save_stats()
    
    def get_top_subreddits(self, limit: int = 10, min_posts: int = 10) -> List[Dict]:
        """Get top performing subreddits by conversion rate"""
        subreddits = []
        for name, stats in self.stats["subreddits"].items():
            if stats["total_posts"] >= min_posts:
                subreddits.append({
                    "name": name,
                    "conversion_rate": stats["conversion_rate"],
                    "total_posts": stats["total_posts"],
                    "total_relevant": stats["total_relevant"],
                    "runs": stats["runs"]
                })
        
        # Sort by conversion rate
        subreddits.sort(key=lambda x: x["conversion_rate"], reverse=True)
        return subreddits[:limit]
    
    def get_low_performers(self, threshold: float = 0.05, min_posts: int = 20) -> List[str]:
        """Get subreddits with low conversion rates (candidates for removal)"""
        low_performers = []
        for name, stats in self.stats["subreddits"].items():
            if stats["total_posts"] >= min_posts and stats["conversion_rate"] < threshold:
                low_performers.append(name)
        return low_performers
    
    def discover_subreddits_from_posts(self, posts: List) -> Set[str]:
        """
        Discover new subreddits mentioned in posts and comments
        Looks for r/subreddit mentions
        """
        discovered = set()
        
        for post in posts:
            # Check post title and body
            text = f"{post.title} {post.subtitle}".lower()
            
            # Find r/subreddit mentions
            import re
            pattern = r'r/([a-zA-Z0-9_]+)'
            matches = re.findall(pattern, text)
            discovered.update(matches)
            
            # Check comments
            if hasattr(post, 'comments') and post.comments:
                for comment in post.comments:
                    if hasattr(comment, 'body'):
                        comment_matches = re.findall(pattern, comment.body.lower())
                        discovered.update(comment_matches)
        
        # Filter out common non-relevant subreddits
        excluded = {'all', 'popular', 'askreddit', 'pics', 'funny', 'videos'}
        discovered = {sub for sub in discovered if sub not in excluded}
        
        return discovered
    
    def get_recommended_subreddits(self) -> List[str]:
        """Get list of recommended subreddits based on performance"""
        top = self.get_top_subreddits(limit=20, min_posts=5)
        return [sub["name"] for sub in top if sub["conversion_rate"] > 0.1]
    
    def print_report(self):
        """Print analytics report"""
        print("\n" + "="*60)
        print("📊 SUBREDDIT ANALYTICS REPORT")
        print("="*60)
        
        print(f"\n📈 Total Pipeline Runs: {self.stats['total_runs']}")
        print(f"📅 Last Updated: {self.stats.get('last_updated', 'Never')}")
        
        # Top performers
        print("\n🏆 TOP PERFORMING SUBREDDITS:")
        print("-"*60)
        top = self.get_top_subreddits(limit=10)
        if top:
            for i, sub in enumerate(top, 1):
                print(f"{i}. r/{sub['name']}")
                print(f"   Conversion: {sub['conversion_rate']*100:.1f}% "
                      f"({sub['total_relevant']}/{sub['total_posts']} posts)")
                print(f"   Runs: {sub['runs']}")
        else:
            print("   No data yet. Run the pipeline first!")
        
        # Low performers
        low = self.get_low_performers()
        if low:
            print("\n⚠️  LOW PERFORMING SUBREDDITS (Consider removing):")
            print("-"*60)
            for sub in low:
                stats = self.stats["subreddits"][sub]
                print(f"   r/{sub}: {stats['conversion_rate']*100:.1f}% "
                      f"({stats['total_relevant']}/{stats['total_posts']} posts)")
        
        # All subreddits summary
        print("\n📋 ALL TRACKED SUBREDDITS:")
        print("-"*60)
        for name, stats in sorted(self.stats["subreddits"].items()):
            print(f"r/{name:20} | Posts: {stats['total_posts']:4} | "
                  f"Relevant: {stats['total_relevant']:3} | "
                  f"Rate: {stats['conversion_rate']*100:5.1f}%")
        
        print("\n" + "="*60)


def analyze_pipeline_results(scraped_file: str = "scraped_posts.json",
                            relevant_file: str = "relevant_posts.json"):
    """
    Analyze pipeline results and update subreddit statistics
    """
    from api_utils import posts_from_json
    
    analytics = SubredditAnalytics()
    
    # Load posts
    try:
        scraped_posts = posts_from_json(scraped_file)
        relevant_posts = posts_from_json(relevant_file)
    except FileNotFoundError:
        print("❌ Error: Run the pipeline first to generate data files")
        return
    
    # Count posts per subreddit
    subreddit_counts = defaultdict(lambda: {"scraped": 0, "relevant": 0})
    
    for post in scraped_posts:
        # Extract subreddit from URL
        import re
        match = re.search(r'reddit\.com/r/([^/]+)/', post.url)
        if match:
            subreddit = match.group(1)
            subreddit_counts[subreddit]["scraped"] += 1
    
    for post in relevant_posts:
        match = re.search(r'reddit\.com/r/([^/]+)/', post.url)
        if match:
            subreddit = match.group(1)
            subreddit_counts[subreddit]["relevant"] += 1
    
    # Update stats
    for subreddit, counts in subreddit_counts.items():
        analytics.update_subreddit_stats(
            subreddit,
            counts["scraped"],
            counts["relevant"]
        )
    
    # Discover new subreddits
    discovered = analytics.discover_subreddits_from_posts(scraped_posts)
    if discovered:
        print(f"\n🔍 Discovered {len(discovered)} new subreddits mentioned in posts:")
        for sub in sorted(discovered):
            if sub not in analytics.stats["subreddits"]:
                print(f"   • r/{sub} (NEW)")
    
    # Print report
    analytics.print_report()
    
    # Recommendations
    recommended = analytics.get_recommended_subreddits()
    if recommended:
        print("\n💡 RECOMMENDED SUBREDDITS FOR NEXT RUN:")
        print("-"*60)
        print(", ".join([f"r/{sub}" for sub in recommended]))
    
    return analytics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze subreddit performance")
    parser.add_argument('--scraped', default='scraped_posts.json',
                        help='Scraped posts file')
    parser.add_argument('--relevant', default='relevant_posts.json',
                        help='Relevant posts file')
    args = parser.parse_args()
    
    analyze_pipeline_results(args.scraped, args.relevant)
