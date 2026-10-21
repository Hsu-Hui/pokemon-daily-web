"""各資料來源的抓取。每個函式失敗時丟出例外，由 main 記錄並在網頁上註明。"""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import config


@dataclass
class GoEvent:
    id: str
    name: str
    heading: str
    type: str
    url: str
    start: datetime | None
    end: datetime | None
    field_research: bool = False  # 活動期間有專屬田野調查


@dataclass
class Research:
    text: str          # 英文任務
    rewards: list[str]  # 獎勵（寶可夢英文名或道具）


@dataclass
class Product:
    id: str
    source: str
    name: str
    url: str
    price: str = ""
    image: str = ""


@dataclass
class News:
    id: str
    title: str
    url: str
    source: str
    published: datetime | None
    others: list[str] = field(default_factory=list)  # 被合併的其他媒體
    category: str = ""  # 官網的分類（活動、商品…）


@dataclass
class TaskGroup:
    id: str
    name: str
    url: str
    start: datetime | None
    end: datetime | None
    tasks: list[tuple[str, str]]  # (任務, 獎勵)


def _get(url: str, **kwargs) -> requests.Response:
    headers = {"User-Agent": config.USER_AGENT, **kwargs.pop("headers", {})}
    resp = requests.get(url, headers=headers, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp


def parse_time(value: str | None) -> datetime | None:
    """ScrapedDuck 的時間多半是當地時間（沒有時區），視為台灣時間。"""
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=config.TZ)
    return dt.astimezone(config.TZ)


# ---------- Pokémon GO 活動 ----------

def fetch_go_events() -> list[GoEvent]:
    return [
        GoEvent(
            id=e["eventID"],
            name=e["name"],
            heading=e.get("heading") or e.get("eventType", ""),
            type=e.get("eventType", ""),
            url=e.get("link", ""),
            start=parse_time(e.get("start")),
            end=parse_time(e.get("end")),
            field_research=bool(((e.get("extraData") or {}).get("generic") or {}).get("hasFieldResearchTasks")),
        )
        for e in _get(config.GO_EVENTS_URL).json()
    ]


def fetch_field_research() -> list[Research]:
    out = []
    for r in _get(config.GO_RESEARCH_URL).json():
        text = re.sub(r"<[^>]+>", "", r.get("text", "")).strip()
        rewards = [x.get("name", "") for x in r.get("rewards") or [] if x.get("name")]
        if text:
            out.append(Research(text, rewards))
    return out


# ---------- PChome ----------

def fetch_pchome() -> list[Product]:
    items, seen = [], set()
    for query in config.PCHOME_QUERIES:
        page, total = 1, 1
        while page <= min(total, config.PCHOME_PAGES):
            data = _get(
                config.PCHOME_SEARCH_URL,
                params={"q": query, "page": page, "sort": "new/dc"},
                headers={"Referer": "https://24h.pchome.com.tw/"},
            ).json()
            total = int(data.get("totalPage") or 1)
            for p in data.get("prods") or []:
                name, pid = p.get("name", ""), p.get("Id", "")
                if not pid or pid in seen:
                    continue
                if not any(k.lower() in name.lower() for k in config.PCHOME_NAME_KEYWORDS):
                    continue
                seen.add(pid)
                price = p.get("price")
                pic = p.get("picB") or p.get("picS") or ""
                items.append(Product(
                    id=f"pchome:{pid}",
                    source="PChome",
                    name=name,
                    url=f"https://24h.pchome.com.tw/prod/{pid}",
                    price=f"${price:,}" if isinstance(price, int) else "",
                    image=urljoin(config.PCHOME_IMAGE_HOST + "/", pic.lstrip("/")) if pic else "",
                ))
            page += 1
    return items


# ---------- Google 新聞 ----------

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


