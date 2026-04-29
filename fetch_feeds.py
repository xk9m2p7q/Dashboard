import feedparser
import json
import time
from datetime import datetime, timezone

FEEDS = [
    {"url": "https://feeds.reuters.com/reuters/worldNews", "source": "Reuters", "region": "global", "tag": "global"},
    {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC World", "region": "global", "tag": "global"},
    {"url": "https://feeds.feedburner.com/al-monitor/wwpS", "source": "Al-Monitor", "region": "mena", "tag": "mena"},
    {"url": "https://www.moroccoworldnews.com/feed", "source": "Morocco World News", "region": "morocco", "tag": "mena"},
    {"url": "https://insightcrime.org/feed/", "source": "InSight Crime", "region": "latam", "tag": "latam"},
    {"url": "https://elpais.com/rss/america/portada/", "source": "El País América", "region": "latam", "tag": "latam"},
    {"url": "https://www.politico.eu/feed/", "source": "POLITICO Europe", "region": "europe", "tag": "eu"},
    {"url": "https://ecfr.eu/feed/", "source": "ECFR", "region": "europe", "tag": "eu"},
    {"url": "https://foreignpolicy.com/feed/", "source": "Foreign Policy", "region": "global", "tag": "global"},
    {"url": "https://warontherocks.com/feed/", "source": "War on the Rocks", "region": "global", "tag": "global"},
    {"url": "https://www.laprensa.com.pa/feed", "source": "La Prensa Panama", "region": "latam", "tag": "latam"},
    {"url": "https://www.middleeasteye.net/rss", "source": "Middle East Eye", "region": "mena", "tag": "mena"},
]

def time_ago(published):
    try:
        pub = datetime(*published[:6], tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - pub
        mins = int(diff.total_seconds() / 60)
        if mins < 60:
            return f"{mins}m ago"
        elif mins < 1440:
            return f"{mins // 60}h ago"
        else:
            return f"{mins // 1440}d ago"
    except:
        return ""

articles = []

for feed_info in FEEDS:
    try:
        feed = feedparser.parse(feed_info["url"])
        for entry in feed.entries[:8]:
            articles.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", ""))[:200].strip(),
                "source": feed_info["source"],
                "region": feed_info["region"],
                "tag": feed_info["tag"],
                "time": time_ago(entry.get("published_parsed") or entry.get("updated_parsed") or time.gmtime()),
            })
        time.sleep(1)
    except Exception as e
