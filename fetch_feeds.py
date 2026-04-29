import feedparser
import json
import re
import time
from datetime import datetime, timezone

FEEDS = [
    # GLOBAL WIRE
    {"url": "https://feeds.reuters.com/reuters/worldNews", "source": "Reuters", "region": "global", "tag": "global"},
    {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC World", "region": "global", "tag": "global"},
    {"url": "https://apnews.com/rss/world-news", "source": "AP World", "region": "global", "tag": "global"},
    {"url": "https://rss.france24.com/rss/en/world", "source": "France 24", "region": "global", "tag": "global"},
    {"url": "https://foreignpolicy.com/feed/", "source": "Foreign Policy", "region": "global", "tag": "global"},
    {"url": "https://warontherocks.com/feed/", "source": "War on the Rocks", "region": "global", "tag": "global"},
    {"url": "https://www.economist.com/international/rss.xml", "source": "The Economist", "region": "global", "tag": "global"},
    # EUROPE
    {"url": "https://www.politico.eu/feed/", "source": "POLITICO Europe", "region": "europe", "tag": "eu"},
    {"url": "https://ecfr.eu/feed/", "source": "ECFR", "region": "europe", "tag": "eu"},
    {"url": "https://euobserver.com/rss/articles", "source": "EUobserver", "region": "europe", "tag": "eu"},
    {"url": "https://www.euractiv.com/feed/", "source": "Euractiv", "region": "europe", "tag": "eu"},
    {"url": "https://www.theguardian.com/world/europe/rss", "source": "The Guardian", "region": "europe", "tag": "eu"},
    {"url": "https://www.spiegel.de/international/index.rss", "source": "Der Spiegel", "region": "europe", "tag": "eu"},
    # SPAIN
    {"url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "source": "El Pais", "region": "spain", "tag": "eu"},
    {"url": "https://www.elmundo.es/rss/portada.xml", "source": "El Mundo", "region": "spain", "tag": "eu"},
    {"url": "https://www.elconfidencial.com/rss/", "source": "El Confidencial", "region": "spain", "tag": "eu"},
    {"url": "https://www.lavanguardia.com/rss/home.xml", "source": "La Vanguardia", "region": "spain", "tag": "eu"},
    # MENA
    {"url": "https://www.aljazeera.com/xml/rss/all.xml", "source": "Al Jazeera", "region": "mena", "tag": "mena"},
    {"url": "https://www.middleeasteye.net/rss", "source": "Middle East Eye", "region": "mena", "tag": "mena"},
    {"url": "https://www.moroccoworldnews.com/feed", "source": "Morocco World News", "region": "morocco", "tag": "mena"},
    {"url": "https://english.alarabiya.net/tools/rss", "source": "Al Arabiya", "region": "mena", "tag": "mena"},
    {"url": "https://www.arabnews.com/rss.xml", "source": "Arab News", "region": "mena", "tag": "mena"},
    {"url": "https://iranintl.com/en/rss.xml", "source": "Iran International", "region": "mena", "tag": "mena"},
    {"url": "https://www.yabiladi.com/rss/actu.xml", "source": "Yabiladi", "region": "morocco", "tag": "mena"},
    # LATIN AMERICA
    {"url": "https://insightcrime.org/feed/", "source": "InSight Crime", "region": "latam", "tag": "latam"},
    {"url": "https://elpais.com/rss/america/portada/", "source": "El Pais America", "region": "latam", "tag": "latam"},
    {"url": "https://www.laprensa.com.pa/feed", "source": "La Prensa Panama", "region": "latam", "tag": "latam"},
    {"url": "https://www.americasquarterly.org/feed/", "source": "Americas Quarterly", "region": "latam", "tag": "latam"},
    {"url": "https://mercopress.com/rss/rss.xml", "source": "MercoPress", "region": "latam", "tag": "latam"},
    {"url": "https://efectococuyo.com/feed/", "source": "Efecto Cocuyo", "region": "venezuela", "tag": "latam"},
    {"url": "https://talcualdigital.com/feed/", "source": "Tal Cual", "region": "venezuela", "tag": "latam"},
    {"url": "https://www.elnacional.com/feed/", "source": "El Nacional", "region": "venezuela", "tag": "latam"},
    # ACADEMIC & THINK TANKS
    {"url": "https://carnegieendowment.org/rss/solr/posts?lang=en", "source": "Carnegie Endowment", "region": "academic", "tag": "academic"},
    {"url": "https://www.brookings.edu/feed/", "source": "Brookings", "region": "academic", "tag": "academic"},
    {"url": "https://www.chathamhouse.org/rss.xml", "source": "Chatham House", "region": "academic", "tag": "academic"},
    {"url": "https://www.rand.org/rss/research.xml", "source": "RAND", "region": "academic", "tag": "academic"},
    {"url": "https://www.crisisgroup.org/rss.xml", "source": "Crisis Group", "region": "academic", "tag": "academic"},
    {"url": "https://www.csis.org/rss.xml", "source": "CSIS", "region": "academic", "tag": "academic"},
    {"url": "https://www.iiss.org/rss", "source": "IISS", "region": "academic", "tag": "academic"},
    {"url": "https://www.realinstitutoelcano.org/rss/", "source": "Elcano Institute", "region": "academic", "tag": "academic"},
    {"url": "https://www.wilsoncenter.org/rss.xml", "source": "Wilson Center", "region": "academic", "tag": "academic"},
    {"url": "https://www.stimson.org/feed/", "source": "Stimson Center", "region": "academic", "tag": "academic"},
    {"url": "https://foreignaffairs.com/rss.xml", "source": "Foreign Affairs", "region": "academic", "tag": "academic"},
    {"url": "https://blogs.lse.ac.uk/ideas/feed/", "source": "LSE IDEAS", "region": "academic", "tag": "academic"},
]


def time_ago(published):
    try:
        pub = datetime(*published[:6], tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - pub
        mins = int(diff.total_seconds() / 60)
        if mins < 60:
            return str(mins) + "m ago"
        elif mins < 1440:
            return str(mins // 60) + "h ago"
        else:
            return str(mins // 1440) + "d ago"
    except Exception:
        return ""


def get_timestamp(published):
    try:
        return int(datetime(*published[:6], tzinfo=timezone.utc).timestamp())
    except Exception:
        return 0


articles = []
failed = []

for feed_info in FEEDS:
    try:
        feed = feedparser.parse(feed_info["url"])
        count = 0
        for entry in feed.entries[:6]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            if not title or not link:
                continue
            summary = entry.get("summary", entry.get("description", ""))
            if summary:
                summary = re.sub(r'<[^>]+>', '', summary)[:200].strip()
            pub = entry.get("published_parsed") or entry.get("updated_parsed") or None
            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": feed_info["source"],
                "region": feed_info["region"],
                "tag": feed_info["tag"],
                "time": time_ago(pub) if pub else "",
                "timestamp": get_timestamp(pub) if pub else 0,
            })
            count += 1
        print("OK: " + feed_info["source"] + " (" + str(count) + ")")
        time.sleep(0.5)
    except Exception as ex:
        print("FAIL: " + feed_info["source"] + " - " + str(ex))
        failed.append(feed_info["source"])

articles.sort(key=lambda x: x["timestamp"], reverse=True)

output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "articles": articles,
    "failed_sources": failed,
    "total": len(articles)
}

with open("feeds.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Total: " + str(len(articles)) + " articles from " + str(len(FEEDS) - len(failed)) + " sources")
