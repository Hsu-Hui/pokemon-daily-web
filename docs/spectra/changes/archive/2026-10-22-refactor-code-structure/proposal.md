## 摘要

整理爬蟲和 Apps Script 的程式，不加新功能：一份共用設定檔、拆小檔案、簡化新聞／商品的處理、讓 `doPost` 更安全，並替 Apps Script 的合併邏輯加測試。

## 動機

程式可以動，但已經變得雜亂，改起來容易出錯：

- 六大活動分類、提醒時間（4 小時）和保留天數（7 天）分別寫在 `scraper/translate.py`、`gas/Code.gs` 和 `gas/Index.html`，改一個地方其他地方就會跟不上。
- `gas/Index.html` 有 493 行，CSS、版面和所有 JavaScript 都在一起；`render()` 是一長串 `if (ui.tab === ...)`。
- `scraper/sources.py` 391 行裡放了五個來源，還有三套各自的日期解析。
- `main.build_news` 用 `id(n)` 對應分類，`dedupe_news` 會修改傳進來的資料，`known_titles` 參數只有測試在用。
- 商品用 `p.__dict__` 輸出，其他資料都是明確寫出欄位。
- 看板把商品類新聞假裝成商品（`price: '看消息'`，寫死 `'寶可夢官網' → '官網'`）。
- `doPost` 在檢查密碼之前就解析內容，格式錯誤時會回 Apps Script 錯誤頁，而不是 JSON。
- `mergeTimed_`／`mergeFresh_` 沒有測試。
- `translate.PATTERNS` 把句型規則和地名、流星雨對照混在一起。

這一批後面的 change（關鍵字分類、商品搜尋、Discord 錯誤通知、任務修正）都建立在這個結構上，所以先做這個。

## 解決方式

- 新增 `shared/board.json`，作為分類、提醒時數和保留天數的唯一來源。Python 直接讀它；`scripts/build_gas_config.py` 從它產生 `gas/Board.gs`，部署腳本在 `clasp push` 前重新產生，產生的檔案過期時單元測試會失敗。`getData` 把設定傳給頁面。
- 把 `gas/Index.html` 拆成 `Index.html`、`Styles.html`、`App.html`（用 `include()` 接起來），`if` 串改成每個分頁一個 render 函式。
- `scraper/sources.py` 改成 `scraper/sources/` package（每個來源一個模組，加上共用的 `dates.py`），對外名稱不變。
- `News` 加上去重前就設定好的 `kind` 欄位；`dedupe_news` 回傳新的物件，拿掉 `known_titles`。
- 商品用 `dataclasses.asdict` 輸出。商品類新聞在爬蟲端就轉成 `Product`（`source` 為官網或寶可夢中心、價格空白、`media` 為媒體），頁面直接顯示同一份清單。
- `doPost` 的解析包進 try，任何失敗都回 `{ok:false, error}`。
- 替 Apps Script 的合併函式加 Node 測試（`node --test tests/gas`），並在每日 workflow 執行。
- 流星雨和地名對照搬到 `scraper/data/translations.json`。

## 不做的事

見 design.md。

## 影響

- 影響的規格：news-feed、product-feed、data-ingest、dashboard
- 影響的程式：
  - 修改：scraper/main.py、scraper/translate.py、scraper/config.py、gas/Code.gs、gas/Index.html、scripts/deploy_gas.sh、.github/workflows/daily.yml、tests/test_scraper.py、README.md
  - 新增：shared/board.json、scripts/build_gas_config.py、gas/Board.gs、gas/Styles.html、gas/App.html、scraper/sources/__init__.py、scraper/sources/go.py、scraper/sources/pchome.py、scraper/sources/news.py、scraper/sources/official.py、scraper/sources/bahamut.py、scraper/sources/dates.py、scraper/data/translations.json、tests/gas/merge.test.js
  - 刪除：scraper/sources.py
