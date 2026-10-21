# bahamut-tasks Specification

## Purpose

從巴哈姆特 Pokémon GO 哈啦板（bsn 29659）的【情報】文章擷取限時調查的任務、獎勵和期間。對應 `scraper/sources.py` 的 `fetch_bahamut_tasks`、`parse_bahamut_list`、`parse_bahamut_post`、`parse_tasks`、`parse_period`。

## Requirements

### Requirement: Post discovery

系統 SHALL 讀取看板列表前 2 頁（`BAHAMUT_PAGES`），只收標題前 6 個字含「情報」且標題含「調查」「任務」「課題」其中之一的文章，依 `snA` 去重，最多讀 15 篇（`BAHAMUT_MAX_POSTS`）。

#### Scenario: Non-intel post

- **WHEN** 文章標題為「【心得】田野調查心得」
- **THEN** 該文章 SHALL 不被讀取

### Requirement: Task line extraction

系統 SHALL 把文章內文逐行處理：去掉條列符號後，長度不超過 80 字、含任務動詞（捕捉、轉動、孵化、使用、完成…）的行當作任務；箭頭（→、->、➔ 等）或「獎勵：」之後是獎勵。沒有獎勵也沒有數字的行 SHALL 視為說明文字略過。每篇最多 40 項。

#### Scenario: Task with arrow reward

- **WHEN** 內文有一行「・捕捉 5 隻寶可夢 → 星塵 x500」
- **THEN** 系統 SHALL 擷取任務「捕捉 5 隻寶可夢」與獎勵「星塵 x500」

#### Scenario: Missing reward

- **WHEN** 任務行有數字但沒有獎勵分隔符號
- **THEN** 任務 SHALL 保留，獎勵為空字串（看板顯示「見原文」）

### Requirement: Period parsing

系統 SHALL 從內文解析第一個「月/日 [時:分] ~ [月/日] [時:分]」的期間；沒有開始時間時為 00:00、沒有結束時間時為 23:59，只有結束時刻時沿用開始日期。年份以文章編輯時間為準；日期早於發文時間 180 天以上時 SHALL 視為隔年，結束早於開始時 SHALL 把結束改到隔年。

#### Scenario: Cross-year period

- **WHEN** 12 月的文章寫「12/30 ~ 1/5」
- **THEN** 結束時間 SHALL 為隔年 1 月 5 日 23:59

### Requirement: Post acceptance

系統 SHALL 只輸出有任務且有結束時間、且尚未結束的文章，任務組 id 為 `bh-<snA>`，名稱為去掉開頭【…】的文章標題，`url` 為文章網址。單篇文章讀取失敗 SHALL 只略過該篇。

#### Scenario: Pinned summary post

- **WHEN** 文章有任務行但沒有可解析的期間
- **THEN** 該文章 SHALL 不輸出任務組

#### Scenario: Bahamut task has no id

- **WHEN** 巴哈任務組輸出
- **THEN** 每個任務 SHALL 只有 `text` 與 `reward`，沒有 `id`（勾選紀錄以項目順序識別）