def dedupe_news(items: list[News], known_titles: list[str] = ()) -> list[News]:
    """同一件事被不同媒體報導時只留第一則，其他媒體記在 others。
    known_titles 是之前已經存過的標題，跟它們太像的也拿掉。"""
    kept: list[News] = []
    for item in items:
        if any(similarity(item.title, t) >= config.NEWS_SIMILARITY for t in known_titles):
            continue
        for k in kept:
            if similarity(item.title, k.title) >= config.NEWS_SIMILARITY:
                if item.source not in k.others and item.source != k.source:
                    k.others.append(item.source)
                break
        else:
            kept.append(item)
    return kept


# ---------- 寶可夢台灣官網 ----------

_DATE_RE = re.compile(r"(20\d{2})[./\-年](\d{1,2})[./\-月](\d{1,2})")
_DATE_MDY_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(20\d{2})")


def _parse_date(text: str) -> datetime | None:
    if m := _DATE_RE.search(text):
        y, mo, d = int(m[1]), int(m[2]), int(m[3])
    elif m := _DATE_MDY_RE.search(text):
        mo, d, y = int(m[1]), int(m[2]), int(m[3])
    else:
        return None
    try:
        return datetime(y, mo, d, tzinfo=config.TZ)
    except ValueError:
        return None


def parse_official_news(html: str, base_url: str) -> list[News]:
    """官網列表每筆是一個 <a>，裡面有標題（可能出現兩次）、分類（活動、商品…）和日期。"""
    soup = BeautifulSoup(html, "html.parser")
    items, seen = [], set()
    for a in soup.find_all("a", href=True):
        url = urljoin(base_url, a["href"])
        if not re.search(r"/topics/[\w\-]+", url) or url.rstrip("/") == base_url.rstrip("/") or url in seen:
            continue
        raw = [" ".join(t.split()) for t in a.stripped_strings]
        published = _parse_date(" ".join(raw))
        parts = [_DATE_MDY_RE.sub("", _DATE_RE.sub("", p)).strip(" ・|｜-") for p in raw]
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


# ---------- 巴哈姆特任務 ----------

_TASK_VERBS = re.compile(
    r"捕捉|抓到|轉動|孵化|使用|完成|獲勝|投擲|進化|交換|贈送|拍攝|走路|步行|行走|打敗|擊敗|強化|"
    r"探索|參加|餵|散步|收集|造訪|拜訪|對戰|挑戰|投出|丟出|遇見|發送|開啟|戰勝"
)
_REWARD_SEP = re.compile(r"\s*(?:→|->|➔|➜|⇒|⮕|=>|｜\s*獎勵[:：]?|\|\s*獎勵[:：]?|獎勵[:：])\s*")
_BULLET = re.compile(r"^[\s・•●○◆◇▪▫■□★☆\-–—*＊·\d.、()（）]+")
_RANGE_RE = re.compile(
    r"(\d{1,2})\s*[/月]\s*(\d{1,2})\s*日?[^\d~～至到\n]{0,12}?(\d{1,2}[:：]\d{2})?\s*"
    r"[~～至到\-–]\s*"
    r"(?:(\d{1,2})\s*[/月]\s*(\d{1,2})\s*日?)?(?:[^\d\n]{0,12}?(\d{1,2}[:：]\d{2}))?"
)


def _mkdate(year: int, month: int, day: int, hm: str | None, default: str, ref: datetime) -> datetime | None:
    h, m = map(int, (hm or default).replace("：", ":").split(":"))
    try:
        dt = datetime(year, month, day, min(h, 23), m, tzinfo=config.TZ)
    except ValueError:
        return None
    if dt < ref - timedelta(days=180):  # 跨年：12 月發文寫「1/5」
        dt = dt.replace(year=year + 1)
    return dt


