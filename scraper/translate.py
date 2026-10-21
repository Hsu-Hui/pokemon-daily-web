"""把 LeekDuck 的英文活動名稱翻成中文（字典對照，不用 AI）。對不到的專有名詞保留原文。"""
import json
import re
from pathlib import Path

from . import config

# 寶可夢英文名 → 繁中名，來源 PokeAPI pokemon_species_names.csv
_NAMES: dict[str, str] = json.loads(
    (Path(__file__).parent / "data" / "pokemon_names.json").read_text(encoding="utf-8")
)
_NAME_RE = re.compile(
    r"(?<![A-Za-z])(" + "|".join(re.escape(n) for n in sorted(_NAMES, key=len, reverse=True)) + r")(?![A-Za-z])"
)

TYPE_LABELS = {
    "event": "活動",
    "community-day": "社群日",
    "raid-battles": "團體戰",
    "raid-hour": "團體戰時間",
    "raid-day": "團體戰日",
    "pokemon-spotlight-hour": "聚焦時刻",
    "max-mondays": "極巨星期一",
    "max-battles": "極巨對戰",
    "research": "調查",
    "go-pass": "GO Pass",
    "pokemon-go-tour": "Pokémon GO Tour",
    "wild-area": "野外區域",
    "city-safari": "城市狩獵",
    "twitch-drops": "Twitch 掉寶",
    "go-battle-league": "GO 對戰聯盟",
    "season": "季節",
}

# 月份、流星雨、地名等固定對照（依序取代）
_LOOKUPS = json.loads((Path(__file__).parent / "data" / "translations.json").read_text(encoding="utf-8"))
MONTHS, METEORS, PLACES = _LOOKUPS["months"], _LOOKUPS["meteors"], _LOOKUPS["places"]

# 依序套用；先處理整句結構，再處理零散字詞
PATTERNS = [
    (r"^(.+) in 5-star Raid Battles$", r"五星團體戰：\1"),
    (r"^(.+) in Mega Raids$", r"團體戰：\1"),
    (r"^(.+) in Shadow Raids$", r"團體戰：\1"),
    (r"^(.+) Super Mega Raid Day$", r"超級團體戰日：\1"),
    (r"^Super Mega Raid Day$", "超級團體戰日"),
    (r"^(.+) Raid Day$", r"團體戰日：\1"),
    (r"^(.+) Raid Hour$", r"團體戰時間：\1"),
    (r"^(.+) Spotlight Hour$", r"聚焦時刻：\1"),
    (r"^Dynamax (.+) during Max Monday$", r"極巨星期一：極巨化\1"),
    (r"^Max Monday: Pokémon to be announced$", "極巨星期一：寶可夢待公布"),
    (r"^Dynamax (.+) Max Battle Day$", r"極巨對戰日：極巨化\1"),
    (r"^(.+) Max Battle Day$", r"極巨對戰日：\1"),
    (r"^(\w+) Community Day$", r"\1社群日"),
    (r"^(.+) Community Day Classic$", r"\1社群日經典"),
    (r"^小隕星 Showers: (.+?) (\d{4})$", r"小隕星流星雨：\1 \2"),
    (r"^Twitch Drops for (.+)$", r"Twitch 掉寶：\1"),
    (r"(.+) Timed Research$", r"\1限時調查"),
    (r" Part II$", " 第二部"),
    (r" Part I$", " 第一部"),
    (r"\(Rescheduled\)", "（改期）"),
    (r"\bHalloween\b", "萬聖節"),
    (r"\bwearing a witch hat\b", "（戴巫師帽）"),
    (r"\(Normal, Defense, Attack, and Speed Formes\)", "（普通、防禦、攻擊、速度形態）"),
    (r"\(Incarnate Forme\)", "（化身形態）"),
    (r"\(Therian Forme\)", "（靈獸形態）"),
    (r"\(Origin Forme\)", "（起源形態）"),
    (r"\(Altered Forme\)", "（別種形態）"),
    # 只有後面接的是寶可夢中文名才翻（避免 Mega Edition、Dynamax Trails 被翻壞）
    (r"\bMega (?=[\u4e00-\u9fff])", "超級"),
    (r"\bShadow (?=[\u4e00-\u9fff])", "暗影"),
    (r"\bDynamax (?=[\u4e00-\u9fff])", "極巨化"),
    (r"\bGigantamax (?=[\u4e00-\u9fff])", "超極巨化"),
    (r" +（", "（"),
    (r",? and ", "、"),
    (r", ", "、"),
]
_PATTERNS = [(re.compile(p), r) for p, r in PATTERNS]


