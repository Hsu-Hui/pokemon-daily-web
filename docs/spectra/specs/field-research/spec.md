# field-research Specification

## Purpose

把目前的田野調查任務（ScrapedDuck `research.min.json`）整理成一個任務組，翻成中文並給定期限。對應 `scraper/sources/` 的 `fetch_field_research` 與 `scraper/main.py` 的 `build_field_research`。

## Requirements

### Requirement: 讀取田野調查

系統 SHALL 從 `GO_RESEARCH_URL` 讀取田野調查，去掉任務文字裡的 HTML 標籤，保留有名稱的獎勵；任務文字為空的項目 SHALL 略過。

#### Scenario: 任務含 HTML

- **WHEN** 任務文字為 `<b>Catch 5</b> Pokémon`
- **THEN** 系統 SHALL 以 `Catch 5 Pokémon` 處理

### Requirement: 單一田野調查任務組

有任何田野調查時，系統 SHALL 輸出恰好一個任務組；沒有時 SHALL 不輸出任務組。

#### Scenario: 有專屬田野調查的活動進行中

- **WHEN** 有已開始、尚未結束、且 `hasFieldResearchTasks` 為真的活動
- **THEN** 任務組 SHALL 以其中最早結束的活動為準：id 為 `field-<活動id>`，名稱為 `田野調查：<活動中文名>`，開始與結束沿用該活動

#### Scenario: 沒有進行中的活動

- **WHEN** 沒有符合條件的活動
- **THEN** 任務組 id SHALL 為 `field-YYYYMM`，名稱為 `<月> 月田野調查`，期限為當月 1 日 00:00 到月底最後一分鐘（台灣時間）

### Requirement: 田野調查任務項目

每個任務 SHALL 有 `id`（英文任務文字轉小寫、非英數字換成 `-`）、翻譯後的 `text`，以及 `reward`：最多 6 個獎勵翻成中文後以「、」連接並加上「遇見 」前綴，沒有獎勵時為空字串。任務組的 `url` SHALL 為 `https://leekduck.com/research/`。

#### Scenario: 任務 id 每天相同

- **WHEN** 同一個英文任務隔天再次出現
- **THEN** 任務 `id` SHALL 相同，使用者的勾選紀錄因此保留
