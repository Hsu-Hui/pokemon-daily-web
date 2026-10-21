"""PChome 24h 搜尋 API。"""
from urllib.parse import urljoin

from .. import config
from .http import _get
from .models import Product


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