def parse_period(text: str, posted: datetime) -> tuple[datetime | None, datetime | None]:
    m = _RANGE_RE.search(text)
    if not m:
        return None, None
    start = _mkdate(posted.year, int(m[1]), int(m[2]), m[3], "00:00", posted)
    if m[4]:
        end = _mkdate(posted.year, int(m[4]), int(m[5]), m[6], "23:59", posted)
    elif start:
        end = _mkdate(start.year, start.month, start.day, m[6], "23:59", posted)
    else:
        end = None
    if start and end and end < start:
        end = end.replace(year=end.year + 1)
    return start, end


def parse_tasks(text: str) -> list[tuple[str, str]]:
    tasks = []
    for raw in text.splitlines():
        line = _BULLET.sub("", raw).strip()
        if not line or len(line) > 80 or not _TASK_VERBS.search(line):
            continue
        parts = _REWARD_SEP.split(line, maxsplit=1)
        task = parts[0].strip(" ：:")
        reward = parts[1].strip() if len(parts) > 1 else ""
        if not _TASK_VERBS.search(task) or len(task) < 3:
            continue
        if not reward and not re.search(r"\d", task):
            continue  # 沒有獎勵也沒有數量，多半是說明文字
        tasks.append((task, reward))
    return tasks[:40]


def _clean_post_title(title: str) -> str:
    return re.sub(r"^【[^】]*】\s*", "", title).strip()


def parse_bahamut_post(html: str, url: str, sn: str, now: datetime) -> TaskGroup | None:
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one(".c-post__header__title") or soup.find("h1")
    body = soup.select_one(".c-article__content")
    if not title_el or not body:
        return None
    for br in body.find_all("br"):
        br.replace_with("\n")
    for block in body.find_all(["div", "p", "li"]):
        block.insert_after("\n")
    text = body.get_text()
    posted = now
    when = soup.select_one(".edittime[data-mtime]")
    if when:
        try:
            posted = datetime.fromisoformat(when["data-mtime"]).replace(tzinfo=config.TZ)
        except ValueError:
            pass
    tasks = parse_tasks(text)
    if not tasks:
        return None
    start, end = parse_period(text, posted)
    if not end:
        return None  # 置頂的資料整理串之類沒有活動時間，不是任務文
    return TaskGroup(f"bh-{sn}", _clean_post_title(title_el.get_text(strip=True)), url, start, end, tasks)


def parse_bahamut_list(html: str) -> list[tuple[str, str, str]]:
    """回傳 (snA, 標題, 網址)。"""
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        m = re.search(r"C\.php\?.*?snA=(\d+)", a["href"])
        title = a.get_text(" ", strip=True)
        if not m or m[1] in seen or not title:
            continue
        if "情報" not in title[:6] or not any(k in title for k in config.BAHAMUT_TITLE_KEYWORDS):
            continue
        seen.add(m[1])
        out.append((m[1], title, f"{config.BAHAMUT_POST_URL}?bsn={config.BAHAMUT_BSN}&snA={m[1]}"))
    return out


def fetch_bahamut_tasks(now: datetime) -> list[TaskGroup]:
    headers = {"Referer": "https://forum.gamer.com.tw/", "Accept-Language": "zh-TW,zh;q=0.9"}
    posts = []
    for page in range(1, config.BAHAMUT_PAGES + 1):
        resp = _get(config.BAHAMUT_BOARD_URL, params={"bsn": config.BAHAMUT_BSN, "page": page}, headers=headers)
        posts += [p for p in parse_bahamut_list(resp.text) if p[0] not in {x[0] for x in posts}]
    print(f"巴哈：列表找到 {len(posts)} 篇任務相關文章")
    groups = []
    for sn, title, url in posts[: config.BAHAMUT_MAX_POSTS]:
        try:
            group = parse_bahamut_post(_get(url, headers=headers).text, url, sn, now)
        except requests.RequestException as err:
            print(f"巴哈：讀取 {title} 失敗：{err}")
            continue
        if not group:
            print(f"巴哈：{title} 沒有解析到任務")
            continue
        if group.end and group.end < now:
            continue
        groups.append(group)
    return groups
