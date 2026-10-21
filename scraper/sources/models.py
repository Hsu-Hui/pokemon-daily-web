"""各來源共用的資料結構。"""
from dataclasses import dataclass, field
from datetime import datetime


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
    media: str = ""  # 從新聞來的商品消息：報導的媒體


@dataclass
class News:
    id: str
    title: str
    url: str
    source: str
    published: datetime | None
    others: list[str] = field(default_factory=list)  # 被合併的其他媒體
    category: str = ""  # 官網的分類（活動、商品…）
    kind: str = "event"  # 看板分類：event（台灣活動）或 product（新商品）


@dataclass
class TaskGroup:
    id: str
    name: str
    url: str
    start: datetime | None
    end: datetime | None
    tasks: list[tuple[str, str]]  # (任務, 獎勵)
