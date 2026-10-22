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
### Requirement: 商品消息轉成商品

`kind` 為 `product` 的新聞 SHALL 轉成商品：`id` 沿用新聞 id，`source` 在官網消息時為「官網」、其他為「寶可夢中心」，`name` 為新聞標題，`url` 為新聞網址，`price` 與 `image` 為空字串，`media` 為新聞來源（媒體名稱）。PChome 商品的 `media` SHALL 為空字串。所有商品 SHALL 以相同欄位輸出。

#### Scenario: 寶可夢中心新聞

- **WHEN** 寶可夢中心新聞「寶可夢中心台北聖誕新品」由「上報」報導
- **THEN** payload 的 `products` SHALL 包含 `source` 為「寶可夢中心」、`name` 為該標題、`price` 為空字串、`media` 為「上報」的商品
