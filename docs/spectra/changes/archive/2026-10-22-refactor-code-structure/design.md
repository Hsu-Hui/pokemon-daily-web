## 背景

專案有兩個執行環境：GitHub Actions 上的 Python 爬蟲，以及 Google Apps Script（由 clasp 從 `gas/` 部署）。clasp 2.4.2 只會上傳 `.gs`、`.js`、`.html` 和 `appsscript.json`，所以 Apps Script 執行時讀不到 repo 裡任意的 JSON 檔。除了規格差異裡寫明的地方，行為都必須維持不變。

## 目標／不做的事

**目標：**

- 分類、提醒時數和保留天數只在一個地方修改。
- `scraper/sources/` 和 `gas/` 拆成小而單一用途的檔案。
- 商品公告以商品的形式儲存和顯示，頁面不再轉換。
- `doPost` 一律回 JSON。
- `mergeTimed_` 和 `mergeFresh_` 有自動測試。

**不做的事：**

- 不加看板新功能（搜尋、關鍵字分類、Discord 通知是另外的 change）。
- 不改任務 id 和任務來源（由 `fix-empty-task-list` 處理）。
- Apps Script 程式不用打包工具或 npm 套件。
- 不改分頁名稱，也不改每日資料最外層的欄位。

## 決策

### 共用設定檔，加上產生的 Apps Script 版本

`shared/board.json` 放 `categories`（依序的 `{name, keywords}`；keywords 在 `keyword-event-categories` 之前先留空）、`remindHours`、`keepNewsDays`、`keepProductDays`、`keepArchiveDays`、`keepSeenDays`。`scripts/build_gas_config.py` 把它寫成 `gas/Board.gs` 的 `const BOARD = <json>;`，開頭註明「自動產生，不要直接改」。`scripts/deploy_gas.sh` 在上傳前重新產生，`tests/test_scraper.py` 檢查 commit 進去的 `gas/Board.gs` 和產生結果一致。放棄的做法：把設定放進每日資料傳給 Apps Script——下一次抓資料之前頁面會拿到舊的或沒有設定，提醒也會變成依賴爬蟲執行。

### 用 include() 拆分 Index.html

`Code.gs` 加上 `include(name)`，回傳 `HtmlService.createHtmlOutputFromFile(name).getContent()`；`Index.html` 只留骨架，用 `<?!= include('…') ?>` 接上 `Styles` 和 `App`。`render()` 改成 `RENDERERS` 對照表，每個分頁一個函式（`renderOverview`、`renderGo`、`renderTasks`、`renderShop`、`renderTw`、`renderArchive`）。放棄的做法：每個分頁各自一頁——要多次呼叫 `google.script.run` 載入資料。

### sources package 與共用的日期模組

`scraper/sources/` 裡有 `go.py`、`pchome.py`、`news.py`（Google 新聞和去重）、`official.py`、`bahamut.py`、`http.py`（`_get`）和 `dates.py`（`parse_time`、`parse_date`、`mkdate`）。`__init__.py` 重新匯出公開名稱和測試用到的內部函式（`_clean_title`），所以 `from scraper import sources` 照樣可用。

### 去重前先標好分類

`News` 加上 `kind: str = "event"`。`build_news` 在呼叫 `dedupe_news` 之前設定每則的分類（官網消息用 `news_kind`）；`dedupe_news` 用 `dataclasses.replace` 複製保留的項目，不修改輸入。`known_titles` 和它的測試一起拿掉。

### 商品公告在爬蟲端轉成商品

去重後，`kind == "product"` 的新聞由 `news_to_product` 轉成 `Product(id, source="官網" if 官網 else "寶可夢中心", name=標題, url, price="", image="", media=<媒體>)` 加進 `products`；`news` 只留 `event`。商品用 `dataclasses.asdict` 輸出。商品分頁加上 `media` 欄。沒有價格的商品頁面顯示「看消息」。新聞分頁裡舊的商品類資料會被頁面的 `kind === 'event'` 篩掉，7 天內自然過期。

### doPost 一律回 JSON

解析和密碼檢查都放進 `try`；任何例外都回 `{ok:false, error:<訊息>}`。通過密碼檢查後才取得 script lock。

### Apps Script 純函式的 Node 測試

`tests/gas/merge.test.js` 把 `gas/Board.gs` 和 `gas/Code.gs` 載入 `vm`，用假的全域物件，以 `node:test` 測 `mergeTimed_` 和 `mergeFresh_`。每日 workflow 在 Python 測試之後執行 `node --test tests/gas`（用 `actions/setup-node` 安裝 Node 20）。

### 翻譯對照表放進資料檔

`scraper/data/translations.json` 放 `months`、`meteors` 和 `places`。`PATTERNS` 只留正規表示式規則；地名在規則之後套用，和原本放在 `PATTERNS` 最後面的效果相同。

## 實作約定

- 行為：看板、接收資料的回應、提醒和每日資料都和原本一樣，除了：(a) 商品公告出現在 `payload.products`，`source` 為官網／寶可夢中心、`price: ""`，並有 `media` 欄位；(b) 格式錯誤的 POST 回 `{ok:false,error}`；(c) `getData()` 多回傳 `config`（BOARD 物件）。
- 介面：上面列出的 `shared/board.json` 欄位；`gas/Board.gs` 定義全域 `BOARD`；`Code.gs` 的 `include(name)`；`scraper.sources` 對外名稱和原本相同，只少了 `dedupe_news(..., known_titles)`。
- 失敗情況：`gas/Board.gs` 過期時 `python -m unittest` 失敗；部署時仍會重新產生。
- 驗收：`python -m unittest` 和 `node --test tests/gas` 通過；沒設定接收資料時 `python -m scraper.main` 會寫出 `out/payload.json`；搜尋確認 `gas/` 和 `scraper/translate.py` 裡除了讀取 `Board.gs`／`board.json` 之外，沒有寫死的 4 小時、7 天或分類清單。
- 範圍：包含本設計列出的項目；不包含新功能、任務 id、任務來源、分頁改名。

## 風險與取捨

- [改了 board.json 忘記重新產生] → 單元測試失敗，部署時也會重新產生。
- [Apps Script 的 include 樣板讓頁面壞掉] → 部署後手動檢查；HTML 只是重新排列，沒有改寫。
- [商品資料格式改變] → 舊資料 7 天內過期；頁面可以處理沒有 `media` 的資料。

## 部署計畫

合併到 main；部署 workflow 重新產生 `Board.gs` 並上傳。下一次每日執行會寫入新的商品格式。要退回的話：revert 合併的 commit，部署 workflow 會上傳舊的程式。
