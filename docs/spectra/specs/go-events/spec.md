# go-events Specification

## Purpose

從 ScrapedDuck（LeekDuck 資料）取得 Pokémon GO 活動，篩出進行中和即將開始的活動，翻成中文並分類。對應 `scraper/sources/` 的 `fetch_go_events`、`parse_time` 與 `scraper/main.py` 的 `build_events`。

## Requirements

### Requirement: 讀取活動

系統 SHALL 從 `GO_EVENTS_URL`（ScrapedDuck `events.min.json`）讀取活動，每筆保留 `eventID`、名稱、heading、`eventType`、連結、開始、結束，以及 `extraData.generic.hasFieldResearchTasks`（活動期間是否有專屬田野調查）。

#### Scenario: 沒有時區的時間

- **WHEN** 活動時間字串沒有時區
- **THEN** 系統 SHALL 視為台灣時間（Asia/Taipei）；有時區（含 `Z`）的時間 SHALL 轉成台灣時間

---
### Requirement: 活動篩選

系統 SHALL 排除 `eventType` 為 `season` 或 `go-battle-league` 的活動、已結束的活動，以及開始時間在 14 天（`GO_LOOKAHEAD_DAYS`）之後的活動。

#### Scenario: 太久以後的活動

- **WHEN** 活動開始時間是 20 天後
- **THEN** 該活動 SHALL 不出現在 payload 的 `events`

#### Scenario: 沒有結束時間的活動

- **WHEN** 活動沒有結束時間且已開始
- **THEN** 該活動 SHALL 保留

---
### Requirement: 活動輸出欄位

每筆輸出的活動 SHALL 包含 `id`、翻譯後的 `name`、中文 `type`（依 `TYPE_LABELS`，對不到時用 heading）、`category`（六大分類之一）、`url`、`start`、`end`（ISO 字串或 null）。

#### Scenario: 聚焦時刻

- **WHEN** 活動 `eventType` 為 `pokemon-spotlight-hour`
- **THEN** `type` SHALL 為「聚焦時刻」，`category` SHALL 為「聚焦時刻」

---
### Requirement: 六大分類

活動分類 SHALL 只有「聚焦時刻」「極巨化/超極巨化」「團體戰/超級團體戰」「GO Pass」「限時調查」「其他」，順序與每類的關鍵字定義在 `shared/board.json` 的 `categories`。系統 SHALL 先依 `eventType` 對照表決定分類；對不到時，SHALL 依分類順序檢查英文原名與翻譯後的中文名稱是否包含該分類任一關鍵字（英文不分大小寫），取第一個符合的分類；都不符合時為「其他」。預設關鍵字：

| 分類 | 關鍵字 |
| ---- | ------ |
| 聚焦時刻 | Spotlight Hour、聚焦時刻 |
| 極巨化/超極巨化 | Max Battle、Max Monday、Dynamax、Gigantamax、極巨 |
| 團體戰/超級團體戰 | Raid、團體戰 |
| GO Pass | GO Pass |
| 限時調查 | Timed Research、Special Research、Limited Research、限時調查、特別調查 |

#### Scenario: 類型對不到但名稱有 Raid

- **WHEN** `eventType` 為 `event` 且名稱含 `Raid`
- **THEN** `category` SHALL 為「團體戰/超級團體戰」

#### Scenario: 名稱含關鍵字

- **WHEN** 活動的 `eventType` 沒有對照，名稱含某分類的關鍵字
- **THEN** 活動 SHALL 歸到該分類

##### Example: 活動名稱

| eventType | 名稱 | 分類 | 原因 |
| --------- | ---- | ---- | ---- |
| event | Dynamax Trails | 極巨化/超極巨化 | 名稱含 Dynamax |
| event | GO Pass: Halloween | GO Pass | 名稱含 GO Pass |
| event | Halloween 2026 Timed Research | 限時調查 | 名稱含 Timed Research |
| event | Shadow Raid Weekend | 團體戰/超級團體戰 | 名稱含 Raid |
| event | Fall Marathon: Buddy Trek | 其他 | 沒有關鍵字 |
| raid-day | Chandelure Super Mega Raid Day | 團體戰/超級團體戰 | eventType 對照 |
| community-day | November Community Day | 其他 | eventType 沒有對照，名稱也沒有關鍵字 |

#### Scenario: 新增關鍵字

- **WHEN** 在 `shared/board.json` 的「聚焦時刻」加上關鍵字「Hour」並重新產生 `gas/Board.gs`
- **THEN** 隔天名稱含 Hour 且 eventType 沒有對照的活動 SHALL 歸到「聚焦時刻」
