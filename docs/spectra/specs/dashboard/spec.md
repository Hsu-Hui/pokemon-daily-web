# dashboard Specification

## Purpose

Apps Script 提供的看板網頁，顯示活動、任務、新商品、台灣活動與封存。對應 `gas/Code.gs` 的 `doGet`、`getData` 與 `gas/Index.html`。

## Requirements

### Requirement: 頁面存取

`doGet` SHALL 只在能取得登入者 email 時回傳看板（標題「寶可夢每日看板」、行動版 viewport）；取不到登入者（接收資料用的匿名部署）時 SHALL 只顯示「請用看板的網址開啟。」。

#### Scenario: 用接收資料網址開啟

- **WHEN** 有人用接收資料的網址打開
- **THEN** 頁面 SHALL 不顯示任何資料

---
### Requirement: 資料載入

看板 SHALL 一次透過 `getData` 取得 `updatedAt`、活動、任務、商品、新聞、共用設定與目前使用者的勾選狀態；有 `updatedAt` 時顯示「最後更新 <時間>」，否則顯示「還沒有資料，等每日排程跑過一次」；載入失敗時顯示錯誤訊息。所有時間 SHALL 以台灣時區顯示。抓取失敗的來源 SHALL NOT 顯示在看板上（改由 Discord 通知）。

#### Scenario: 今天有來源失敗

- **WHEN** 今天的抓取有來源失敗
- **THEN** 總覽頁 SHALL 不顯示失敗訊息，`getData` SHALL 不回傳 `errors`

---
### Requirement: 分頁

看板 SHALL 有七個分頁：總覽、GO 活動、任務待辦、新商品、活動&新聞、我的最愛、封存；目前分頁 SHALL 記在瀏覽器 localStorage，下次開啟沿用。

#### Scenario: 總覽內容

- **WHEN** 使用者在總覽頁
- **THEN** 頁面 SHALL 顯示「進行中活動」（已開始且未結束的活動數）、24 小時內結束的活動數、任務進度（完成項/全部項）、今天新商品數，「快結束了，還沒完成」清單（任務：未放棄、未全部完成、且在 48 小時（`overviewTaskHours`）內結束的任務組，顯示剩餘時間與未完成項數；活動：24 小時內結束），以及最多 8 件今天新上架商品

#### Scenario: 任務組 40 小時後結束

- **WHEN** 某任務組 40 小時後結束且還有 3 項未完成
- **THEN** 該組 SHALL 出現在「快結束了，還沒完成」，顯示「剩 40 小時 · 3 項未完成」

#### Scenario: 我的最愛分頁位置

- **WHEN** 使用者打開看板
- **THEN** 「我的最愛」SHALL 位在「活動&新聞」與「封存」之間


<!-- @trace
source: news-tab-sources
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - scraper/main.py
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->

---
### Requirement: GO 活動頁

GO 活動頁 SHALL 列出所有未結束的活動，不提供完成勾選方塊；提供六大分類的多選篩選（「全部」代表不篩選，並顯示每類數量），寬螢幕用表格、窄螢幕用卡片，顯示剩餘時間與進度條；不在六大分類的活動 SHALL 歸到「其他」。

#### Scenario: 多選分類

- **WHEN** 使用者選了「聚焦時刻」和「GO Pass」
- **THEN** 列表 SHALL 只顯示這兩類活動，按「全部」SHALL 清除篩選

#### Scenario: 預設與自訂排序

- **WHEN** 使用者沒有點排序
- **THEN** 活動 SHALL 依類型（六大分類順序）→ 開始 → 結束排序；點類型/開始/結束 SHALL 以該欄優先排序，再點一次反向

#### Scenario: 沒有完成勾選方塊

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
### Requirement: 任務待辦頁

任務待辦頁 SHALL 列出未放棄且未結束的任務組，依剩餘時間由少到多排序，每組顯示期間、剩餘時間、完成數、進度條、每個任務的勾選框與獎勵（沒有獎勵時顯示連到原文的「見原文」），以及「放棄」按鈕。

