import json, time, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone

SOURCES = [
    {"name": "JobInRwanda", "url": "https://www.jobinrwanda.com/jobs"},
    {"name": "MIFOTRA", "url": "https://recruitment.mifotra.gov.rw/"},
]
KEYWORDS = ["computer science", "information technology", "ict",
            "software", "developer", "systems", "network", "database"]
DEGREE_WORDS = ["bachelor", "bsc", "b.sc", "degree"]
HEADERS = {"User-Agent": "Mozilla/5.0 (personal job alert project)"}

def get_text(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def candidate_links(src):
    soup = BeautifulSoup(get_text(src["url"]), "html.parser")
    host = urlparse(src["url"]).netloc
    found = {}
    for a in soup.find_all("a", href=True):
        title = " ".join(a.get_text().split())
        link = urljoin(src["url"], a["href"])
        if len(title) >= 12 and urlparse(link).netloc == host:
            found[link] = title
    return list(found.items())[:60]  # be polite: max 60 pages

def main():
    results = []
    for src in SOURCES:
        try:
            for link, title in candidate_links(src):
                time.sleep(1)
                try:
                    page = BeautifulSoup(get_text(link), "html.parser").get_text(" ").lower()
                except Exception:
                    continue
                hits = [k for k in KEYWORDS if k in page]
                if hits and any(d in page for d in DEGREE_WORDS):
                    results.append({"source": src["name"], "title": title,
                                    "link": link, "matched": hits})
        except Exception as e:
            print("Failed:", src["name"], e)
    with open("jobs.json", "w") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(),
                   "jobs": results}, f, indent=2)

main()
