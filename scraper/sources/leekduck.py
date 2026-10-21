"""LeekDuck 活動頁上的限時調查／特別調查（任務和獎勵）。"""
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .. import config
from .http import _get
from .models import GoEvent


def parse_event_research(html: str) -> list[tuple[str, str, list[str]]]:
    """回傳 (步驟名稱, 英文任務, [英文獎勵…])。頁面沒有限時調查時回傳空清單。"""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for step in soup.select(".special-research-list .step-item"):
        name_el = step.select_one(".step-name")
        name = name_el.get_text(" ", strip=True) if name_el else ""
        for row in step.select(".task-reward"):
            text_el = row.select_one(".task-text")
            text = text_el.get_text(" ", strip=True) if text_el else ""
            if text:
                out.append((name, text, [r.get_text(" ", strip=True) for r in row.select(".reward-label")]))
    return out


def active_events(events: list[GoEvent], now: datetime) -> list[GoEvent]:
    """進行中、會讀活動頁的活動。"""
    return [
        e for e in events
        if e.url and e.type not in config.GO_SKIP_TYPES
        and (not e.start or e.start <= now) and e.end and e.end > now
    ][: config.LEEKDUCK_MAX_PAGES]


def fetch_event_research(events: list[GoEvent], now: datetime) -> list[tuple[GoEvent, list[tuple[str, str, list[str]]]]]:
    """讀進行中活動的 LeekDuck 頁面；單頁失敗只略過那一頁。"""
    out = []
    for ev in active_events(events, now):
        try:
            steps = parse_event_research(_get(ev.url).text)
        except requests.RequestException as err:
            print(f"LeekDuck：讀取 {ev.name} 失敗：{err}")
            continue
        if steps:
            out.append((ev, steps))
    print(f"LeekDuck：{len(out)} 個活動有限時調查")
    return out
