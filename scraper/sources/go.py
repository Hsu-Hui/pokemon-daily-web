"""Pokémon GO 活動和田野調查（LeekDuck 資料，ScrapedDuck 整理成 JSON）。"""
import re

from .. import config
from .dates import parse_time
from .http import _get
from .models import GoEvent, Research


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
