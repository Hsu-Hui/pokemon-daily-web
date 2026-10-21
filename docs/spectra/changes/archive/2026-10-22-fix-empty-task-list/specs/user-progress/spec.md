## MODIFIED Requirements

### Requirement: Per-user state

勾選紀錄 SHALL 以 JSON 存在 Apps Script UserProperties 的 `state`，包含 `done`（活動 id）、`taskDone`（`<任務組id>#<任務id>`；任務沒有 id 時才用項目順序）與 `gaveUp`（任務組 id）。不同 Google 帳號的紀錄 SHALL 互不影響，同一帳號在不同裝置 SHALL 同步。

#### Scenario: Two users

- **WHEN** 使用者 A 勾選某活動完成
- **THEN** 使用者 B 的看板 SHALL 不受影響

#### Scenario: Task order changes

- **WHEN** 巴哈文章被編輯、任務順序改變
- **THEN** 已勾選的任務 SHALL 仍然對應同一段任務文字
