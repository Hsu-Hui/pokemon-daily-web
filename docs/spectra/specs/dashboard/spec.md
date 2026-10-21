# dashboard Specification

## Purpose

Apps Script 提供的看板網頁，顯示活動、任務、新商品、台灣活動與封存。對應 `gas/Code.gs` 的 `doGet`、`getData` 與 `gas/Index.html`。

## Requirements

### Requirement: Page access

`doGet` SHALL 只在能取得登入者 email 時回傳看板（標題「寶可夢每日看板」、行動版 viewport）；取不到登入者（接收資料用的匿名部署）時 SHALL 只顯示「請用看板的網址開啟。」。

#### Scenario: Opened through ingest URL

- **WHEN** 有人用接收資料的網址打開
- **THEN** 頁面 SHALL 不顯示任何資料

---
### Requirement: Data loading

看板 SHALL 一次透過 `getData` 取得 `updatedAt`、活動、任務、商品、新聞、共用設定與目前使用者的勾選狀態；有 `updatedAt` 時顯示「最後更新 <時間>」，否則顯示「還沒有資料，等每日排程跑過一次」；載入失敗時顯示錯誤訊息。所有時間 SHALL 以台灣時區顯示。抓取失敗的來源 SHALL NOT 顯示在看板上（改由 Discord 通知）。

#### Scenario: Source errors today

- **WHEN** 今天的抓取有來源失敗
- **THEN** 總覽頁 SHALL 不顯示失敗訊息，`getData` SHALL 不回傳 `errors`

---
### Requirement: Tabs

看板 SHALL 有六個分頁：總覽、GO 活動、任務待辦、新商品、台灣活動、封存；目前分頁 SHALL 記在瀏覽器 localStorage，下次開啟沿用。

#### Scenario: Overview content

- **WHEN** 使用者在總覽頁
- **THEN** 頁面 SHALL 顯示「進行中活動」（已開始且未結束的活動數）、24 小時內結束的活動數、任務進度（完成項/全部項）、今天新商品數，「快結束了，還沒完成」清單（任務：結束前 4 小時內且未全部完成；活動：24 小時內結束），以及最多 8 件今天新上架商品


<!-- @trace
source: remove-event-checkbox
updated: 2026-10-22
code:
  - gas/App.html
  - tests/gas/load.js
  - README.md
  - tests/gas/app.js
  - gas/Code.gs
  - gas/Styles.html
tests:
  - tests/gas/app.test.js
  - tests/gas/merge.test.js
-->

---
### Requirement: GO events tab

GO 活動頁 SHALL 列出所有未結束的活動，不提供完成勾選方塊；提供六大分類的多選篩選（「全部」代表不篩選，並顯示每類數量），寬螢幕用表格、窄螢幕用卡片，顯示剩餘時間與進度條；不在六大分類的活動 SHALL 歸到「其他」。

#### Scenario: Multi-select categories

- **WHEN** 使用者選了「聚焦時刻」和「GO Pass」
- **THEN** 列表 SHALL 只顯示這兩類活動，按「全部」SHALL 清除篩選

#### Scenario: Default and custom sorting

- **WHEN** 使用者沒有點排序
- **THEN** 活動 SHALL 依類型（六大分類順序）→ 開始 → 結束排序；點類型/開始/結束 SHALL 以該欄優先排序，再點一次反向

#### Scenario: No done checkbox

- **WHEN** 使用者打開 GO 活動頁
- **THEN** 表格與卡片 SHALL 沒有勾選方塊與「完成」欄，舊的活動完成紀錄 SHALL 不影響列表


<!-- @trace
source: remove-event-checkbox
updated: 2026-10-22
code:
  - gas/App.html
  - tests/gas/load.js
  - README.md
  - tests/gas/app.js
  - gas/Code.gs
  - gas/Styles.html
tests:
  - tests/gas/app.test.js
  - tests/gas/merge.test.js
-->

---
### Requirement: Tasks tab

任務待辦頁 SHALL 列出未放棄且未結束的任務組，依剩餘時間由少到多排序，每組顯示期間、剩餘時間、完成數、進度條、每個任務的勾選框與獎勵（沒有獎勵時顯示連到原文的「見原文」），以及「放棄」按鈕。

#### Scenario: Give up a group

- **WHEN** 使用者按「放棄」
- **THEN** 該任務組 SHALL 移到封存頁且不再提醒

---
### Requirement: Products tab

新商品頁 SHALL 顯示 payload 的商品（PChome、寶可夢中心、官網，欄位相同，不在頁面上轉換新聞），沒有價格的商品 SHALL 顯示「看消息」，有 `media` 時來源顯示為「來源 · 媒體」。頁面提供 PChome/寶可夢中心/官網的多選來源篩選與排序（上架時間新到舊（預設）、舊到新、價格高到低、低到高；沒有價格的排最後）。首次出現未滿 24 小時的商品 SHALL 標示 NEW。