def event_name(name: str) -> str:
    text = _NAME_RE.sub(lambda m: _NAMES[m.group(1)], name)
    for word, zh in MONTHS.items():
        text = re.sub(rf"\b{word}\b", zh, text)
    for word, zh in METEORS.items():
        text = text.replace(word, zh)
    for pattern, repl in _PATTERNS:
        text = pattern.sub(repl, text)
    for word, zh in PLACES.items():
        text = text.replace(word, zh)
    # 中文字和 X / Y 之間的空白拿掉，例如「超級噴火龍 X」→「超級噴火龍X」
    return re.sub(r"(?<=[一-鿿]) (?=[XY](?:$|、))", "", text)


def event_type(type_slug: str, heading: str) -> str:
    return TYPE_LABELS.get(type_slug, heading)


# 活動分類：看板上的分頁只分這幾類
CATEGORIES = [c["name"] for c in config.BOARD["categories"]]
_CATEGORY_OF = {
    "pokemon-spotlight-hour": "聚焦時刻",
    "max-battles": "極巨化/超極巨化",
    "max-mondays": "極巨化/超極巨化",
    "raid-battles": "團體戰/超級團體戰",
    "raid-hour": "團體戰/超級團體戰",
    "raid-day": "團體戰/超級團體戰",
    "raid-weekend": "團體戰/超級團體戰",
    "elite-raids": "團體戰/超級團體戰",
    "super-mega-raid": "團體戰/超級團體戰",
    "go-pass": "GO Pass",
    "research": "限時調查",
    "timed-research": "限時調查",
    "special-research": "限時調查",
    "limited-research": "限時調查",
    "research-breakthrough": "限時調查",
}


def event_category(type_slug: str, name: str = "") -> str:
    if type_slug in _CATEGORY_OF:
        return _CATEGORY_OF[type_slug]
    if re.search(r"Timed Research|Special Research|Limited Research", name):
        return "限時調查"
    if re.search(r"Dynamax|Gigantamax|Max Battle|Max Monday", name):
        return "極巨化/超極巨化"
    if re.search(r"Raid", name):
        return "團體戰/超級團體戰"
    return "其他"


# ---------- 田野調查任務 ----------

_FORMS = {"Alolan": "阿羅拉", "Galarian": "伽勒爾", "Hisuian": "洗翠", "Paldean": "帕底亞", "Shadow": "暗影", "Mega": "超級"}
_TYPES = {
    "Normal": "一般", "Fire": "火", "Water": "水", "Grass": "草", "Electric": "電", "Ice": "冰",
    "Fighting": "格鬥", "Poison": "毒", "Ground": "地面", "Flying": "飛行", "Psychic": "超能力",
    "Bug": "蟲", "Rock": "岩石", "Ghost": "幽靈", "Dragon": "龍", "Dark": "惡", "Steel": "鋼", "Fairy": "妖精",
}
_THROWS = {"Nice": "不錯", "Great": "很棒", "Excellent": "非常棒", "Curveball": "曲球"}


def pokemon(name: str) -> str:
    """獎勵寶可夢名稱，例如「Alolan Geodude」→「阿羅拉小拳石」、「Spinda 4」→「晃晃斑 4」。"""
    form = ""
    first, _, rest = name.partition(" ")
    if first in _FORMS and rest:
        form, name = _FORMS[first], rest
    base, _, suffix = name.partition(" ")
    zh = _NAMES.get(base)
    if zh is None:
        return form + event_name(name)
    return form + zh + (" " + suffix if suffix else "")


def _num(m: str | None) -> str:
    return m if m and m.isdigit() else "1"


def _throw(words: str) -> str:
    parts = words.split()
    return "".join(_THROWS.get(w, w) for w in parts if w != "Throws" and w != "Throw")


