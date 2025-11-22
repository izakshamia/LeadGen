from dataclasses import dataclass, field
from typing import List, Optional

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
