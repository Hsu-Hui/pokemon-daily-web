# event-research Specification

## Purpose

把 LeekDuck 活動頁上列出的限時調查與特別調查，整理成進行中 Pokémon GO 活動的任務組，讓任務待辦不只有每月的田野調查。

## Requirements

### Requirement: 進行中活動頁

系統 SHALL 對目前進行中（已開始或沒有開始時間、尚未結束）且類型不在 `GO_SKIP_TYPES` 的活動讀取其 LeekDuck 活動頁（ScrapedDuck 的 `link`），每天最多 20 頁；單頁讀取失敗 SHALL 只略過該頁。

#### Scenario: 未來的活動

- **WHEN** 活動 3 天後才開始
- **THEN** 系統 SHALL 不讀取該活動頁

---
### Requirement: 解析調查步驟

系統 SHALL 從活動頁的 `.special-research-list .step-item` 讀取每一步的名稱（`.step-name`）與任務（`.task-reward` 的 `.task-text`、`.reward-label`）。頁面沒有限時調查時 SHALL 不輸出任務組。

#### Scenario: 有限時調查的活動頁

- **WHEN** 活動頁有「adidas Timed Research (1/3)」一步，任務為「Spin 10 PokéStops or Gyms」獎勵「Razz Berry ×5」
- **THEN** 系統 SHALL 擷取該任務與獎勵

#### Scenario: 沒有限時調查的活動頁

- **WHEN** 活動頁的限時調查清單是空的
- **THEN** 該活動 SHALL 不產生任務組

---
### Requirement: 活動限時調查任務組

每個有任務的活動 SHALL 產生一個任務組：`id` 為 `ld-<活動id>`，名稱為 `限時調查：<中文活動名>`，`url` 為活動頁，開始與結束沿用活動，最多 40 項。每個任務 SHALL 有 `id`（步驟名稱、英文任務與該任務在同一步驟第幾次出現的雜湊，重複的任務 id 也不同）、翻譯後的 `text`，以及 `reward`：獎勵翻成中文（寶可夢查字典、道具查 `translations.json` 的 `items`，保留 ×數量，對不到保留英文）並以「、」連接。

##### Example: 任務翻譯

| 英文任務 | 英文獎勵 | text | reward |
| -------- | -------- | ---- | ------ |
| Spin 10 PokéStops or Gyms | Razz Berry ×5 | 轉動 10 個補給站或道館 | 蔓莓果 ×5 |
| Catch 20 Pokémon | Incense ×3 | 捕捉 20 隻寶可夢 | 薰香 ×3 |

#### Scenario: 任務組順序

- **WHEN** 爬蟲輸出任務組
- **THEN** 順序 SHALL 為巴哈任務組、LeekDuck 限時調查組、田野調查組