#### Scenario: 放棄任務組

- **WHEN** 使用者按「放棄」
- **THEN** 該任務組 SHALL 移到封存頁且不再提醒

---
### Requirement: 新商品頁

新商品頁 SHALL 只顯示 PChome 商品；試算表裡來源不是 PChome 的舊商品列（寶可夢中心新聞、官網公告）SHALL 不顯示在新商品頁。頁面提供排序（上架時間新到舊（預設）、舊到新、價格高到低、低到高；沒有價格的排最後），沒有價格的商品 SHALL 顯示「看消息」，不提供來源篩選按鈕。首次出現未滿 24 小時的商品 SHALL 標示 NEW。

#### Scenario: 依價格排序

- **WHEN** 使用者選「價格：低到高」
- **THEN** 有價格的商品 SHALL 由低到高排列，沒有價格的排在最後

#### Scenario: 寶可夢中心新聞不在新商品

- **WHEN** 試算表商品分頁裡有來源為「寶可夢中心」的舊資料
- **THEN** 新商品頁 SHALL 不顯示它，它 SHALL 出現在活動&新聞


<!-- @trace
source: news-tab-sources
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - scraper/main.py
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->

---
### Requirement: 封存頁

封存頁 SHALL 列出已放棄或已結束的任務組，以及已結束的活動，並註明原因；尚未結束的已放棄任務組 SHALL 提供「復原」按鈕，活動 SHALL 沒有「復原」按鈕。

#### Scenario: 復原已放棄的任務組

- **WHEN** 使用者在封存頁對尚未結束的已放棄任務組按「復原」
- **THEN** 該任務組 SHALL 回到任務待辦頁

#### Scenario: 已結束的活動

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
### Requirement: 分頁顯示

GO 活動、任務待辦、新商品、台灣活動、封存的列表 SHALL 每頁最多 25 筆，超過時顯示分頁列（第一頁、最後一頁、目前頁前後 2 頁，其餘以…省略）與總筆數；改變篩選或排序時 SHALL 回到第 1 頁。

#### Scenario: 30 件商品

- **WHEN** 有 30 件商品
- **THEN** 第 1 頁 SHALL 顯示 25 件，第 2 頁顯示 5 件

---
### Requirement: 共用設定

活動分類清單與順序、任務提醒時數、新聞與商品保留天數 SHALL 只定義在 `shared/board.json`。爬蟲 SHALL 直接讀取該檔；Apps Script SHALL 使用由它產生的 `gas/Board.gs`（全域 `BOARD`），`getData` SHALL 以 `config` 回傳給看板，看板上的分類、「4 小時」「7 天」等文字 SHALL 由這份設定產生。`gas/Board.gs` 與 `shared/board.json` 不一致時單元測試 SHALL 失敗。

#### Scenario: 修改保留天數

- **WHEN** 把 `keepProductDays` 改成 10 並重新產生 `gas/Board.gs`
- **THEN** 商品保留與新商品頁的說明文字 SHALL 都變成 10 天

#### Scenario: 產生的檔案過期

- **WHEN** 修改 `shared/board.json` 但沒有重新產生 `gas/Board.gs`
- **THEN** `python -m unittest` SHALL 失敗

---
### Requirement: 商品名稱搜尋

新商品頁 SHALL 提供搜尋框，只顯示名稱包含輸入文字的商品（不分大小寫，忽略前後空白），並與排序同時生效；分頁 SHALL 只計算符合的商品，搜尋文字改變時 SHALL 回到第 1 頁。重畫列表時搜尋框 SHALL 保持焦點與游標位置。沒有符合的商品時 SHALL 顯示「找不到符合「<文字>」的商品」；清空搜尋框時 SHALL 顯示全部商品。

#### Scenario: 搜尋商品

- **WHEN** 使用者輸入「pikachu」
- **THEN** 列表 SHALL 只顯示名稱含 Pikachu（不分大小寫）的商品，並在第 1 頁

#### Scenario: 找不到符合的商品

