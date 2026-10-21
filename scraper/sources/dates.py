"""日期解析：ScrapedDuck 時間、官網日期、巴哈文章裡的月/日。全部視為台灣時間。"""
import re
from datetime import datetime, timedelta

from .. import config


def parse_time(value: str | None) -> datetime | None:
    """ScrapedDuck 的時間多半是當地時間（沒有時區），視為台灣時間。"""
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=config.TZ)
    return dt.astimezone(config.TZ)


DATE_RE = re.compile(r"(20\d{2})[./\-年](\d{1,2})[./\-月](\d{1,2})")
DATE_MDY_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(20\d{2})")


def parse_date(text: str) -> datetime | None:
    if m := DATE_RE.search(text):
        y, mo, d = int(m[1]), int(m[2]), int(m[3])
    elif m := DATE_MDY_RE.search(text):
        mo, d, y = int(m[1]), int(m[2]), int(m[3])
    else:
        return None
    try:
        return datetime(y, mo, d, tzinfo=config.TZ)
    except ValueError:
        return None


def mkdate(year: int, month: int, day: int, hm: str | None, default: str, ref: datetime) -> datetime | None:
    h, m = map(int, (hm or default).replace("：", ":").split(":"))
    try:
        dt = datetime(year, month, day, min(h, 23), m, tzinfo=config.TZ)
    except ValueError:
        return None
    if dt < ref - timedelta(days=180):  # 跨年：12 月發文寫「1/5」
        dt = dt.replace(year=year + 1)
    return dt


