"""把 LeekDuck 的英文活動名稱翻成中文（字典對照，不用 AI）。對不到的專有名詞保留原文。"""
import json
import re
from pathlib import Path

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

MONTHS = {
    "January": "1月", "February": "2月", "March": "3月", "April": "4月",
    "May": "5月", "June": "6月", "July": "7月", "August": "8月",
    "September": "9月", "October": "10月", "November": "11月", "December": "12月",
}

METEORS = {
    "Orionids": "獵戶座", "Leonids": "獅子座", "Geminids": "雙子座", "Perseids": "英仙座",
    "Quadrantids": "象限儀座", "Lyrids": "天琴座", "Eta Aquariids": "寶瓶座η",
    "Southern Delta Aquariids": "南寶瓶座δ", "Draconids": "天龍座", "Taurids": "金牛座",
}

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
    (r"Wild Area", "野外區域"),
    (r"City Safari", "城市狩獵"),
    (r"Mexico City", "墨西哥城"),
    (r"Los Angeles", "洛杉磯"),
    (r"London", "倫敦"),
    (r"Boston", "波士頓"),
    (r"Sendai • Tohoku", "仙台・東北"),
    (r"Global", "全球"),
    (r"Kaohsiung", "高雄"),
    (r"Taipei", "台北"),
    (r"Taiwan", "台灣"),
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
    # 中文字和 X / Y 之間的空白拿掉，例如「超級噴火龍 X」→「超級噴火龍X」
    return re.sub(r"(?<=[一-鿿]) (?=[XY](?:$|、))", "", text)


def event_type(type_slug: str, heading: str) -> str:
    return TYPE_LABELS.get(type_slug, heading)
