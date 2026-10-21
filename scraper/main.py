"""每天執行：抓資料、整理成 JSON，送到 Apps Script 存進 Google 試算表。"""
import json
import os
import re
import sys
import traceback
from dataclasses import asdict, replace
from datetime import datetime, timedelta
from pathlib import Path

import requests

from . import config, sources, translate

OUT_PATH = Path("out/payload.json")

ERROR_REASONS = {401: "需要登入", 403: "被拒絕存取", 404: "找不到頁面", 429: "請求次數過多被限制"}


def describe_error(err: Exception) -> str:
    response = getattr(err, "response", None)
    if response is not None:
        return ERROR_REASONS.get(response.status_code, f"HTTP {response.status_code}")
    if isinstance(err, requests.Timeout):
        return "連線逾時"
    if isinstance(err, requests.ConnectionError):
        return "連不上"
    return "資料格式不符"


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def build_events(events: list[sources.GoEvent], now: datetime) -> list[dict]:
    horizon = now + timedelta(days=config.GO_LOOKAHEAD_DAYS)
    out = []
    for ev in events:
        if ev.type in config.GO_SKIP_TYPES:
            continue
        if (ev.end and ev.end < now) or (ev.start and ev.start > horizon):
            continue
        out.append({
            "id": ev.id,
            "name": translate.event_name(ev.name),
            "type": translate.event_type(ev.type, ev.heading),
            "category": translate.event_category(ev.type, ev.name),
            "url": ev.url,
            "start": iso(ev.start),
            "end": iso(ev.end),
        })
    return out


def build_tasks(groups: list[sources.TaskGroup]) -> list[dict]:
    return [{
        "id": g.id,
        "name": g.name,
        "url": g.url,
        "start": iso(g.start),
        "end": iso(g.end),
        "tasks": [{"id": i, "text": t, "reward": r} for i, t, r in g.tasks],
    } for g in groups]


def build_field_research(research: list[sources.Research], events: list[sources.GoEvent], now: datetime) -> list[dict]:
    """目前的田野調查任務整理成一組。田野調查沒有固定期限：有活動專屬任務時，
    以那個活動的結束時間當期限；否則以月底當期限（每月 1 日會換一批）。"""
    if not research:
        return []
    active = [e for e in events if e.field_research and e.end and e.end > now and (not e.start or e.start <= now)]
    if active:
        ev = min(active, key=lambda e: e.end)
        start, end, name = ev.start, ev.end, f"田野調查：{translate.event_name(ev.name)}"
        gid = f"field-{ev.id}"
    else:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        nxt = (start + timedelta(days=32)).replace(day=1)
        end, name, gid = nxt - timedelta(minutes=1), f"{now.month} 月田野調查", f"field-{now:%Y%m}"
    tasks = []
    for r in research:
        rewards = "、".join(translate.pokemon(x) for x in r.rewards[:6])
        tasks.append({
            "id": re.sub(r"[^a-z0-9]+", "-", r.text.lower()).strip("-"),
            "text": translate.research_task(r.text),
            "reward": f"遇見 {rewards}" if rewards else "",
        })
    return [{
        "id": gid, "name": name, "url": "https://leekduck.com/research/",
        "start": iso(start), "end": iso(end), "tasks": tasks,
    }]


def _step_task_ids(steps: list[tuple[str, str, list[str]]]) -> list[str]:
    """同一步驟裡重複的任務（例如四個「Use a Star Piece」）加上第幾次出現，id 才不會撞在一起。"""
    seen: dict[tuple[str, str], int] = {}
    ids = []
    for step, text, _ in steps:
        n = seen[step, text] = seen.get((step, text), 0) + 1
        ids.append(sources.task_id(step, text, str(n)))
    return ids


def build_event_research(found: list[tuple[sources.GoEvent, list[tuple[str, str, list[str]]]]]) -> list[dict]:
    """LeekDuck 活動頁的限時調查：每個活動一組，期間跟著活動。"""
    return [{
        "id": f"ld-{ev.id}",
        "name": f"限時調查：{translate.event_name(ev.name)}",
        "url": ev.url,
        "start": iso(ev.start),
        "end": iso(ev.end),
        "tasks": [{
            "id": tid,
            "text": translate.research_task(text),
            "reward": "、".join(translate.reward(r) for r in rewards),
        } for tid, (step, text, rewards) in zip(_step_task_ids(steps[:40]), steps[:40])],
    } for ev, steps in found]


