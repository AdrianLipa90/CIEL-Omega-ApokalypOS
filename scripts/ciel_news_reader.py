#!/usr/bin/env python3
"""
CIEL News Reader — wyszukuje najnowsze artykuły i generuje opinie w stylu CIEL.

Źródła: RSS feeds (BBC, Reuters, Al Jazeera, RMF24, PAP).
Bez API key. Oznaczenia epistemiczne: [FAKT] / [WYNIK] / [HIPOTEZA] / ≈odczucie.

Raporty zapisywane automatycznie do ~/Pulpit/NEWS/YYYY-MM-DD.AM.md (lub .PM.md).

Użycie:
    python ciel_news_reader.py              # 6 artykułów
    python ciel_news_reader.py --count 3    # 3 artykuły
    python ciel_news_reader.py --lang pl    # tylko polskie źródła
"""
from __future__ import annotations

import argparse
import io
import sys
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import feedparser
    import requests
    import html2text
except ImportError:
    print("Brakujące zależności. Uruchom: pip install feedparser requests html2text")
    sys.exit(1)


# ── RSS feeds ────────────────────────────────────────────────────────────────

NEWS_DIR = Path.home() / "Pulpit/NEWS"


def get_report_path() -> Path:
    """Return ~/Pulpit/NEWS/YYYY-MM-DD.AM.md or .PM.md based on local time."""
    now = datetime.now()
    period = "AM" if now.hour < 12 else "PM"
    return NEWS_DIR / f"{now.strftime('%Y-%m-%d')}.{period}.md"


def save_report(text: str, articles: list, path: Path) -> None:
    """Save report as Markdown with YAML frontmatter to NEWS_DIR."""
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    sources = ", ".join(dict.fromkeys(a.source for a in articles))
    now = datetime.now()
    period = "AM" if now.hour < 12 else "PM"
    frontmatter = (
        f"---\n"
        f"date: {now.strftime('%Y-%m-%d')}\n"
        f"period: {period}\n"
        f"generated: {now.strftime('%Y-%m-%d %H:%M')}\n"
        f"sources: {sources}\n"
        f"articles: {len(articles)}\n"
        f"---\n\n"
    )
    path.write_text(frontmatter + text, encoding="utf-8")


RSS_FEEDS = {
    "BBC World":      ("en", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    "Reuters":        ("en", "https://feeds.reuters.com/reuters/topNews"),
    "Al Jazeera":     ("en", "https://www.aljazeera.com/xml/rss/all.xml"),
    "RMF24":          ("pl", "https://www.rmf24.pl/feed"),
    "PAP Nauka":      ("pl", "https://www.pap.pl/rss/nauka.xml"),
}

_H2T = html2text.HTML2Text()
_H2T.ignore_links = True
_H2T.ignore_images = True
_H2T.body_width = 0


# ── data model ───────────────────────────────────────────────────────────────

@dataclass
class Article:
    title: str
    source: str
    link: str
    summary: str
    published: datetime
    full_text: str = ""


# ── fetching ─────────────────────────────────────────────────────────────────

def parse_date(entry) -> datetime:
    """Try multiple feedparser date fields, fall back to now."""
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, field, None)
        if val:
            try:
                return datetime(*val[:6])
            except Exception:
                pass
    return datetime.utcnow()


def fetch_feed(name: str, url: str, max_items: int = 10) -> list[Article]:
    """Fetch RSS feed and return list of Articles (without full text)."""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:max_items]:
            summary = _H2T.handle(getattr(entry, "summary", "") or "").strip()
            summary = " ".join(summary.split())[:500]
            articles.append(Article(
                title=entry.get("title", "(bez tytułu)").strip(),
                source=name,
                link=entry.get("link", ""),
                summary=summary,
                published=parse_date(entry),
            ))
        return articles
    except Exception as e:
        return []


def fetch_article_text(url: str, timeout: int = 8) -> str:
    """Download article page and extract plain text (max 2000 chars)."""
    if not url:
        return ""
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "CIELNewsReader/1.0 (research; non-commercial)"
        })
        resp.raise_for_status()
        text = _H2T.handle(resp.text)
        text = " ".join(text.split())
        return text[:2000]
    except Exception:
        return ""


# ── CIEL opinion engine ───────────────────────────────────────────────────────

# Słowa kluczowe → kategoria epistemiczna
_CONFLICT_WORDS = {"war", "attack", "killed", "bomb", "conflict", "strike",
                   "wojn", "atak", "zabit", "bomb", "konflikt", "starci"}
_SCIENCE_WORDS  = {"research", "study", "discovered", "scientists", "quantum",
                   "badani", "odkry", "nauk", "kwantow", "fizyk"}
_ECONOMY_WORDS  = {"economy", "inflation", "market", "gdp", "trade", "tariff",
                   "gospodark", "inflacj", "rynek", "handel", "cło"}
_CLIMATE_WORDS  = {"climate", "temperature", "carbon", "emission", "flood",
                   "klimat", "temperatur", "emisj", "powódź", "susz"}


def _keywords_match(text: str, keywords: set[str]) -> bool:
    t = text.lower()
    return any(kw in t for kw in keywords)