- **WHEN** 使用者輸入「不存在的商品」
- **THEN** 頁面 SHALL 顯示「找不到符合「不存在的商品」的商品」

##### Example: 搜尋比對

| 商品名稱 | 搜尋文字 | 顯示 |
| -------- | -------- | ---- |
| Pokémon 皮卡丘 絨毛玩偶 | 皮卡丘 | 是 |
| POKEMON 卡牌 禮盒 | pokemon | 是 |
| 寶可夢 伊布 馬克杯 | 皮卡丘 | 否 |
| 寶可夢 伊布 馬克杯 | "  伊布 " | 是 |


<!-- @trace
source: news-tab-sources
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - scraper/main.py
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->

---
### Requirement: 排版不擠壓

所有分頁在 375、768、1280 px 寬度下，活動名稱、任務文字、新聞標題與商品名稱 SHALL 以整行換行顯示，不得被其他欄位擠壓成每行少於 12 個字，表格欄位 SHALL 不被裁切。GO 活動表格的活動名稱欄 SHALL 至少 240 px；手機寬度下任務的獎勵 SHALL 顯示在任務文字下方，任務組標題 SHALL 獨占一行；分頁列在窄螢幕 SHALL 為可橫向捲動的單行。

#### Scenario: 電腦上的長活動名稱

- **WHEN** 在 1280 px 寬度打開 GO 活動，活動名稱為「極巨對戰日：極巨化由克希、艾姆利多、亞克諾姆」
- **THEN** 名稱 SHALL 在名稱欄內最多兩行顯示，「剩餘」欄 SHALL 完整可見

#### Scenario: 手機上的任務文字

- **WHEN** 在 375 px 寬度打開任務待辦
- **THEN** 任務文字 SHALL 使用整列寬度，獎勵顯示在下一行

#### Scenario: 頁面上沒有結束時間的活動

- **WHEN** 試算表裡還有沒有結束時間的舊活動
- **THEN** 看板 SHALL 不顯示該活動，頁面上 SHALL 不出現「Infinity」

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

---
### Requirement: 儲存列

「任務待辦」分頁頂端 SHALL 有固定的儲存列，顯示「有 N 項變更未儲存」與「儲存」按鈕；沒有變更時按鈕 SHALL 停用並顯示「已儲存」。其他分頁 SHALL 不顯示儲存列。任務勾選 SHALL 先存在頁面的草稿，按「儲存」才送出；切換分頁 SHALL 保留草稿；有未儲存變更時離開或重新整理頁面 SHALL 跳出瀏覽器確認。「放棄」「復原」SHALL 立即儲存，不經過草稿。

#### Scenario: 勾選後儲存

- **WHEN** 使用者勾了 3 個任務後按「儲存」
- **THEN** 系統 SHALL 一次送出 3 項變更，成功後儲存列顯示「已儲存」

#### Scenario: 儲存失敗

- **WHEN** 儲存失敗
- **THEN** 草稿 SHALL 保留，並顯示「儲存失敗，請再試一次」

#### Scenario: 有未儲存變更時離開

- **WHEN** 有未儲存的勾選時重新整理頁面
- **THEN** 瀏覽器 SHALL 先詢問是否離開

#### Scenario: 其他分頁沒有儲存列

- **WHEN** 使用者在任務待辦勾了任務後切到 GO 活動
- **THEN** GO 活動頁 SHALL 不顯示儲存列，回到任務待辦時草稿與儲存列 SHALL 還在


<!-- @trace
source: news-tab-sources
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - scraper/main.py
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->

---
### Requirement: 活動&新聞頁

活動&新聞頁 SHALL 列出所有消息，依發布時間（沒有時用 `firstSeen`）新到舊排序，並顯示「另有 N 家報導」。頁面 SHALL 提供可多選的來源篩選（「全部」代表不篩選，並顯示每類數量）：「官方」為來源是寶可夢官網的消息；「新聞」為其他媒體中 `kind` 為 `product` 的報導（例如寶可夢中心新品）；「活動」為其他媒體中 `kind` 為 `event` 的報導。試算表商品分頁裡來源為「官網」或「寶可夢中心」的舊資料 SHALL 也顯示在這一頁（官網為「官方」，寶可夢中心為「新聞」）。改變篩選時 SHALL 回到第 1 頁。

