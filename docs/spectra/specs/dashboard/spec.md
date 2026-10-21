# dashboard Specification

## Purpose

Apps Script 提供的看板網頁，顯示活動、任務、新商品、台灣活動與封存。對應 `gas/Code.gs` 的 `doGet`、`getData` 與 `gas/Index.html`。

## Requirements

### Requirement: Page access

`doGet` SHALL 只在能取得登入者 email 時回傳看板（標題「寶可夢每日看板」、行動版 viewport）；取不到登入者（接收資料用的匿名部署）時 SHALL 只顯示「請用看板的網址開啟。」。

#### Scenario: Opened through ingest URL

- **WHEN** 有人用接收資料的網址打開
- **THEN** 頁面 SHALL 不顯示任何資料

### Requirement: Data loading

看板 SHALL 一次透過 `getData` 取得 `updatedAt`、`errors`、活動、任務、商品、新聞與目前使用者的勾選狀態；有 `updatedAt` 時顯示「最後更新 <時間>」，否則顯示「還沒有資料，等每日排程跑過一次」；載入失敗時顯示錯誤訊息。所有時間 SHALL 以台灣時區顯示。

#### Scenario: Source errors today

- **WHEN** `errors` 不為空
- **THEN** 總覽頁 SHALL 顯示「今天這些來源抓取失敗：…」

### Requirement: Tabs

看板 SHALL 有六個分頁：總覽、GO 活動、任務待辦、新商品、台灣活動、封存；目前分頁 SHALL 記在瀏覽器 localStorage，下次開啟沿用。

#### Scenario: Overview content

- **WHEN** 使用者在總覽頁
- **THEN** 頁面 SHALL 顯示未完成且已開始的活動數、24 小時內結束的活動數、任務進度（完成項/全部項）、今天新商品數，「快結束了，還沒完成」清單（任務：結束前 4 小時內且未全部完成；活動：24 小時內結束），以及最多 8 件今天新上架商品

### Requirement: GO events tab

GO 活動頁 SHALL 只列未完成且未結束的活動，提供六大分類的多選篩選（「全部」代表不篩選，並顯示每類數量），寬螢幕用表格、窄螢幕用卡片，顯示剩餘時間與進度條；不在六大分類的活動 SHALL 歸到「其他」。

#### Scenario: Multi-select categories

- **WHEN** 使用者選了「聚焦時刻」和「GO Pass」
- **THEN** 列表 SHALL 只顯示這兩類活動，按「全部」SHALL 清除篩選

#### Scenario: Default and custom sorting

- **WHEN** 使用者沒有點排序
- **THEN** 活動 SHALL 依類型（六大分類順序）→ 開始 → 結束排序；點類型/開始/結束 SHALL 以該欄優先排序，再點一次反向

### Requirement: Tasks tab

任務待辦頁 SHALL 列出未放棄且未結束的任務組，依剩餘時間由少到多排序，每組顯示期間、剩餘時間、完成數、進度條、每個任務的勾選框與獎勵（沒有獎勵時顯示連到原文的「見原文」），以及「放棄」按鈕。

#### Scenario: Give up a group

- **WHEN** 使用者按「放棄」
- **THEN** 該任務組 SHALL 移到封存頁且不再提醒

### Requirement: Products tab

新商品頁 SHALL 合併 PChome 商品與 `kind` 為 `product` 的新聞（來源為「官網」或「寶可夢中心」，價格顯示「看消息」），提供 PChome/寶可夢中心/官網的多選來源篩選與排序（上架時間新到舊（預設）、舊到新、價格高到低、低到高；沒有價格的排最後）。首次出現未滿 24 小時的商品 SHALL 標示 NEW。

#### Scenario: Sort by price

- **WHEN** 使用者選「價格：低到高」
- **THEN** 有價格的商品 SHALL 由低到高排列，沒有價格的排在最後

### Requirement: Taiwan news tab

台灣活動頁 SHALL 列出 `kind` 為 `event` 的新聞，依發布時間（沒有時用 `firstSeen`）新到舊排序，並顯示「另有 N 家報導」。

#### Scenario: Merged coverage

- **WHEN** 一則新聞的 `others` 有 2 家媒體
- **THEN** 該則 SHALL 顯示「另有 2 家報導」

### Requirement: Archive tab

封存頁 SHALL 列出已放棄或已結束的任務組，以及已完成或已結束的活動，並註明原因；尚未結束的已放棄任務組與已完成活動 SHALL 提供「復原」按鈕。

#### Scenario: Restore a done event

- **WHEN** 使用者在封存頁對尚未結束的已完成活動按「復原」
- **THEN** 該活動 SHALL 回到 GO 活動頁

### Requirement: Pagination

GO 活動、任務待辦、新商品、台灣活動、封存的列表 SHALL 每頁最多 25 筆，超過時顯示分頁列（第一頁、最後一頁、目前頁前後 2 頁，其餘以…省略）與總筆數；改變篩選或排序時 SHALL 回到第 1 頁。

#### Scenario: 30 products

- **WHEN** 有 30 件商品
- **THEN** 第 1 頁 SHALL 顯示 25 件，第 2 頁顯示 5 件
