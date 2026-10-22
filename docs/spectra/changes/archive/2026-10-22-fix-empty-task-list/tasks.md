## 1. 任務 id

- [x] 1.1 實作「用雜湊產生固定任務 id」：`sources.task_id(*parts)`，`TaskGroup.tasks` 改成（id、文字、獎勵）；巴哈任務使用 `task_id(text)`（擷取任務行、每個人的勾選紀錄）。驗證：單元測試確認同樣文字得到同樣 id，且 `build_tasks` 輸出的每個任務都有 `id`。

## 2. 巴哈解析

- [x] 2.1 實作「巴哈含年份的期間」（期間解析），並略過以 。／！ 結尾的行（擷取任務行）。驗證：單元測試 `test_full_date_period` 和使用精簡公告頁的 `test_announcement_post_has_no_tasks`；文章採用條件的既有測試不受影響。[after: 1.1]

## 3. LeekDuck 活動限時調查

- [x] 3.1 實作「以 LeekDuck 活動頁作為限時調查來源」：`parse_event_research` 和 `fetch_event_research`，只讀進行中活動頁，最多 20 頁（進行中活動頁、解析調查步驟）。驗證：針對 `tests/fixtures/leekduck_timed_research.html`（任務和獎勵）與 `tests/fixtures/leekduck_no_research.html`（不產生任務組）的單元測試，以及模擬讀取時略過未來活動的測試。[after: 1.1]
- [x] 3.2 實作「活動限時調查任務組的格式」（活動限時調查任務組）：任務組 id／名稱／網址／期間、翻譯後的文字、使用 `items` 對照表的 `translate.reward`，以及 `main.collect` 中巴哈 → LeekDuck → 田野調查的順序。驗證：範例表（`轉動 10 個補給站或道館`／`蔓莓果 ×5`）和任務組順序的單元測試。[after: 3.1]