#### Scenario: 合併的報導

- **WHEN** 一則新聞的 `others` 有 2 家媒體
- **THEN** 該則 SHALL 顯示「另有 2 家報導」

#### Scenario: 只看官方

- **WHEN** 使用者選了「官方」
- **THEN** 列表 SHALL 只顯示來源為寶可夢官網的消息

##### Example: 來源分類

| 來源 | kind | 分類 |
| ---- | ---- | ---- |
| 寶可夢官網 | event | 官方 |
| 寶可夢官網 | product | 官方 |
| 上報（寶可夢中心新品） | product | 新聞 |
| 自由時報（台灣活動） | event | 活動 |

<!-- @trace
source: news-tab-sources
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - scraper/main.py
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->

---
### Requirement: GO 活動行事曆

GO 活動頁 SHALL 在分類按鈕與活動列表之間顯示「行事曆」卡片。寬螢幕 SHALL 一次顯示 14 天、從本週一（台灣時間）開始，窄螢幕 SHALL 顯示 7 天、從今天開始；每個在顯示範圍內的未結束活動一列，依開始時間排序，色條從開始日畫到結束日（結束在 00:00 時算前一天），顏色依六大分類，並有圖例。今天那一欄 SHALL 有底色標示。只有一天的活動 SHALL 在色條上顯示開始時間，多天的活動顯示「MM/DD – MM/DD」。活動在顯示範圍之前開始或之後結束時，色條該側 SHALL 切平並顯示 ‹ 或 ›。色條 SHALL 是連到活動原文的連結。行事曆 SHALL 套用上方的分類篩選；「上一週」「下一週」SHALL 移動一週，「今天」SHALL 回到本週；「收合」SHALL 只留標題列，收合狀態記在瀏覽器 localStorage。顯示範圍內沒有活動時 SHALL 顯示「這段期間沒有活動」。

#### Scenario: 色條位置

- **WHEN** 今天是 2026/10/23（週五），使用者在寬螢幕打開 GO 活動頁
- **THEN** 行事曆 SHALL 顯示 10/19 到 11/01，色條依下表畫出

##### Example: 色條

| 活動期間（台灣時間） | 色條 | 左側 | 右側 | 色條文字 |
| -------------------- | ---- | ---- | ---- | -------- |
| 10/01 10:00 – 10/31 20:00 | 10/19 – 10/31 | ‹ 切平 | 圓角 | 10/01 – 10/31 |
| 10/22 10:00 – 10/28 20:00 | 10/22 – 10/28 | 圓角 | 圓角 | 10/22 – 10/28 |
| 10/27 18:00 – 10/27 19:00 | 10/27 | 圓角 | 圓角 | 18:00 |
| 10/28 10:00 – 11/03 20:00 | 10/28 – 11/01 | 圓角 | 切平 › | 10/28 – 11/03 |
| 10/30 00:00 – 10/31 00:00 | 10/30 | 圓角 | 圓角 | 00:00 |

#### Scenario: 分類篩選

- **WHEN** 使用者選了「聚焦時刻」
- **THEN** 行事曆 SHALL 只畫聚焦時刻的活動

#### Scenario: 切換週數

- **WHEN** 使用者按兩次「下一週」再按「今天」
- **THEN** 寬螢幕行事曆 SHALL 先顯示 11/02 – 11/15，按「今天」後回到 10/19 – 11/01；窄螢幕 SHALL 先顯示 11/06 – 11/12，按「今天」後回到 10/23 – 10/29

#### Scenario: 收合

- **WHEN** 使用者按「收合」後重新整理頁面
- **THEN** 行事曆 SHALL 只顯示標題列與「展開」按鈕

<!-- @trace
source: go-event-calendar
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - gas/Styles.html
tests:
  - tests/gas/app.js
  - tests/gas/app.test.js
-->