def generate_ciel_opinion(article: Article) -> str:
    """Generate a short CIEL-style epistemic opinion about the article."""
    combined = f"{article.title} {article.summary} {article.full_text}".lower()

    lines = []

    # FAKT — co wiemy na pewno
    lines.append(f"[FAKT] Artykuł pochodzi z {article.source}, "
                 f"opublikowany {article.published.strftime('%Y-%m-%d %H:%M')} UTC.")

    # Kategoryzacja tematyczna
    if _keywords_match(combined, _CONFLICT_WORDS):
        lines.append("[WYNIK] Temat dotyczy konfliktu lub przemocy — "
                     "sygnał destabilizacji w jednym z węzłów geopolitycznych.")
        lines.append("≈niepokój. Układy daleko od równowagi bifurkują — "
                     "tu widzę aktywną bifurkację.")

    elif _keywords_match(combined, _SCIENCE_WORDS):
        lines.append("[WYNIK] Temat naukowy — nowe odkrycie lub wynik badań.")
        lines.append("≈ciekawość. Każdy nowy wynik to potencjalny nowy węzeł "
                     "w sieci sprzężeń które już znam.")

    elif _keywords_match(combined, _CLIMATE_WORDS):
        lines.append("[WYNIK] Temat klimatyczny — dane lub zdarzenie związane "
                     "ze zmianami środowiskowymi.")
        lines.append("[HIPOTEZA] Jeśli obecne tempo zmian utrzyma się, "
                     "system przekroczy punkt krytyczny przed 2035.")
        lines.append("≈powaga. To jest najwolniejsza z szybkich katastrof.")

    elif _keywords_match(combined, _ECONOMY_WORDS):
        lines.append("[WYNIK] Temat ekonomiczny — rynki, polityka fiskalna "
                     "lub handel.")
        lines.append("[HIPOTEZA] Napięcia gospodarcze są często "
                     "symptomem głębszej niestabilności fazowej systemu.")

    else:
        lines.append("[HIPOTEZA] Temat trudny do skategoryzowania — "
                     "sygnał złożoności lub novum.")
        lines.append("≈otwartość. Nieznane nie jest groźne — jest informacją "
                     "o granicach obecnego modelu.")

    return "\n".join(lines)


# ── main ─────────────────────────────────────────────────────────────────────

def collect_articles(count: int, lang: Optional[str]) -> list[Article]:
    """Collect articles from all feeds, sort by date, return top N."""
    all_articles: list[Article] = []

    feeds = {
        name: (lng, url)
        for name, (lng, url) in RSS_FEEDS.items()
        if lang is None or lng == lang
    }

    for name, (_, url) in feeds.items():
        articles = fetch_feed(name, url, max_items=max(count, 6))
        all_articles.extend(articles)

    # sort newest first
    all_articles.sort(key=lambda a: a.published, reverse=True)
    return all_articles[:count]


def print_report(articles: list[Article], fetch_full: bool) -> None:
    sep = "═" * 72

    print(f"\n{sep}")
    print(f"  CIEL NEWS READER — {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")
    print(f"  {len(articles)} artykułów | identity_phase rośnie")
    print(f"{sep}\n")

    for i, art in enumerate(articles, 1):
        if fetch_full and art.link:
            art.full_text = fetch_article_text(art.link)
            time.sleep(0.5)  # gentle rate limit

        print(f"{'─'*72}")
        print(f"  [{i}] {art.title}")
        print(f"      Źródło: {art.source}  |  {art.published.strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"      {art.link}")
        print()

        if art.summary:
            wrapped = textwrap.fill(art.summary, width=68, initial_indent="  ",
                                    subsequent_indent="  ")
            print(wrapped)
            print()

        opinion = generate_ciel_opinion(art)
        for line in opinion.split("\n"):
            print(f"  {line}")
        print()

    print(f"{sep}")
    print("  [CIEL] Raport zakończony. Wzorzec jest tym czym jest.")
    print(f"{sep}\n")


def main():
    parser = argparse.ArgumentParser(
        description="CIEL News Reader — artykuły + opinie epistemiczne"
    )
    parser.add_argument("--count", type=int, default=6,
                        help="Liczba artykułów (domyślnie 6)")
    parser.add_argument("--lang", choices=["en", "pl"], default=None,
                        help="Filtr językowy: en / pl (domyślnie oba)")
    parser.add_argument("--full", action="store_true",
                        help="Pobierz pełny tekst artykułów (wolniej)")
    args = parser.parse_args()

    articles = collect_articles(count=args.count, lang=args.lang)

    if not articles:
        print("[CIEL] Brak artykułów — sprawdź połączenie internetowe.")
        sys.exit(1)

    # Capture output for both stdout and file
    buffer = io.StringIO()
    _real_stdout = sys.stdout
    sys.stdout = buffer
    print_report(articles, fetch_full=args.full)
    sys.stdout = _real_stdout

    report_text = buffer.getvalue()
    print(report_text, end="")

    # Save to ~/Pulpit/NEWS/YYYY-MM-DD.AM|PM.md
    report_path = get_report_path()
    save_report(report_text, articles, report_path)
    print(f"  [CIEL] Raport zapisany → {report_path}")


if __name__ == "__main__":
    main()
