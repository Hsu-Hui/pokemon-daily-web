# data-ingest Specification

## Purpose

Apps Script 網頁應用程式接收每日 payload、驗證密碼，並與試算表裡的既有資料合併、套用保留期限。對應 `gas/Code.gs` 的 `doPost`、`mergeTimed_`、`mergeFresh_`、`readRows_`、`writeRows_`、`setup`。

## Requirements

### Requirement: 密碼檢查

`doPost` SHALL 比對 body 的 `secret` 與 Script Properties 的 `INGEST_SECRET`；沒有設定密碼或不相符時 SHALL 回應 `{"ok": false, "error": "bad secret"}` 且不寫入任何資料。body 不是合法 JSON 或處理過程丟出例外時，SHALL 回應 `{"ok": false, "error": <錯誤訊息>}` 的 JSON，不回傳 Apps Script 錯誤頁。

#### Scenario: 密碼錯誤

- **WHEN** 有人用錯誤密碼 POST 到接收資料網址
- **THEN** 回應 SHALL 為 `ok: false`，試算表不變

#### Scenario: 格式錯誤的內容

- **WHEN** POST 的內容不是 JSON
- **THEN** 回應 SHALL 為 JSON `{"ok": false, "error": ...}`，試算表不變

---
### Requirement: 試算表儲存

資料 SHALL 存在同一個試算表的分頁：活動、任務、商品、新聞、已看過、狀態，第一列為欄位名稱並凍結；商品分頁 SHALL 包含 `media` 欄位；`tasks` 與 `others` 欄位 SHALL 以 JSON 字串儲存。寫入時 SHALL 先把儲存格設為純文字格式，避免日期與價格被自動轉換。寫入期間 SHALL 取得 script lock（最多等 30 秒）。保留天數 SHALL 讀取共用設定 `shared/board.json`（Apps Script 端為產生的 `BOARD`）。

#### Scenario: 缺少分頁

- **WHEN** 某個分頁不存在
- **THEN** 系統 SHALL 自動建立並寫入粗體標題列

#### Scenario: 新增欄位

- **WHEN** 既有商品分頁沒有 `media` 欄
- **THEN** 下一次寫入 SHALL 更新標題列並寫入 `media`

---
### Requirement: 活動與任務的覆蓋合併

活動與任務組 SHALL 以新資料覆蓋，`firstSeen` 沿用既有值（新項目為當下時間）；不在新資料裡、有結束時間、且結束未滿 30 天（`KEEP_ARCHIVE_DAYS`）的舊項目 SHALL 保留給封存頁，其餘移除。

#### Scenario: 活動從來源消失

- **WHEN** 某活動昨天還在、今天不在 payload，且 10 天前結束
- **THEN** 該活動 SHALL 仍保留在活動分頁

---
### Requirement: 商品與新聞的新增合併

商品與新聞 SHALL 只新增第一次看到的項目（不在現有資料、也不在「已看過」中），`firstSeen` 設為當下時間；`firstSeen` 超過 7 天（`KEEP_PRODUCT_DAYS`、`KEEP_NEWS_DAYS`）的項目 SHALL 移除。「已看過」SHALL 記住項目 120 天（`KEEP_SEEN_DAYS`），避免過期刪掉後隔天又被當成新的。

#### Scenario: 過期商品又出現

- **WHEN** 一件 8 天前首次出現、已被移除的商品今天又出現在 payload
- **THEN** 該商品 SHALL 不被重新加入

---
### Requirement: 執行紀錄

每次接收 SHALL 在「狀態」分頁寫入 `updatedAt`（payload 的 `generatedAt`）與 `errors`（以「、」連接），並回應 `ok: true` 與各類筆數。

#### Scenario: 接收成功

- **WHEN** 密碼正確且合併完成
- **THEN** 回應 SHALL 為 `{"ok": true, "events": n, "tasks": n, "products": n, "news": n}`

---
### Requirement: 第一次設定

`setup` SHALL 建立所有分頁、在沒有 `INGEST_SECRET` 時產生一組 32 字元的隨機密碼並寫入執行記錄，並把 `remindTasks` 每小時觸發器重建為恰好一個。

#### Scenario: 重複執行 setup

- **WHEN** 再次執行 `setup`
- **THEN** 既有密碼 SHALL 不變，`remindTasks` 觸發器 SHALL 仍只有一個