#### Scenario: Sort by price

- **WHEN** 使用者選「價格：低到高」
- **THEN** 有價格的商品 SHALL 由低到高排列，沒有價格的排在最後

#### Scenario: Announcement without price

- **WHEN** 商品來源為「官網」且沒有價格
- **THEN** 價格位置 SHALL 顯示「看消息」

---
### Requirement: Taiwan news tab

台灣活動頁 SHALL 列出 `kind` 為 `event` 的新聞，依發布時間（沒有時用 `firstSeen`）新到舊排序，並顯示「另有 N 家報導」。

#### Scenario: Merged coverage

- **WHEN** 一則新聞的 `others` 有 2 家媒體
- **THEN** 該則 SHALL 顯示「另有 2 家報導」

---
### Requirement: Archive tab

封存頁 SHALL 列出已放棄或已結束的任務組，以及已結束的活動，並註明原因；尚未結束的已放棄任務組 SHALL 提供「復原」按鈕，活動 SHALL 沒有「復原」按鈕。

#### Scenario: Restore a given-up group

- **WHEN** 使用者在封存頁對尚未結束的已放棄任務組按「復原」
- **THEN** 該任務組 SHALL 回到任務待辦頁

#### Scenario: Ended event

- **WHEN** 活動結束
- **THEN** 該活動 SHALL 出現在封存頁並顯示「已結束 · <結束時間>」


<!-- @trace
source: remove-event-checkbox
updated: 2026-10-22
code:
  - gas/App.html
  - tests/gas/load.js
  - README.md
  - tests/gas/app.js
  - gas/Code.gs
  - gas/Styles.html
tests:
  - tests/gas/app.test.js
  - tests/gas/merge.test.js
-->

---
### Requirement: Pagination

GO 活動、任務待辦、新商品、台灣活動、封存的列表 SHALL 每頁最多 25 筆，超過時顯示分頁列（第一頁、最後一頁、目前頁前後 2 頁，其餘以…省略）與總筆數；改變篩選或排序時 SHALL 回到第 1 頁。

#### Scenario: 30 products

- **WHEN** 有 30 件商品
- **THEN** 第 1 頁 SHALL 顯示 25 件，第 2 頁顯示 5 件

---
### Requirement: Shared settings

活動分類清單與順序、任務提醒時數、新聞與商品保留天數 SHALL 只定義在 `shared/board.json`。爬蟲 SHALL 直接讀取該檔；Apps Script SHALL 使用由它產生的 `gas/Board.gs`（全域 `BOARD`），`getData` SHALL 以 `config` 回傳給看板，看板上的分類、「4 小時」「7 天」等文字 SHALL 由這份設定產生。`gas/Board.gs` 與 `shared/board.json` 不一致時單元測試 SHALL 失敗。

#### Scenario: Change retention days

- **WHEN** 把 `keepProductDays` 改成 10 並重新產生 `gas/Board.gs`
- **THEN** 商品保留與新商品頁的說明文字 SHALL 都變成 10 天

#### Scenario: Stale generated file

- **WHEN** 修改 `shared/board.json` 但沒有重新產生 `gas/Board.gs`
- **THEN** `python -m unittest` SHALL 失敗

---
### Requirement: Product name search

新商品頁 SHALL 提供搜尋框，只顯示名稱包含輸入文字的商品（不分大小寫，忽略前後空白），並與來源篩選、排序同時生效；分頁 SHALL 只計算符合的商品，搜尋文字改變時 SHALL 回到第 1 頁。重畫列表時搜尋框 SHALL 保持焦點與游標位置。沒有符合的商品時 SHALL 顯示「找不到符合「<文字>」的商品」；清空搜尋框時 SHALL 顯示全部商品。

#### Scenario: Search with source filter

- **WHEN** 使用者選了來源「PChome」並輸入「pikachu」
- **THEN** 列表 SHALL 只顯示來源為 PChome 且名稱含 Pikachu（不分大小寫）的商品，並在第 1 頁

#### Scenario: No match

- **WHEN** 使用者輸入「不存在的商品」
- **THEN** 頁面 SHALL 顯示「找不到符合「不存在的商品」的商品」

##### Example: Matching

| 商品名稱 | 搜尋文字 | 顯示 |
| -------- | -------- | ---- |
| Pokémon 皮卡丘 絨毛玩偶 | 皮卡丘 | 是 |
| POKEMON 卡牌 禮盒 | pokemon | 是 |
| 寶可夢 伊布 馬克杯 | 皮卡丘 | 否 |
| 寶可夢 伊布 馬克杯 | "  伊布 " | 是 |