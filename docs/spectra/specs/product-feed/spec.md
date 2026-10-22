# product-feed Specification

## Purpose

從 PChome 24h 搜尋 API 取得最新上架的寶可夢商品。對應 `scraper/sources/` 的 `fetch_pchome`。寶可夢中心新聞與官網商品公告的部分由 news-feed 產生、在看板上併入新商品頁。

## Requirements

### Requirement: PChome 搜尋

系統 SHALL 對「寶可夢」「Pokemon」兩個關鍵字各呼叫 PChome 搜尋 API（`sort=new/dc`，帶 PChome Referer），每個關鍵字最多翻 5 頁（`PCHOME_PAGES`），且不超過 API 回報的 `totalPage`。

#### Scenario: 頁數較少

- **WHEN** API 回報 `totalPage` 為 2
- **THEN** 該關鍵字 SHALL 只讀 2 頁

---
### Requirement: 商品篩選

商品名稱 SHALL 包含 `PCHOME_NAME_KEYWORDS` 其中之一（不分大小寫），且依商品 Id 跨關鍵字去重；沒有 Id 的商品 SHALL 略過。

#### Scenario: 搜尋到無關商品

- **WHEN** 搜尋結果商品名稱不含任何寶可夢關鍵字
- **THEN** 該商品 SHALL 不輸出

---
### Requirement: 商品欄位

每筆商品 SHALL 包含 `id`（`pchome:<Id>`）、`source`（`PChome`）、`name`、`url`（`https://24h.pchome.com.tw/prod/<Id>`）、`price`（整數價格格式化為 `$1,234`，否則空字串）與 `image`（`picB` 或 `picS` 接在 `https://cs-a.ecimg.tw/` 後，沒有時為空字串）。

#### Scenario: 價格不是整數

- **WHEN** API 的 `price` 不是整數
- **THEN** `price` SHALL 為空字串

---
### Requirement: 移除重複商品

商品 SHALL 以「名稱（去掉多餘空白、不分大小寫）＋價格」為鍵去重，只保留第一筆（最新上架）。看板顯示時 SHALL 用同一個鍵再去重一次，讓試算表裡已存的重複商品不再顯示。

#### Scenario: 同一商品有兩個 PChome 編號

- **WHEN** PChome 回傳 `DECU5W-A900FSAGQ` 與 `DEAS4E-A900FSAIT`，名稱都是「皮卡丘 卡比獸 百變怪 精靈球 造型存錢筒」、價格都是 $590
- **THEN** payload 與新商品頁 SHALL 只有一筆

#### Scenario: 名稱相同價格不同

- **WHEN** 兩件商品名稱相同但價格不同
- **THEN** 兩件 SHALL 都保留

<!-- @trace
source: fix-board-display
updated: 2026-10-22
code:
  - .spectra.yaml
  - scraper/sources/__init__.py
  - gas/Styles.html
  - scraper/sources/pchome.py
  - scraper/main.py
  - gas/App.html
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->