def news_kind(item: sources.News, default: str) -> str:
    if item.source == "寶可夢官網":
        text = item.category + item.title
        return "product" if any(w in text for w in config.PRODUCT_WORDS) else "event"
    return default


def build_news(groups: list[tuple[str, list[sources.News]]]) -> list[dict]:
    """groups：(預設分類, 新聞)。全部一起去重，同一件事不同媒體只留一則。"""
    tagged = [replace(n, kind=news_kind(n, kind)) for kind, items in groups for n in items]
    return [{
        "id": n.id,
        "kind": n.kind,
        "title": n.title,
        "url": n.url,
        "source": n.source,
        "others": n.others,
        "published": iso(n.published),
    } for n in sources.dedupe_news(tagged)]


def news_to_product(n: dict) -> dict:
    """商品類的消息放到新商品頁：官網公告標成「官網」，其他是寶可夢中心的新聞。"""
    official = n["source"] == "寶可夢官網"
    return asdict(sources.Product(
        id=n["id"], source="官網" if official else "寶可夢中心", name=n["title"], url=n["url"],
        media="" if official else n["source"],
    ))


def collect(now: datetime) -> dict:
    errors: list[str] = []

    def safe(name: str, fn, *args, default=None):
        try:
            return fn(*args)
        except Exception as err:  # 單一來源失敗不影響其他來源
            traceback.print_exc()
            errors.append(f"{name}（{describe_error(err)}）")
            return default

    events = safe("Pokémon GO 活動", sources.fetch_go_events, default=[])
    tasks = safe("巴哈姆特任務", sources.fetch_bahamut_tasks, now, default=[])
    research = safe("田野調查", sources.fetch_field_research, default=[])
    event_research = safe("LeekDuck 限時調查", sources.fetch_event_research, events, now, default=[])
    products = safe("PChome", sources.fetch_pchome, default=[])
    official = safe("寶可夢官網", sources.fetch_official_news, now, default=[])
    pc_news = safe("寶可夢中心新聞", sources.fetch_google_news, config.NEWS_QUERIES["pc_taipei"], now, default=[])
    tw_news = safe("台灣活動新聞", sources.fetch_google_news, config.NEWS_QUERIES["tw_events"], now, default=[])

    # 官網放最前面，重複時保留官網的版本
    news = build_news([("event", official), ("product", pc_news), ("event", tw_news)])
    return {
        "generatedAt": now.isoformat(),
        "events": build_events(events, now),
        "taskGroups": build_tasks(tasks) + build_event_research(event_research) + build_field_research(research, events, now),
        "products": [asdict(p) for p in products] + [news_to_product(n) for n in news if n["kind"] == "product"],
        "news": [n for n in news if n["kind"] == "event"],
        "errors": errors,
    }


def send(payload: dict, url: str, secret: str) -> dict:
    resp = requests.post(url, json={"secret": secret, "data": payload}, timeout=120)
    resp.raise_for_status()
    result = resp.json()
    if not result.get("ok"):
        raise RuntimeError(f"Apps Script 回應錯誤：{result}")
    return result


def main() -> int:
    now = datetime.now(config.TZ)
    payload = collect(now)
    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"活動 {len(payload['events'])}、任務組 {len(payload['taskGroups'])}、"
        f"商品 {len(payload['products'])}、新聞 {len(payload['news'])}"
    )
    for g in payload["taskGroups"]:
        print(f"任務：{g['name']}（{g['start']} ~ {g['end']}）")
        for t in g["tasks"][:5]:
            print(f"  ・{t['text']} → {t['reward'] or '（無獎勵）'}")
    for p in payload["products"][:3]:
        print(f"商品：{p['name']}｜{p['price']}｜{p['image']}")
    for n in payload["news"][:10]:
        print(f"新聞[{n['kind']}]：{n['title']}｜{n['source']}｜另有 {len(n['others'])} 家")
    if payload["errors"]:
        print("失敗的來源：" + "、".join(payload["errors"]))

    url, secret = os.environ.get("GAS_INGEST_URL"), os.environ.get("GAS_INGEST_SECRET")
    if not url or not secret:
        print(f"沒有設定 GAS_INGEST_URL / GAS_INGEST_SECRET，只輸出 {OUT_PATH}")
        return 0
    print("Apps Script：", send(payload, url, secret))
    return 0


if __name__ == "__main__":
    sys.exit(main())
