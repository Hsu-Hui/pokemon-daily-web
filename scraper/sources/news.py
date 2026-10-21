"""Google 新聞 RSS 和跨來源的新聞去重。"""
import re
import xml.etree.ElementTree as ET
from dataclasses import replace
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from .. import config
from .http import _get
from .models import News


def _clean_title(title: str, source: str) -> str:
    """Google 新聞標題後面會接「 - 媒體名稱」，拿掉；也拿掉「討論牆 |」這類前綴和「- 遊戲新聞」分類尾巴。"""
    if source and title.endswith(" - " + source):
        title = title[: -len(source) - 3].strip()
    else:
        title = re.sub(r"\s+-\s+[^-]+$", "", title).strip()
    title = re.sub(r"^討論牆\s*[|｜]\s*", "", title)
    return re.sub(r"\s*[-－]\s*\S{2,6}新聞$", "", title).strip()


def fetch_google_news(query: str, now: datetime) -> list[News]:
    resp = _get(
        config.GOOGLE_NEWS_RSS,
        params={"q": query, "hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
    )
    root = ET.fromstring(resp.content)
    oldest = now - timedelta(hours=config.NEWS_MAX_AGE_HOURS)
    items = []
    for node in root.iter("item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        source = (node.findtext("source") or "").strip()
        pub = node.findtext("pubDate")
        published = parsedate_to_datetime(pub).astimezone(config.TZ) if pub else None
        if not title or not link or (published and published < oldest):
            continue
        if not any(w in title.lower() for w in config.NEWS_TITLE_KEYWORDS):
            continue
        items.append(News(
            id=(node.findtext("guid") or link).strip(),
            title=_clean_title(title, source),
            url=link,
            source=source or "Google 新聞",
            published=published,
        ))
    return items


def _bigrams(text: str) -> set[str]:
    text = re.sub(r"[\s\W_]+", "", text.lower())
    return {text[i:i + 2] for i in range(len(text) - 1)} or {text}


def similarity(a: str, b: str) -> float:
    x, y = _bigrams(a), _bigrams(b)
    return len(x & y) / min(len(x), len(y))


def dedupe_news(items: list[News]) -> list[News]:
    """同一件事被不同媒體報導時只留第一則，其他媒體記在 others。回傳新的物件，不改輸入。"""
    kept: list[News] = []
    for item in items:
        for k in kept:
            if similarity(item.title, k.title) >= config.NEWS_SIMILARITY:
                if item.source not in k.others and item.source != k.source:
                    k.others.append(item.source)
                break
        else:
            kept.append(replace(item, others=list(item.others)))
    return kept
