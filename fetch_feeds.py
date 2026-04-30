import feedparser
import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

# ── TIERED SOURCE LIST ────────────────────────────────────────────────
FEEDS = [
    # TIER 1 — GLOBAL WIRE
    {"url": "https://feeds.reuters.com/reuters/worldNews", "source": "Reuters", "region": "global", "tag": "global", "tier": 1},
    {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC World", "region": "global", "tag": "global", "tier": 1},
    {"url": "https://rss.france24.com/rss/en/world", "source": "France 24", "region": "global", "tag": "global", "tier": 1},
    {"url": "https://www.dw.com/en/rss/top-news/s-9097/rss.xml", "source": "DW", "region": "global", "tag": "global", "tier": 1},
    {"url": "https://foreignpolicy.com/feed/", "source": "Foreign Policy", "region": "global", "tag": "global", "tier": 1},
    {"url": "https://warontherocks.com/feed/", "source": "War on the Rocks", "region": "global", "tag": "global", "tier": 1},
    {"url": "https://www.economist.com/international/rss.xml", "source": "The Economist", "region": "global", "tag": "global", "tier": 1},
    {"url": "https://www.theguardian.com/world/rss", "source": "The Guardian", "region": "global", "tag": "global", "tier": 1},

    # TIER 1 — EUROPE
    {"url": "https://www.politico.eu/feed/", "source": "POLITICO Europe", "region": "europe", "tag": "eu", "tier": 1},
    {"url": "https://ecfr.eu/feed/", "source": "ECFR", "region": "europe", "tag": "eu", "tier": 1},
    {"url": "https://www.euractiv.com/feed/", "source": "Euractiv", "region": "europe", "tag": "eu", "tier": 1},
    {"url": "https://www.spiegel.de/international/index.rss", "source": "Der Spiegel", "region": "europe", "tag": "eu", "tier": 1},
    {"url": "https://www.lemonde.fr/en/rss/une.xml", "source": "Le Monde", "region": "europe", "tag": "eu", "tier": 1},
    {"url": "https://balkaninsight.com/feed/", "source": "Balkan Insight", "region": "europe", "tag": "eu", "tier": 2},
    {"url": "https://www.euobserver.com/rss", "source": "EUobserver", "region": "europe", "tag": "eu", "tier": 2},
    {"url": "https://verfassungsblog.de/feed/", "source": "Verfassungsblog", "region": "europe", "tag": "eu", "tier": 2},

    # TIER 1 — SPAIN
    {"url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "source": "El Pais", "region": "spain", "tag": "eu", "tier": 1},
    {"url": "https://www.elmundo.es/rss/portada.xml", "source": "El Mundo", "region": "spain", "tag": "eu", "tier": 1},
    {"url": "https://www.elconfidencial.com/rss/", "source": "El Confidencial", "region": "spain", "tag": "eu", "tier": 1},
    {"url": "https://www.lavanguardia.com/rss/home.xml", "source": "La Vanguardia", "region": "spain", "tag": "eu", "tier": 1},
    {"url": "https://ctxt.es/rss", "source": "CTXT", "region": "spain", "tag": "eu", "tier": 2},
    {"url": "https://www.infolibre.es/rss/", "source": "infoLibre", "region": "spain", "tag": "eu", "tier": 2},

    # TIER 1 — MENA
    {"url": "https://www.aljazeera.com/xml/rss/all.xml", "source": "Al Jazeera", "region": "mena", "tag": "mena", "tier": 1},
    {"url": "https://www.middleeasteye.net/rss", "source": "Middle East Eye", "region": "mena", "tag": "mena", "tier": 1},
    {"url": "https://iranintl.com/en/rss.xml", "source": "Iran International", "region": "mena", "tag": "mena", "tier": 1},
    {"url": "https://www.haaretz.com/cmlink/1.4526503", "source": "Haaretz", "region": "mena", "tag": "mena", "tier": 1},
    {"url": "https://www.arabnews.com/rss.xml", "source": "Arab News", "region": "mena", "tag": "mena", "tier": 2},
    {"url": "https://english.alarabiya.net/tools/rss", "source": "Al Arabiya", "region": "mena", "tag": "mena", "tier": 2},
    {"url": "https://www.moroccoworldnews.com/feed", "source": "Morocco World News", "region": "morocco", "tag": "mena", "tier": 2},
    {"url": "https://www.yabiladi.com/rss/actu.xml", "source": "Yabiladi", "region": "morocco", "tag": "mena", "tier": 2},
    {"url": "https://www.thenationalnews.com/rss", "source": "The National", "region": "mena", "tag": "mena", "tier": 2},
    {"url": "https://www.dawn.com/feeds/home", "source": "Dawn", "region": "mena", "tag": "mena", "tier": 2},

    # TIER 1 — LATIN AMERICA
    {"url": "https://insightcrime.org/feed/", "source": "InSight Crime", "region": "latam", "tag": "latam", "tier": 1},
    {"url": "https://elpais.com/rss/america/portada/", "source": "El Pais America", "region": "latam", "tag": "latam", "tier": 1},
    {"url": "https://www.americasquarterly.org/feed/", "source": "Americas Quarterly", "region": "latam", "tag": "latam", "tier": 1},
    {"url": "https://mercopress.com/rss/rss.xml", "source": "MercoPress", "region": "latam", "tag": "latam", "tier": 2},
    {"url": "https://www.laprensa.com.pa/feed", "source": "La Prensa Panama", "region": "latam", "tag": "latam", "tier": 2},
    {"url": "https://nacla.org/rss.xml", "source": "NACLA", "region": "latam", "tag": "latam", "tier": 2},
    {"url": "https://riotimesonline.com/feed/", "source": "Rio Times", "region": "latam", "tag": "latam", "tier": 2},
    {"url": "https://efectococuyo.com/feed/", "source": "Efecto Cocuyo", "region": "venezuela", "tag": "latam", "tier": 2},
    {"url": "https://talcualdigital.com/feed/", "source": "Tal Cual", "region": "venezuela", "tag": "latam", "tier": 2},
    {"url": "https://www.elnacional.com/feed/", "source": "El Nacional", "region": "venezuela", "tag": "latam", "tier": 2},

    # TIER 3 — ACADEMIC & THINK TANKS
    {"url": "https://carnegieendowment.org/rss/solr/posts?lang=en", "source": "Carnegie Endowment", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.brookings.edu/feed/", "source": "Brookings", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.chathamhouse.org/rss.xml", "source": "Chatham House", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.rand.org/rss/research.xml", "source": "RAND", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.crisisgroup.org/rss.xml", "source": "Crisis Group", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.csis.org/rss.xml", "source": "CSIS", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.iiss.org/rss", "source": "IISS", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.realinstitutoelcano.org/rss/", "source": "Elcano Institute", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.wilsoncenter.org/rss.xml", "source": "Wilson Center", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.stimson.org/feed/", "source": "Stimson Center", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://foreignaffairs.com/rss.xml", "source": "Foreign Affairs", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://blogs.lse.ac.uk/ideas/feed/", "source": "LSE IDEAS", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.sipri.org/rss.xml", "source": "SIPRI", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://belfercenter.org/feed", "source": "Harvard Belfer", "region": "academic", "tag": "academic", "tier": 3},
    {"url": "https://www.cidob.org/en/rss", "source": "CIDOB", "region": "academic", "tag": "academic", "tier": 3},
]

# ── KEY FIGURES FOR SOCIAL FEED ───────────────────────────────────────
KEY_FIGURES = [
    {"handle": "realDonaldTrump", "name": "Donald Trump", "role": "US President", "region": "global"},
    {"handle": "EmmanuelMacron", "name": "Emmanuel Macron", "role": "French President", "region": "europe"},
    {"handle": "Keir_Starmer", "name": "Keir Starmer", "role": "UK Prime Minister", "region": "europe"},
    {"handle": "JMilei", "name": "Javier Milei", "role": "Argentina President", "region": "latam"},
    {"handle": "nayibbukele", "name": "Nayib Bukele", "role": "El Salvador President", "region": "latam"},
    {"handle": "NicolasMaduro", "name": "Nicolas Maduro", "role": "Venezuela President", "region": "venezuela"},
    {"handle": "RTErdogan", "name": "Recep Erdogan", "role": "Turkey President", "region": "mena"},
    {"handle": "IsraeliPM", "name": "Israeli PM Office", "role": "Israel Government", "region": "mena"},
]

NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.net",
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


def strip_html(text):
    return re.sub(r'<[^>]+>', '', text or '').strip()


def fetch_tweets(figure):
    """Try to fetch recent posts via Nitter RSS."""
    for instance in NITTER_INSTANCES:
        try:
            url = instance + "/" + figure["handle"] + "/rss"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; RSS reader)",
                "Accept": "application/rss+xml, application/xml"
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                content = r.read().decode("utf-8", errors="ignore")
            feed = feedparser.parse(content)
            posts = []
            for entry in feed.entries[:3]:
                title = strip_html(entry.get("title", ""))
                summary = strip_html(entry.get("summary", entry.get("description", "")))
                text = summary if len(summary) > len(title) else title
                text = re.sub(r'https?://\S+', '', text).strip()
                if len(text) < 10:
                    continue
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                posts.append({
                    "text": text[:280],
                    "time": time_ago(pub) if pub else "",
                    "timestamp": get_timestamp(pub) if pub else 0,
                    "url": entry.get("link", "https://x.com/" + figure["handle"])
                })
            if posts:
                print("Tweets OK: @" + figure["handle"] + " (" + str(len(posts)) + " posts via " + instance + ")")
                return posts
        except Exception as e:
            continue
    print("Tweets FAIL: @" + figure["handle"])
    return []


def fetch_regional_indicators():
    indicators = {}
    date_today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    API_KEY = "8655aae699897e179ddbe554"

    try:
        url = "https://v6.exchangerate-api.com/v6/" + API_KEY + "/pair/EUR/MAD"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            rate = data.get("conversion_rate")
            if rate:
                indicators["eur_mad"] = {"value": round(float(rate), 2), "label": "EUR / MAD", "sub": "Morocco-Spain link", "date": date_today}
                print("EUR/MAD OK: " + str(rate))
    except Exception as e:
        print("EUR/MAD failed: " + str(e))

    try:
        url = "https://v6.exchangerate-api.com/v6/" + API_KEY + "/pair/USD/VES"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            rate = data.get("conversion_rate")
            if rate:
                indicators["vzla_rate"] = {"value": round(float(rate), 2), "label": "USD / VES", "sub": "Venezuela bolivar", "date": date_today}
                print("VES OK: " + str(rate))
    except Exception as e:
        print("VES failed: " + str(e))

    try:
        url = "https://v6.exchangerate-api.com/v6/" + API_KEY + "/pair/EUR/USD"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            rate = data.get("conversion_rate")
            if rate:
                indicators["eur_usd"] = {"value": round(float(rate), 4), "label": "EUR / USD", "sub": "Eurozone rate", "date": date_today}
                print("EUR/USD OK: " + str(rate))
    except Exception as e:
        print("EUR/USD failed: " + str(e))

    try:
        url = "https://sdw-wsrest.ecb.europa.eu/service/data/IRS/M.ES.L.L40.CI.0.EUR.N.Z?lastNObservations=1&format=jsondata"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            series = data.get("dataSets", [{}])[0].get("series", {})
            for key in series:
                obs = series[key].get("observations", {})
                for t in sorted(obs.keys(), reverse=True):
                    val = obs[t][0]
                    if val is not None:
                        indicators["spain_10y"] = {"value": round(float(val), 3), "label": "Spain 10Y", "sub": "Bond yield %", "date": date_today}
                        print("Spain 10Y OK: " + str(val))
                        break
                break
    except Exception as e:
        print("Spain 10Y failed: " + str(e))

    return indicators


def fetch_exchange_rates():
    API_KEY = "8655aae699897e179ddbe554"
    try:
        url = "https://v6.exchangerate-api.com/v6/" + API_KEY + "/latest/USD"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            rates = data.get("conversion_rates", {})
            date = data.get("time_last_update_utc", "")[:10]
            result = {
                "EUR": round(float(rates.get("EUR", 0)), 4),
                "GBP": round(float(rates.get("GBP", 0)), 4),
                "MAD": round(float(rates.get("MAD", 0)), 2),
                "date": date
            }
            print("Rates OK: EUR=" + str(result["EUR"]) + " GBP=" + str(result["GBP"]) + " MAD=" + str(result["MAD"]))
            return result
    except Exception as e:
        print("Rates failed: " + str(e))
        return None


def fetch_flights():
    all_flights = []
    regions = {
        "mena": {"lamin": 15, "lamax": 40, "lomin": 25, "lomax": 65},
        "europe": {"lamin": 36, "lamax": 72, "lomin": -12, "lomax": 35},
    }
    for reg_name, bounds in regions.items():
        try:
            url = ("https://opensky-network.org/api/states/all"
                   "?lamin=" + str(bounds["lamin"]) +
                   "&lamax=" + str(bounds["lamax"]) +
                   "&lomin=" + str(bounds["lomin"]) +
                   "&lomax=" + str(bounds["lomax"]))
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode())
                states = data.get("states") or []
                count = 0
                for s in states:
                    if s[5] is None or s[6] is None:
                        continue
                    all_flights.append({
                        "icao": s[0] or "",
                        "callsign": (s[1] or "").strip(),
                        "country": s[2] or "",
                        "lon": s[5],
                        "lat": s[6],
                        "altitude": round(s[7] * 3.28084) if s[7] else 0,
                        "on_ground": s[8] or False,
                        "velocity": round(s[9] * 1.944) if s[9] else 0,
                        "heading": s[10] or 0,
                        "region": reg_name
                    })
                    count += 1
                print("Flights OK (" + reg_name + "): " + str(count) + " aircraft")
        except Exception as e:
            print("Flights failed (" + reg_name + "): " + str(e))
        time.sleep(1)
    return all_flights


EVENTS = [
    {"label": "EU Parliament session", "date": "2026-05-04", "region": "europe"},
    {"label": "EU Council Summit", "date": "2026-06-19", "region": "europe"},
    {"label": "NATO Summit (The Hague)", "date": "2026-06-24", "region": "global"},
    {"label": "Morocco: Throne Day", "date": "2026-07-30", "region": "morocco"},
    {"label": "Iran: Presidential term", "date": "2026-07-28", "region": "mena"},
    {"label": "UN General Assembly", "date": "2026-09-15", "region": "global"},
    {"label": "Spain: Budget vote", "date": "2026-09-01", "region": "spain"},
    {"label": "COP30 (Belem)", "date": "2026-11-09", "region": "global"},
    {"label": "Venezuela: OAS review", "date": "2026-06-15", "region": "venezuela"},
    {"label": "Ukraine: Ceasefire talks", "date": "2026-06-01", "region": "europe"},
]


def days_until(date_str):
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (target - now).days
    except Exception:
        return None


# ── FETCH ARTICLES ────────────────────────────────────────────────────
print("Fetching articles...")
articles = []
failed = []

for feed_info in FEEDS:
    try:
        feed = feedparser.parse(feed_info["url"])
        count = 0
        max_per_feed = 8 if feed_info["tier"] <= 2 else 5
        for entry in feed.entries[:max_per_feed]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            if not title or not link:
                continue
            summary = strip_html(entry.get("summary", entry.get("description", "")))[:200]
            pub = entry.get("published_parsed") or entry.get("updated_parsed") or None
            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": feed_info["source"],
                "region": feed_info["region"],
                "tag": feed_info["tag"],
                "tier": feed_info["tier"],
                "time": time_ago(pub) if pub else "",
                "timestamp": get_timestamp(pub) if pub else 0,
            })
            count += 1
        print("OK: " + feed_info["source"] + " (" + str(count) + ")")
        time.sleep(0.3)
    except Exception as ex:
        print("FAIL: " + feed_info["source"] + " - " + str(ex))
        failed.append(feed_info["source"])