_TYPE_ALT = "|".join(_TYPES)
_RESEARCH = [
    (rf"^Catch (\d+|an?) ({_TYPE_ALT})-type Pokémon$", lambda m: f"捕捉 {_num(m[1])} 隻{_TYPES[m[2]]}屬性寶可夢"),
    (rf"^Catch (\d+|an?) ({_TYPE_ALT}) or ({_TYPE_ALT})-type Pokémon$",
     lambda m: f"捕捉 {_num(m[1])} 隻{_TYPES[m[2]]}或{_TYPES[m[3]]}屬性寶可夢"),
    (r"^Catch (\d+) different species of Pokémon$", lambda m: f"捕捉 {m[1]} 種不同的寶可夢"),
    (r"^Catch (\d+|an?) Pokémon with Weather Boost$", lambda m: f"捕捉 {_num(m[1])} 隻受天氣加成的寶可夢"),
    (r"^Catch (\d+|an?) Pokémon$", lambda m: f"捕捉 {_num(m[1])} 隻寶可夢"),
    (r"^Catch (\d+|an?) (.+)$", lambda m: f"捕捉 {_num(m[1])} 隻{pokemon(m[2])}"),
    (r"^Make (\d+|an?) ((?:Nice|Great|Excellent|Curveball| )+)Throws? in a row$", lambda m: f"連續投出 {_num(m[1])} 次「{_throw(m[2])}」"),
    (r"^Make (\d+|an?) ((?:Nice|Great|Excellent|Curveball| )+)Throws?$", lambda m: f"投出 {_num(m[1])} 次「{_throw(m[2])}」"),
    (r"^Win a three-star raid or higher$", lambda m: "在三星以上的團體戰中獲勝"),
    (r"^Win (\d+|an?) raids?$", lambda m: f"在團體戰中獲勝 {_num(m[1])} 次"),
    (r"^Win (\d+|an?) Max Battles?$", lambda m: f"在極巨對戰中獲勝 {_num(m[1])} 次"),
    (r"^Explore (\d+) km$", lambda m: f"探索 {m[1]} 公里"),
    (r"^Hatch (\d+|an?) Eggs?$", lambda m: f"孵化 {_num(m[1])} 顆蛋"),
    (r"^Spin (\d+|an?) PokéStops? or Gyms?$", lambda m: f"轉動 {_num(m[1])} 個補給站或道館"),
    (r"^Spin (\d+|an?) PokéStops?$", lambda m: f"轉動 {_num(m[1])} 個補給站"),
    (r"^Take a snapshot of a wild Pokémon$", lambda m: "拍下野生寶可夢的照片"),
    (r"^Take (\d+) snapshots? of (.+)$", lambda m: f"拍下 {m[1]} 張{m[2]}的照片"),
    (r"^Evolve (\d+|an?) Pokémon$", lambda m: f"進化 {_num(m[1])} 隻寶可夢"),
    (r"^Power up Pokémon (\d+) times?$", lambda m: f"強化寶可夢 {m[1]} 次"),
    (r"^Earn (\d+|an?) Candy walking with your buddy$", lambda m: f"和夥伴一起走路獲得 {_num(m[1])} 顆糖果"),
    (r"^Earn (\d+) Candies walking with your buddy$", lambda m: f"和夥伴一起走路獲得 {m[1]} 顆糖果"),
    (r"^Earn (\d+) hearts with your buddy$", lambda m: f"和夥伴累積 {m[1]} 顆愛心"),
    (r"^Send (\d+|an?) Gifts? and add a sticker to each$", lambda m: f"送出 {_num(m[1])} 個禮物並貼上貼圖"),
    (r"^Send (\d+|an?) Gifts? to friends$", lambda m: f"送 {_num(m[1])} 個禮物給好友"),
    (r"^Trade (\d+|an?) Pokémon$", lambda m: f"交換 {_num(m[1])} 隻寶可夢"),
    (r"^Defeat (\d+|an?) Team GO Rocket Grunts?$", lambda m: f"打敗 {_num(m[1])} 個 GO 火箭隊手下"),
    (r"^Battle in the GO Battle League (\d+) times?$", lambda m: f"在 GO 對戰聯盟對戰 {m[1]} 次"),
    (r"^Use (\d+) berries to help catch Pokémon$", lambda m: f"使用 {m[1]} 顆莓果捕捉寶可夢"),
    (r"^Use (\d+) (.+) Berries to help catch Pokémon$", lambda m: f"使用 {m[1]} 顆{m[2]}果捕捉寶可夢"),
    (r"^Transfer (\d+) Pokémon$", lambda m: f"放生 {m[1]} 隻寶可夢"),
]
_RESEARCH = [(re.compile(p), f) for p, f in _RESEARCH]


def research_task(text: str) -> str:
    for pattern, fn in _RESEARCH:
        if m := pattern.match(text):
            return fn(m)
    return event_name(text)
