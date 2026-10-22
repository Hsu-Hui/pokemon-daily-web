## 背景

任務組來自每月田野調查（ScrapedDuck `research.min.json`）和巴哈【情報】文。2026-10-21 的資料顯示巴哈從來沒有產生任務組，所以頁面上除了田野調查之外等於是空的。ScrapedDuck 的 `events.min.json` 沒有調查任務，但每個活動的 `link` 都連到 LeekDuck 活動頁，上面有結構化的調查步驟。

## 目標／不做的事

**目標：**

- 任務待辦顯示進行中活動的限時／特別調查。
- 修正巴哈含年份日期的期間解析，說明句子不再變成任務。
- 每個任務都有固定 id。

**不做的事：**

- 不讀還沒開始或已經結束的活動的 LeekDuck 頁面。
- 不翻譯所有道具名稱；對不到的獎勵保留英文。

## 決策

### 以 LeekDuck 活動頁作為限時調查來源

`fetch_event_research(events, now)` 對 `start <= now < end`（或沒有開始時間）且類型不在 `GO_SKIP_TYPES` 的活動讀取其 `link`，最多 `LEEKDUCK_MAX_PAGES = 20` 頁，一次一個請求。`parse_event_research(html)` 讀 `.special-research-list .step-item`；每個 `.task-reward` 取 `.task-text` 和 `.reward-label`（含 `×N` 數量）。單頁失敗只印出紀錄並略過。放棄的做法：放寬巴哈標題條件——那些文章根本沒有任務清單。

### 活動限時調查任務組的格式

任務組 `id = "ld-<eventID>"`，`name = "限時調查：<event_name(name)>"`，`url = link`，期間沿用活動，最多 40 項。每個任務：`text = research_task(英文)`，`reward` = 翻譯後的獎勵以「、」連接（`translate.reward`：寶可夢用 `pokemon()`，道具查 `translations.json` 的 `items`，保留 `×N`），`id = task_id(step, 英文, n)`。

### 用雜湊產生固定任務 id

`task_id(*parts)` 回傳各部分以 `|` 連接後 SHA-1 的前 10 個十六進位字元。巴哈任務用 `task_id(text)`，LeekDuck 任務用 `task_id(步驟名稱, text, n)`，`n` 是同一步驟裡同樣文字第幾次出現（LeekDuck 會列出例如四個一樣的「Use a Star Piece」）。頁面原本就用 `t.id || i` 當 key，所以頁面不用改；巴哈舊的依順序勾選紀錄會失效一次，因為巴哈從沒產生過任務組，可以接受。

### 巴哈含年份的期間

`parse_period` 先試 `YYYY年M月D日[ HH:MM] ～ [YYYY年]M月D日[ HH:MM]`（也接受 `/` 分隔）；符合就直接使用，不做 180 天的年份推測。否則沿用原本的月/日規則。以「。」或「！」結尾的行不是任務。

## 實作約定

- 行為：`payload.taskGroups` = 巴哈任務組 + LeekDuck 活動限時調查組 + 田野調查組；每個任務都有 `id`、`text`、`reward`。
- 介面：`sources.fetch_event_research(events, now) -> list[tuple[GoEvent, steps]]`（翻譯成任務組在 `main.build_event_research`）、`sources.parse_event_research(html) -> list[tuple[str, str, list[str]]]`（步驟、任務、獎勵）、`translate.reward(label) -> str`、`sources.task_id(*parts) -> str`；`TaskGroup.tasks` 改成 `list[tuple[str, str, str]]`（id、文字、獎勵）。
- 失敗情況：LeekDuck 單頁失敗 → 印出紀錄並略過；整個來源失敗 → 和其他來源一樣記成錯誤 `LeekDuck 限時調查（原因）`。
- 驗收：測試用頁面的單元測試、`parse_period` 含年份測試、巴哈公告測試頁回傳 `None`；`python -m unittest` 通過。
- 範圍：包含以上項目；不包含看板和提醒的修改。

## 風險與取捨

- [LeekDuck 改版面] → 解析不到任務就略過該組；測試頁面讓問題會在測試裡出現。
- [每天最多多 20 個 LeekDuck 請求] → 依序送出，用現有的 User-Agent 和 30 秒逾時；只讀進行中的活動。
- [巴哈舊的依順序勾選紀錄失效一次] → 接受，原因見上面的決策。
