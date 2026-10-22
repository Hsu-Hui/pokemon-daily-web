"""PChome 24h 搜尋 API。"""
from urllib.parse import urljoin

from .. import config
from .http import _get
from .models import Product


def product_key(name: str, price: str) -> str:
    """同一件商品在 PChome 可能有好幾個商品編號：名稱（空白整理、不分大小寫）＋價格相同就當成同一件。"""
    return " ".join(name.split()).lower() + "|" + price


def fetch_pchome() -> list[Product]:
    items, seen, keys = [], set(), set()
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
                price = f"${price:,}" if isinstance(price, int) else ""
                key = product_key(name, price)
                if key in keys:
                    continue
                keys.add(key)
                pic = p.get("picB") or p.get("picS") or ""
                items.append(Product(
                    id=f"pchome:{pid}",
                    source="PChome",
                    name=name,
                    url=f"https://24h.pchome.com.tw/prod/{pid}",
                    price=price,
                    image=urljoin(config.PCHOME_IMAGE_HOST + "/", pic.lstrip("/")) if pic else "",
                ))
            page += 1
    return items
