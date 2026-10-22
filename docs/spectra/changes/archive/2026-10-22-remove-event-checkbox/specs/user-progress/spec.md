## MODIFIED Requirements

### Requirement: 每個人的勾選紀錄

勾選紀錄 SHALL 以 JSON 存在 Apps Script UserProperties 的 `state`，包含 `taskDone`（`<任務組id>#<任務id>`；任務沒有 id 時才用項目順序）與 `gaveUp`（任務組 id）。舊版留下的 `done`（活動完成）紀錄 SHALL 被忽略。不同 Google 帳號的紀錄 SHALL 互不影響，同一帳號在不同裝置 SHALL 同步。

#### Scenario: 兩個使用者

- **WHEN** 使用者 A 勾選某任務完成
- **THEN** 使用者 B 的看板 SHALL 不受影響

#### Scenario: 任務順序改變

- **WHEN** 巴哈文章被編輯、任務順序改變
- **THEN** 已勾選的任務 SHALL 仍然對應同一段任務文字

### Requirement: 設定勾選

`setFlag(kind, id, value)` SHALL 只接受 `taskDone`、`gaveUp`，其他值（包含 `done`）丟出錯誤；`value` 為真時設定、為假時刪除該 id，期間取得 user lock（最多等 10 秒），並回傳最新狀態。

#### Scenario: 不合法的種類

- **WHEN** 呼叫 `setFlag('done', ...)`
- **THEN** 系統 SHALL 丟出 `bad kind`

### Requirement: 狀態判斷

活動在已結束時 SHALL 視為封存；任務組在已放棄或已結束時 SHALL 視為封存。任務組「快結束」的條件 SHALL 為剩餘時間大於 0、小於 4 小時、且尚未全部完成；活動「快結束」為剩餘時間小於 24 小時且已開始。

#### Scenario: 任務全部完成

- **WHEN** 任務組所有項目都勾選完成
- **THEN** 該組 SHALL 顯示「全部完成」且不算快結束

#### Scenario: 舊的完成紀錄

- **WHEN** UserProperties 裡還有某活動的 `done` 紀錄而活動尚未結束
- **THEN** 該活動 SHALL 仍顯示在 GO 活動頁
