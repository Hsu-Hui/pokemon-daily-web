"""巴哈姆特 Pokémon GO 哈啦板：從【情報】文章抓任務、獎勵和期間。"""
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .. import config
from .dates import at, mkdate
from .http import _get
from .models import TaskGroup, task_id


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
# 有寫年份的期間，例如「台灣時間2026年11月9日10:00～2026年11月13日20:00」
_FULL_RANGE_RE = re.compile(
    r"(20\d{2})\s*[年/]\s*(\d{1,2})\s*[月/]\s*(\d{1,2})\s*日?\s*(?:[^\d~～至到\n]{0,6}?(\d{1,2}[:：]\d{2}))?\s*"
    r"[~～至到\-–]\s*"
    r"(?:(20\d{2})\s*[年/]\s*)?(?:(\d{1,2})\s*[月/]\s*(\d{1,2})\s*日?)?\s*(?:[^\d\n]{0,6}?(\d{1,2}[:：]\d{2}))?"
)


def _parse_full_period(m: re.Match) -> tuple[datetime | None, datetime | None]:
    start = at(int(m[1]), int(m[2]), int(m[3]), m[4], "00:00")
    if m[6]:
        end = at(int(m[5] or m[1]), int(m[6]), int(m[7]), m[8], "23:59")
    else:
        end = at(int(m[1]), int(m[2]), int(m[3]), m[8], "23:59")
    if start and end and end < start and not m[5]:
        end = end.replace(year=end.year + 1)  # 「2026年12月30日～1月3日」
    return start, end


def parse_period(text: str, posted: datetime) -> tuple[datetime | None, datetime | None]:
    if m := _FULL_RANGE_RE.search(text):
        return _parse_full_period(m)
    m = _RANGE_RE.search(text)
    if not m:
        return None, None
    start = mkdate(posted.year, int(m[1]), int(m[2]), m[3], "00:00", posted)
    if m[4]:
        end = mkdate(posted.year, int(m[4]), int(m[5]), m[6], "23:59", posted)
    elif start:
        end = mkdate(start.year, start.month, start.day, m[6], "23:59", posted)
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
        if line.endswith(("。", "！", "!")):
            continue  # 完整句子是活動說明，不是任務
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
    title = _clean_post_title(title_el.get_text(strip=True))
    return TaskGroup(f"bh-{sn}", title, url, start, end, [(task_id(t), t, r) for t, r in tasks])


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
