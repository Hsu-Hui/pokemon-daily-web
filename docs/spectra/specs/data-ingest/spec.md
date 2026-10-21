# data-ingest Specification

## Purpose

Apps Script 網頁應用程式接收每日 payload、驗證密碼，並與試算表裡的既有資料合併、套用保留期限。對應 `gas/Code.gs` 的 `doPost`、`mergeTimed_`、`mergeFresh_`、`readRows_`、`writeRows_`、`setup`。

## Requirements

### Requirement: Secret check

`doPost` SHALL 比對 body 的 `secret` 與 Script Properties 的 `INGEST_SECRET`；沒有設定密碼或不相符時 SHALL 回應 `{"ok": false, "error": "bad secret"}` 且不寫入任何資料。

#### Scenario: Wrong secret

- **WHEN** 有人用錯誤密碼 POST 到接收資料網址
- **THEN** 回應 SHALL 為 `ok: false`，試算表不變

### Requirement: Sheet storage

資料 SHALL 存在同一個試算表的分頁：活動、任務、商品、新聞、已看過、狀態，第一列為欄位名稱並凍結；`tasks` 與 `others` 欄位 SHALL 以 JSON 字串儲存。寫入時 SHALL 先把儲存格設為純文字格式，避免日期與價格被自動轉換。寫入期間 SHALL 取得 script lock（最多等 30 秒）。

#### Scenario: Missing sheet

- **WHEN** 某個分頁不存在
- **THEN** 系統 SHALL 自動建立並寫入粗體標題列

### Requirement: Timed merge for events and tasks

活動與任務組 SHALL 以新資料覆蓋，`firstSeen` 沿用既有值（新項目為當下時間）；不在新資料裡、有結束時間、且結束未滿 30 天（`KEEP_ARCHIVE_DAYS`）的舊項目 SHALL 保留給封存頁，其餘移除。

#### Scenario: Event disappears from source

- **WHEN** 某活動昨天還在、今天不在 payload，且 10 天前結束
- **THEN** 該活動 SHALL 仍保留在活動分頁

### Requirement: Fresh merge for products and news

商品與新聞 SHALL 只新增第一次看到的項目（不在現有資料、也不在「已看過」中），`firstSeen` 設為當下時間；`firstSeen` 超過 7 天（`KEEP_PRODUCT_DAYS`、`KEEP_NEWS_DAYS`）的項目 SHALL 移除。「已看過」SHALL 記住項目 120 天（`KEEP_SEEN_DAYS`），避免過期刪掉後隔天又被當成新的。

#### Scenario: Product reappears after expiry

- **WHEN** 一件 8 天前首次出現、已被移除的商品今天又出現在 payload
- **THEN** 該商品 SHALL 不被重新加入

### Requirement: Run metadata

每次接收 SHALL 在「狀態」分頁寫入 `updatedAt`（payload 的 `generatedAt`）與 `errors`（以「、」連接），並回應 `ok: true` 與各類筆數。

#### Scenario: Successful ingest

- **WHEN** 密碼正確且合併完成
- **THEN** 回應 SHALL 為 `{"ok": true, "events": n, "tasks": n, "products": n, "news": n}`

### Requirement: One-time setup

`setup` SHALL 建立所有分頁、在沒有 `INGEST_SECRET` 時產生一組 32 字元的隨機密碼並寫入執行記錄，並把 `remindTasks` 每小時觸發器重建為恰好一個。

#### Scenario: Setup run twice

- **WHEN** 再次執行 `setup`
- **THEN** 既有密碼 SHALL 不變，`remindTasks` 觸發器 SHALL 仍只有一個
