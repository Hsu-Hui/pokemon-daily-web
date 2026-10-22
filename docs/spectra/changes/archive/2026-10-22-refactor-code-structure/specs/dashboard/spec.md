## ADDED Requirements

### Requirement: 共用設定

活動分類清單與順序、任務提醒時數、新聞與商品保留天數 SHALL 只定義在 `shared/board.json`。爬蟲 SHALL 直接讀取該檔；Apps Script SHALL 使用由它產生的 `gas/Board.gs`（全域 `BOARD`），`getData` SHALL 以 `config` 回傳給看板，看板上的分類、「4 小時」「7 天」等文字 SHALL 由這份設定產生。`gas/Board.gs` 與 `shared/board.json` 不一致時單元測試 SHALL 失敗。

#### Scenario: 修改保留天數

- **WHEN** 把 `keepProductDays` 改成 10 並重新產生 `gas/Board.gs`
- **THEN** 商品保留與新商品頁的說明文字 SHALL 都變成 10 天

#### Scenario: 產生的檔案過期

- **WHEN** 修改 `shared/board.json` 但沒有重新產生 `gas/Board.gs`
- **THEN** `python -m unittest` SHALL 失敗

## MODIFIED Requirements

### Requirement: 新商品頁

新商品頁 SHALL 顯示 payload 的商品（PChome、寶可夢中心、官網，欄位相同，不在頁面上轉換新聞），沒有價格的商品 SHALL 顯示「看消息」，有 `media` 時來源顯示為「來源 · 媒體」。頁面提供 PChome/寶可夢中心/官網的多選來源篩選與排序（上架時間新到舊（預設）、舊到新、價格高到低、低到高；沒有價格的排最後）。首次出現未滿 24 小時的商品 SHALL 標示 NEW。

#### Scenario: 依價格排序

- **WHEN** 使用者選「價格：低到高」
- **THEN** 有價格的商品 SHALL 由低到高排列，沒有價格的排在最後

#### Scenario: 沒有價格的公告

- **WHEN** 商品來源為「官網」且沒有價格
- **THEN** 價格位置 SHALL 顯示「看消息」
