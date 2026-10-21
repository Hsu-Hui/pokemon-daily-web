"""寶可夢台灣官網的最新消息。"""
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .. import config
from .dates import DATE_MDY_RE, DATE_RE, parse_date
from .http import _get
from .models import News


def parse_official_news(html: str, base_url: str) -> list[News]:
    """官網列表每筆是一個 <a>，裡面有標題（可能出現兩次）、分類（活動、商品…）和日期。"""
    soup = BeautifulSoup(html, "html.parser")
    items, seen = [], set()
    for a in soup.find_all("a", href=True):
        url = urljoin(base_url, a["href"])
        if not re.search(r"/topics/[\w\-]+", url) or url.rstrip("/") == base_url.rstrip("/") or url in seen:
            continue
        raw = [" ".join(t.split()) for t in a.stripped_strings]
        published = parse_date(" ".join(raw))
        parts = [DATE_MDY_RE.sub("", DATE_RE.sub("", p)).strip(" ・|｜-") for p in raw]
        candidates = [p for p in parts if len(p) > 4]
        if not candidates:
            continue
        title = max(candidates, key=len)
        category = next((p for p in parts if 1 < len(p) <= 4), "")
        # 分類和標題擠在同一段文字時，分類在最後面
        if not category and (m := re.match(r"^(.{5,}?)\s+(活動|商品|新聞|遊戲|卡牌|動畫|電影|公告|其他)$", title)):
            title, category = m[1], m[2]
        # 標題和摘要相同時會變成「A A」，只留一份
        half = len(title) // 2
        if len(title) % 2 == 1 and title[:half] == title[half + 1:]:
            title = title[:half]
        seen.add(url)
        items.append(News(id=url, title=title, url=url, source="寶可夢官網", published=published, category=category))
    return items


def fetch_official_news(now: datetime) -> list[News]:
    resp = _get(config.OFFICIAL_NEWS_URL)
    resp.encoding = resp.apparent_encoding or "utf-8"
    oldest = now - timedelta(days=config.OFFICIAL_MAX_AGE_DAYS)
    return [n for n in parse_official_news(resp.text, config.OFFICIAL_NEWS_URL)
            if not n.published or n.published >= oldest.replace(hour=0, minute=0)]
