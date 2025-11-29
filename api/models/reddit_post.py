from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class RedditComment:
    author: str
    body: str
    replies: Optional[List['RedditComment']] = field(default_factory=list)

@dataclass
class RedditPost:
    url: str
    relevance: bool
    title: str
    subtitle: str
    comments: List[RedditComment] = field(default_factory=list)
    ovarra_reply: Optional[str] = None

@dataclass
class RedditorCandidate:
    """Represents a Redditor extracted from posts before consolidation"""
    username: str
    source_post_url: str
    extraction_timestamp: datetime
    is_post_author: bool