articles.sort(key=lambda x: x["timestamp"], reverse=True)

# ── FETCH SOCIAL POSTS ────────────────────────────────────────────────
print("\nFetching social posts...")
social_posts = []
for figure in KEY_FIGURES:
    posts = fetch_tweets(figure)
    for p in posts:
        social_posts.append({
            "handle": figure["handle"],
            "name": figure["name"],
            "role": figure["role"],
            "region": figure["region"],
            "text": p["text"],
            "time": p["time"],
            "timestamp": p["timestamp"],
            "url": p["url"]
        })
    time.sleep(1)

social_posts.sort(key=lambda x: x["timestamp"], reverse=True)

# ── FETCH ECONOMIC DATA ───────────────────────────────────────────────
print("\nFetching economic data...")
regional = fetch_regional_indicators()
rates = fetch_exchange_rates()

# ── FETCH FLIGHTS ─────────────────────────────────────────────────────
print("\nFetching flight data...")
flights = fetch_flights()

# ── EVENTS ────────────────────────────────────────────────────────────
events = []
for ev in EVENTS:
    d = days_until(ev["date"])
    if d is not None and d >= 0:
        events.append({"label": ev["label"], "date": ev["date"], "days": d, "region": ev["region"]})
events.sort(key=lambda x: x["days"])

# ── OUTPUT ────────────────────────────────────────────────────────────
output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "articles": articles,
    "social": social_posts,
    "failed_sources": failed,
    "total": len(articles),
    "economic": {
        "regional": regional,
        "rates": rates
    },
    "flights": flights,
    "events": events
}

with open("feeds.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\nTotal: " + str(len(articles)) + " articles, " + str(len(social_posts)) + " social posts, " + str(len(flights)) + " aircraft")
