"""可調整的設定：資料來源網址、關鍵字、時區。分類、提醒和保留天數在 shared/board.json。"""
import json
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Taipei")

# 爬蟲和 Apps Script 共用的設定（Apps Script 端是產生的 gas/Board.gs）
BOARD = json.loads((Path(__file__).resolve().parent.parent / "shared" / "board.json").read_text(encoding="utf-8"))

# Pokémon GO 活動（LeekDuck 資料，由 ScrapedDuck 整理成 JSON）
GO_EVENTS_URL = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/events.min.json"
# 目前的田野調查任務和獎勵（LeekDuck，ScrapedDuck 整理）
GO_RESEARCH_URL = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/research.min.json"
# 不需要「完成」的活動類型（ScrapedDuck 的 eventType），不列出
GO_SKIP_TYPES = {"season", "go-battle-league"}
# 列出幾天內會開始的活動
GO_LOOKAHEAD_DAYS = 14
# 進行中的活動最多讀幾個 LeekDuck 活動頁找限時調查
LEEKDUCK_MAX_PAGES = 20

# 巴哈姆特 Pokémon GO 哈啦板：從【情報】文章抓任務和獎勵
BAHAMUT_BOARD_URL = "https://forum.gamer.com.tw/B.php"
BAHAMUT_POST_URL = "https://forum.gamer.com.tw/C.php"
BAHAMUT_BSN = 29659
# 文章標題要包含其中一個字才當成任務文
BAHAMUT_TITLE_KEYWORDS = ["調查", "任務", "課題"]
# 列表頁抓幾頁、最多讀幾篇文章
BAHAMUT_PAGES = 2
BAHAMUT_MAX_POSTS = 15

# PChome 24h 搜尋 API，依上架時間排序；每個關鍵字最多翻幾頁
PCHOME_SEARCH_URL = "https://ecshweb.pchome.com.tw/search/v3.3/all/results"
PCHOME_QUERIES = ["寶可夢", "Pokemon"]
PCHOME_PAGES = 5
# 商品名稱要包含其中一個關鍵字才算（排除只是相關搜尋到的雜項）
PCHOME_NAME_KEYWORDS = ["寶可夢", "Pokemon", "Pokémon", "POKEMON", "皮卡丘", "神奇寶貝"]
PCHOME_IMAGE_HOST = "https://cs-a.ecimg.tw"

# 寶可夢台灣官網的最新消息
OFFICIAL_NEWS_URL = "https://tw.portal-pokemon.com/topics/"
# 官網消息只收幾天內發布的（舊公告不算新消息）
OFFICIAL_MAX_AGE_DAYS = 3
# 分類或標題有這些字的官網消息歸到「新商品」，其他歸到「台灣活動」
PRODUCT_WORDS = ["商品", "發售", "上市", "販售", "新品", "周邊", "週邊", "寶可夢中心"]

# Google News RSS：只抓最近 24 小時
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
NEWS_QUERIES = {
    "pc_taipei": '("寶可夢中心" OR "Pokémon Center TAIPEI") (新品 OR 商品 OR 發售 OR 上架) when:1d',
    "tw_events": '寶可夢 (活動 OR 快閃 OR 展覽 OR 聯名 OR 見面會 OR 嘉年華) 台灣 when:1d',
}
NEWS_MAX_AGE_HOURS = 24
# 新聞標題要有其中一個字才收（Google 新聞會混進不相關的「新品」新聞）
NEWS_TITLE_KEYWORDS = ["寶可夢", "pokémon", "pokemon", "皮卡丘", "神奇寶貝", "ptcg"]
# 兩則標題的相似度超過這個值就當成同一則新聞
NEWS_SIMILARITY = 0.45

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
