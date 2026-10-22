## MODIFIED Requirements

### Requirement: 密碼檢查

`doPost` SHALL 比對 body 的 `secret` 與 Script Properties 的 `INGEST_SECRET`；沒有設定密碼或不相符時 SHALL 回應 `{"ok": false, "error": "bad secret"}` 且不寫入任何資料。body 不是合法 JSON 或處理過程丟出例外時，SHALL 回應 `{"ok": false, "error": <錯誤訊息>}` 的 JSON，不回傳 Apps Script 錯誤頁。

#### Scenario: 密碼錯誤

- **WHEN** 有人用錯誤密碼 POST 到接收資料網址
- **THEN** 回應 SHALL 為 `ok: false`，試算表不變

#### Scenario: 格式錯誤的內容

- **WHEN** POST 的內容不是 JSON
- **THEN** 回應 SHALL 為 JSON `{"ok": false, "error": ...}`，試算表不變

### Requirement: 試算表儲存

資料 SHALL 存在同一個試算表的分頁：活動、任務、商品、新聞、已看過、狀態，第一列為欄位名稱並凍結；商品分頁 SHALL 包含 `media` 欄位；`tasks` 與 `others` 欄位 SHALL 以 JSON 字串儲存。寫入時 SHALL 先把儲存格設為純文字格式，避免日期與價格被自動轉換。寫入期間 SHALL 取得 script lock（最多等 30 秒）。保留天數 SHALL 讀取共用設定 `shared/board.json`（Apps Script 端為產生的 `BOARD`）。

#### Scenario: 缺少分頁

- **WHEN** 某個分頁不存在
- **THEN** 系統 SHALL 自動建立並寫入粗體標題列

#### Scenario: 新增欄位

- **WHEN** 既有商品分頁沒有 `media` 欄
- **THEN** 下一次寫入 SHALL 更新標題列並寫入 `media`
