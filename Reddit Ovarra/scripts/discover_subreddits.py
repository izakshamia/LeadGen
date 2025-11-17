#!/usr/bin/env python3
"""
Discover new subreddits for the pipeline using multiple methods
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
from typing import Set, List, Dict
from collections import Counter
import re


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; OvarraBot/1.0)'
}

BASE_URL = "https://www.reddit.com"


def discover_from_seed_posts(seed_subreddit: str, keywords: List[str], limit: int = 50) -> Set[str]:
    """
    Method 1: Scan posts in seed subreddit for r/subreddit mentions
    """
    print(f"\n🔍 Method 1: Scanning r/{seed_subreddit} posts for mentions...")
    discovered = set()
    
    for keyword in keywords:
        url = f"{BASE_URL}/r/{seed_subreddit}/search.json"
        params = {'q': keyword, 'sort': 'new', 'limit': limit, 'restrict_sr': 1}
        
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if resp.status_code == 200:
                posts = resp.json().get('data', {}).get('children', [])
                
                for post in posts:
                    data = post.get('data', {})
                    text = f"{data.get('title', '')} {data.get('selftext', '')}".lower()
                    
                    # Find r/subreddit mentions
                    pattern = r'r/([a-zA-Z0-9_]+)'
                    matches = re.findall(pattern, text)
                    discovered.update(matches)
            
            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"   Error: {e}")
    
    # Filter out common non-relevant subreddits
    excluded = {'all', 'popular', 'askreddit', 'pics', 'funny', 'videos', 'news', 'worldnews'}
    discovered = {sub for sub in discovered if sub.lower() not in excluded}
    
    print(f"   Found {len(discovered)} subreddits mentioned in posts")
    return discovered


def discover_from_related(seed_subreddit: str) -> Set[str]:
    """
    Method 2: Use Reddit's related subreddits feature
    """
    print(f"\n🔍 Method 2: Finding related subreddits to r/{seed_subreddit}...")
    discovered = set()
    
    try:
        # Get subreddit info
        url = f"{BASE_URL}/r/{seed_subreddit}/about.json"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json().get('data', {})
            
            # Some subreddits have related communities in sidebar
            description = data.get('public_description', '') + data.get('description', '')
            pattern = r'r/([a-zA-Z0-9_]+)'
            matches = re.findall(pattern, description.lower())
            discovered.update(matches)
        
        time.sleep(2)
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"   Found {len(discovered)} related subreddits")
    return discovered


def discover_from_user_overlap(seed_subreddit: str, limit: int = 100) -> Set[str]:
    """
    Method 3: Find subreddits where the same users post
    """
    print(f"\n🔍 Method 3: Finding subreddits with user overlap...")
    discovered = Counter()
    
    try:
        # Get recent posts
        url = f"{BASE_URL}/r/{seed_subreddit}/new.json"
        params = {'limit': limit}
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if resp.status_code == 200:
            posts = resp.json().get('data', {}).get('children', [])
            authors = [post.get('data', {}).get('author') for post in posts[:20]]  # Top 20 authors
            
            # For each author, find their other subreddits
            for author in authors[:10]:  # Limit to 10 to avoid rate limits
                if author and author != '[deleted]':
                    user_url = f"{BASE_URL}/user/{author}/submitted.json"
                    user_params = {'limit': 25}
                    
                    try:
                        user_resp = requests.get(user_url, headers=HEADERS, params=user_params, timeout=10)
                        if user_resp.status_code == 200:
                            user_posts = user_resp.json().get('data', {}).get('children', [])
                            for post in user_posts:
                                subreddit = post.get('data', {}).get('subreddit')
                                if subreddit and subreddit.lower() != seed_subreddit.lower():
                                    discovered[subreddit.lower()] += 1
                        
                        time.sleep(3)  # Rate limiting
                    except:
                        continue
    except Exception as e:
        print(f"   Error: {e}")
    
    # Get top overlapping subreddits
    top_overlap = {sub for sub, count in discovered.most_common(20) if count >= 2}
    print(f"   Found {len(top_overlap)} subreddits with user overlap")
    return top_overlap


def discover_from_search(keywords: List[str], limit: int = 10) -> Set[str]:
    """
    Method 4: Search Reddit for keywords and find which subreddits have relevant posts
    """
    print(f"\n🔍 Method 4: Searching Reddit-wide for keywords...")
    discovered = Counter()
    
    for keyword in keywords[:3]:  # Limit to avoid rate limits
        try:
            url = f"{BASE_URL}/search.json"
            params = {'q': keyword, 'sort': 'relevance', 'limit': limit, 'type': 'link'}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
            
            if resp.status_code == 200:
                posts = resp.json().get('data', {}).get('children', [])
                for post in posts:
                    subreddit = post.get('data', {}).get('subreddit')
                    if subreddit:
                        discovered[subreddit.lower()] += 1
            
            time.sleep(3)  # Rate limiting
        except Exception as e:
            print(f"   Error with keyword '{keyword}': {e}")
    
    # Get subreddits that appear multiple times
    relevant = {sub for sub, count in discovered.most_common(30) if count >= 2}
    print(f"   Found {len(relevant)} subreddits with relevant content")
    return relevant


def get_subreddit_info(subreddit: str) -> Dict:
    """
    Get information about a subreddit
    """
    try:
        url = f"{BASE_URL}/r/{subreddit}/about.json"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json().get('data', {})
            return {
                'name': subreddit,
                'subscribers': data.get('subscribers', 0),
                'active_users': data.get('active_user_count', 0),
                'description': data.get('public_description', '')[:100],
                'nsfw': data.get('over18', False),
                'created': data.get('created_utc', 0)
            }
    except:
        pass
    
    return None


def check_creator_context(posts_data: List) -> Dict:
    """
    Analyze if posts are from CREATORS asking for help (not gamers/musicians)
    This filters out noise like gaming DMCA, music copyright, etc.
    """
    # Creator indicators (positive signals)
    creator_keywords = [
        'onlyfans', 'of', 'cam', 'chaturbate', 'stripchat', 'fansly',
        'content creator', 'my content', 'my videos', 'my photos',
        'leaked', 'leak', 'stolen', 'pirated', 'reposted',
        'help', 'advice', 'what do i do', 'how do i',
        'creator', 'model', 'performer', 'sex work'
    ]
    
    # Non-creator indicators (negative signals - filter these out)
    noise_keywords = [
        'game', 'gaming', 'steam', 'mod', 'minecraft', 'roblox',
        'music', 'song', 'album', 'spotify', 'soundcloud',
        'anime', 'manga', 'movie', 'tv show', 'netflix',
        'youtube', 'twitch streamer', 'discord bot',
        'dnd', 'dungeons', 'rpg'
    ]
    
    creator_score = 0
    noise_score = 0
    creator_posts = []
    
    for post in posts_data:
        title = post.get('data', {}).get('title', '').lower()
        selftext = post.get('data', {}).get('selftext', '').lower()
        text = f"{title} {selftext}"
        
        # Check for creator indicators
        post_creator_signals = sum(1 for kw in creator_keywords if kw in text)
        # Check for noise indicators
        post_noise_signals = sum(1 for kw in noise_keywords if kw in text)
        
        if post_creator_signals > post_noise_signals:
            creator_score += 1
            creator_posts.append(title[:80])
        elif post_noise_signals > 0:
            noise_score += 1
    
    total_posts = len(posts_data)
    creator_ratio = creator_score / max(total_posts, 1)
    
    return {
        'creator_posts': creator_score,
        'noise_posts': noise_score,
        'creator_ratio': creator_ratio,
        'sample_creator_posts': creator_posts[:3],
        'is_creator_focused': creator_ratio > 0.5  # More than 50% creator posts
    }


def check_keyword_relevance(subreddit: str, keywords: List[str]) -> Dict:
    """
    Check how many posts in the subreddit match our target keywords
    AND filter for creator-focused content (not gaming/music DMCA)
    """
    print(f"      Checking keyword relevance for r/{subreddit}...")
    all_matching_posts = []
    total_checked = 0
    
    try:
        # Search for each keyword in the subreddit
        for keyword in keywords[:3]:  # Check top 3 keywords
            url = f"{BASE_URL}/r/{subreddit}/search.json"
            params = {'q': keyword, 'sort': 'new', 'limit': 10, 'restrict_sr': 1}
            
            resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if resp.status_code == 200:
                posts = resp.json().get('data', {}).get('children', [])
                all_matching_posts.extend(posts)
                total_checked += 1
            
            time.sleep(1.5)
    except Exception as e:
        print(f"         Error: {e}")
    
    # Analyze creator context
    context = check_creator_context(all_matching_posts)
    
    # Only count creator-focused posts
    relevant_matches = context['creator_posts']
    avg_matches = relevant_matches / max(total_checked, 1)
    
    return {
        'keyword_matches': len(all_matching_posts),
        'creator_matches': relevant_matches,
        'noise_matches': context['noise_posts'],
        'avg_matches_per_keyword': avg_matches,
        'sample_posts': context['sample_creator_posts'],
        'is_creator_focused': context['is_creator_focused'],
        'creator_ratio': context['creator_ratio']
    }


def score_subreddit(info: Dict, keyword_data: Dict = None) -> float:
    """
    Score a subreddit based on relevance criteria
    PRIORITY: Creator-focused keyword relevance is most important!
    """
    if not info:
        return 0.0
    
    score = 0.0
    
    # CRITICAL FILTER: Must be creator-focused
    if keyword_data:
        is_creator_focused = keyword_data.get('is_creator_focused', False)
        creator_ratio = keyword_data.get('creator_ratio', 0)
        
        # If mostly noise (gaming/music DMCA), heavily penalize
        if not is_creator_focused:
            score -= 10.0  # Negative score for non-creator subreddits
            print(f"         ⚠️  Not creator-focused ({creator_ratio*100:.0f}% creator posts)")
            return max(score, 0)  # Don't go below 0
        
        # HIGHEST PRIORITY: Creator-focused keyword matches (0-15 points)
        creator_matches = keyword_data.get('creator_matches', 0)
        if creator_matches >= 10:
            score += 15.0  # Excellent - lots of creator posts
        elif creator_matches >= 7:
            score += 12.0  # Very good
        elif creator_matches >= 5:
            score += 9.0   # Good
        elif creator_matches >= 3:
            score += 6.0   # Decent
        elif creator_matches >= 1:
            score += 3.0   # Some relevant posts
        else:
            return 0.0  # No creator posts = irrelevant
    
    # Check description for creator/DMCA keywords (0-5 points)
    desc = info.get('description', '').lower()
    
    # High-value keywords (creator-focused)
    high_value = ['onlyfans', 'cam girl', 'cam model', 'content creator', 'sex work', 'adult creator']
    for keyword in high_value:
        if keyword in desc:
            score += 2.0
    
    # Medium-value keywords (problem-focused)
    medium_value = ['dmca', 'leak', 'copyright', 'privacy', 'stolen', 'piracy']
    for keyword in medium_value:
        if keyword in desc:
            score += 1.5
    
    # NSFW is relevant for adult content creators
    if info.get('nsfw'):
        score += 2.0
    
    # Size matters (but not too much) (0-2 points)
    subs = info.get('subscribers', 0)
    if 1000 <= subs <= 50000:
        score += 2.0   # Sweet spot - engaged community
    elif 50000 <= subs <= 200000:
        score += 1.5   # Good size
    elif 200000 <= subs <= 500000:
        score += 1.0   # Large but still manageable
    elif subs > 500000:
        score += 0.5   # Too big, posts get lost
    
    # Active community (0-1 point)
    if info.get('active_users', 0) > 50:
        score += 1.0
    
    return score


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Discover new subreddits for the pipeline")
    parser.add_argument('--seed', default='CamGirlProblems',
                        help='Seed subreddit to start discovery from')
    parser.add_argument('--keywords', nargs='+',
                        default=['onlyfans leak', 'dmca', 'content stolen', 'cam girl'],
                        help='Keywords to search for')
    parser.add_argument('--methods', nargs='+',
                        choices=['posts', 'related', 'users', 'search', 'all'],
                        default=['all'],
                        help='Discovery methods to use')
    parser.add_argument('--limit', type=int, default=50,
                        help='Number of posts to analyze per method')
    args = parser.parse_args()
    
    print("="*60)
    print("🔍 SUBREDDIT DISCOVERY TOOL")
    print("="*60)
    print(f"Seed: r/{args.seed}")
    print(f"Keywords: {', '.join(args.keywords)}")
    print(f"Methods: {', '.join(args.methods)}")
    
    all_discovered = set()
    
    # Run discovery methods
    if 'all' in args.methods or 'posts' in args.methods:
        discovered = discover_from_seed_posts(args.seed, args.keywords, args.limit)
        all_discovered.update(discovered)
    
    if 'all' in args.methods or 'related' in args.methods:
        discovered = discover_from_related(args.seed)
        all_discovered.update(discovered)
    
    if 'all' in args.methods or 'users' in args.methods:
        discovered = discover_from_user_overlap(args.seed, args.limit)
        all_discovered.update(discovered)
    
    if 'all' in args.methods or 'search' in args.methods:
        discovered = discover_from_search(args.keywords, args.limit)
        all_discovered.update(discovered)
    
    # Remove seed subreddit
    all_discovered.discard(args.seed.lower())
    
    print(f"\n📊 TOTAL DISCOVERED: {len(all_discovered)} unique subreddits")
    
    # Get info and score each subreddit
    print(f"\n⏳ Fetching subreddit information and checking keyword relevance...")
    scored_subreddits = []
    
    for i, subreddit in enumerate(sorted(all_discovered), 1):
        print(f"   [{i}/{len(all_discovered)}] r/{subreddit}")
        info = get_subreddit_info(subreddit)
        if info:
            # Check keyword relevance (most important!)
            keyword_data = check_keyword_relevance(subreddit, args.keywords)
            score = score_subreddit(info, keyword_data)
            
            # Store with keyword data for display
            info['keyword_matches'] = keyword_data.get('keyword_matches', 0)
            info['creator_matches'] = keyword_data.get('creator_matches', 0)
            info['noise_matches'] = keyword_data.get('noise_matches', 0)
            info['creator_ratio'] = keyword_data.get('creator_ratio', 0)
            info['sample_posts'] = keyword_data.get('sample_posts', [])
            info['is_creator_focused'] = keyword_data.get('is_creator_focused', False)
            
            scored_subreddits.append((score, info))
            
            if score > 0:
                print(f"      ✅ Score: {score:.1f} | Creator posts: {keyword_data.get('creator_matches', 0)} | Noise: {keyword_data.get('noise_matches', 0)}")
            else:
                print(f"      ❌ Filtered out (not creator-focused)")
        time.sleep(2)  # Rate limiting
    
    # Sort by score
    scored_subreddits.sort(reverse=True, key=lambda x: x[0])
    
    # Print recommendations
    print("\n" + "="*60)
    print("🏆 TOP RECOMMENDED SUBREDDITS")
    print("="*60)
    
    print("\n✅ HIGH PRIORITY (Score >= 10.0) - CREATOR-FOCUSED:")
    high_priority = [s for s in scored_subreddits if s[0] >= 10.0]
    if high_priority:
        for score, info in high_priority:
            print(f"\nr/{info['name']}")
            print(f"   Score: {score:.1f}")
            print(f"   Creator Posts: {info.get('creator_matches', 0)} (✅ {info.get('creator_ratio', 0)*100:.0f}% creator-focused)")
            print(f"   Noise Posts: {info.get('noise_matches', 0)} (gaming/music DMCA)")
            print(f"   Subscribers: {info['subscribers']:,}")
            print(f"   Active: {info['active_users']}")
            print(f"   NSFW: {'Yes' if info['nsfw'] else 'No'}")
            print(f"   Description: {info['description']}")
            if info.get('sample_posts'):
                print(f"   Sample creator posts:")
                for post_title in info['sample_posts']:
                    print(f"      • {post_title}")
    else:
        print("   None found - try different keywords or seed subreddit")
    
    print("\n⚠️  MEDIUM PRIORITY (Score 6.0-9.9):")
    medium_priority = [s for s in scored_subreddits if 6.0 <= s[0] < 10.0]
    if medium_priority:
        for score, info in medium_priority[:10]:  # Top 10
            creator_pct = info.get('creator_ratio', 0) * 100
            print(f"   r/{info['name']:25} | Score: {score:.1f} | Creator: {info.get('creator_matches', 0):2} ({creator_pct:.0f}%) | Subs: {info['subscribers']:,}")
    else:
        print("   None found")
    
    print("\n❌ FILTERED OUT (Not creator-focused):")
    filtered = [s for s in scored_subreddits if s[0] <= 0]
    if filtered:
        for score, info in filtered[:5]:  # Show top 5 filtered
            print(f"   r/{info['name']:25} | Reason: Gaming/Music DMCA (not creators)")
    else:
        print("   None filtered")
    
    print("\n💡 SUGGESTED DEFAULT_SUBREDDITS (Creator-focused only):")
    print("-"*60)
    top_names = [info['name'] for score, info in scored_subreddits[:10] if score >= 6.0 and info.get('is_creator_focused')]
    if top_names:
        print(f'DEFAULT_SUBREDDITS = {top_names}')
        print(f"\n📊 Expected Performance (Creator posts only):")
        for score, info in scored_subreddits[:5]:
            if score >= 6.0 and info.get('is_creator_focused'):
                creator_posts = info.get('creator_matches', 0)
                creator_pct = info.get('creator_ratio', 0) * 100
                print(f"   r/{info['name']:20} - {creator_posts} creator posts ({creator_pct:.0f}% creator-focused)")
    else:
        print("❌ No creator-focused subreddits found with current keywords")
        print("\n💡 Suggestions:")
        print("   • Try seed: OnlyFansAdvice, CreatorAdvice, SexWorkersOnly")
        print("   • Use keywords: 'onlyfans leak', 'cam girl help', 'content stolen'")
        print("   • Check if subreddits are private or banned")
    
    print("\n" + "="*60)
    print("✅ Discovery complete!")


if __name__ == "__main__":
    main()
