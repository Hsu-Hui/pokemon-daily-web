## MODIFIED Requirements

### Requirement: Six categories

活動分類 SHALL 只有「聚焦時刻」「極巨化/超極巨化」「團體戰/超級團體戰」「GO Pass」「限時調查」「其他」，順序與每類的關鍵字定義在 `shared/board.json` 的 `categories`。系統 SHALL 先依 `eventType` 對照表決定分類；對不到時，SHALL 依分類順序檢查英文原名與翻譯後的中文名稱是否包含該分類任一關鍵字（英文不分大小寫），取第一個符合的分類；都不符合時為「其他」。預設關鍵字：

| 分類 | 關鍵字 |
| ---- | ------ |
| 聚焦時刻 | Spotlight Hour、聚焦時刻 |
| 極巨化/超極巨化 | Max Battle、Max Monday、Dynamax、Gigantamax、極巨 |
| 團體戰/超級團體戰 | Raid、團體戰 |
| GO Pass | GO Pass |
| 限時調查 | Timed Research、Special Research、Limited Research、限時調查、特別調查 |

#### Scenario: Unknown type with raid in name

- **WHEN** `eventType` 為 `event` 且名稱含 `Raid`
- **THEN** `category` SHALL 為「團體戰/超級團體戰」

#### Scenario: Keyword in name

- **WHEN** 活動的 `eventType` 沒有對照，名稱含某分類的關鍵字
- **THEN** 活動 SHALL 歸到該分類

##### Example: Event names

| eventType | 名稱 | 分類 | 原因 |
| --------- | ---- | ---- | ---- |
| event | Dynamax Trails | 極巨化/超極巨化 | 名稱含 Dynamax |
| event | GO Pass: Halloween | GO Pass | 名稱含 GO Pass |
| event | Halloween 2026 Timed Research | 限時調查 | 名稱含 Timed Research |
| event | Shadow Raid Weekend | 團體戰/超級團體戰 | 名稱含 Raid |
| event | Fall Marathon: Buddy Trek | 其他 | 沒有關鍵字 |
| raid-day | Chandelure Super Mega Raid Day | 團體戰/超級團體戰 | eventType 對照 |
| community-day | November Community Day | 其他 | eventType 沒有對照，名稱也沒有關鍵字 |

#### Scenario: Add a keyword

- **WHEN** 在 `shared/board.json` 的「聚焦時刻」加上關鍵字「Hour」並重新產生 `gas/Board.gs`
- **THEN** 隔天名稱含 Hour 且 eventType 沒有對照的活動 SHALL 歸到「聚焦時刻」
