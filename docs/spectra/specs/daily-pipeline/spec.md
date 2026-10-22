# daily-pipeline Specification

## Purpose

每天自動抓取所有資料來源、整理成一份 JSON payload，送到 Apps Script 存進 Google 試算表。對應 `.github/workflows/daily.yml` 與 `scraper/main.py`（`collect`、`send`、`main`）。

## Requirements

### Requirement: 每日排程

系統 SHALL 由 GitHub Actions 在每天 UTC 17:00（台灣時間 01:00，cron `0 17 * * *`）執行爬蟲，並 SHALL 支援手動觸發（`workflow_dispatch`）。同一時間只允許一個執行（concurrency group `daily-board`，不取消進行中的執行）。

#### Scenario: 排程執行

- **WHEN** 時間到達 UTC 17:00
- **THEN** workflow SHALL 安裝 `requirements.txt`、執行 `python -m unittest`，再執行 `python -m scraper.main` 並帶入 `GAS_INGEST_URL` 與 `GAS_INGEST_SECRET`

#### Scenario: Pull request 檢查

- **WHEN** workflow 因 pull request 觸發
- **THEN** `GAS_INGEST_URL` SHALL 為空字串，只抓資料檢查來源，不送到 Apps Script

### Requirement: 來源失敗互不影響

每個資料來源 SHALL 獨立抓取；單一來源丟出例外時，系統 SHALL 以空清單取代該來源的結果、繼續處理其他來源，並把「來源名稱（原因）」加進 payload 的 `errors`。

#### Scenario: 單一來源失敗

- **WHEN** PChome 回應 HTTP 429
- **THEN** payload 的 `products` SHALL 為空，`errors` SHALL 包含 `PChome（請求次數過多被限制）`，其他來源照常輸出

#### Scenario: 錯誤原因對照

- **WHEN** 例外帶有 HTTP 回應
- **THEN** 原因 SHALL 依狀態碼對應為 401「需要登入」、403「被拒絕存取」、404「找不到頁面」、429「請求次數過多被限制」，其他狀態碼為 `HTTP <code>`；逾時為「連線逾時」，連線錯誤為「連不上」，其他為「資料格式不符」

### Requirement: 每日資料格式

payload SHALL 包含 `generatedAt`（台灣時區 ISO 時間）、`events`、`taskGroups`（巴哈任務組在前、田野調查組在後）、`products`、`news`（官網、寶可夢中心新聞、台灣活動新聞一起去重）與 `errors`。

#### Scenario: 寫入本機檔案

- **WHEN** 爬蟲執行完成
- **THEN** payload SHALL 寫入 `out/payload.json`（UTF-8、不轉義中文），並印出各類筆數與部分樣本

### Requirement: 送到 Apps Script

設定了 `GAS_INGEST_URL` 與 `GAS_INGEST_SECRET` 時，系統 SHALL 以 POST `{"secret": ..., "data": payload}` 送出（逾時 120 秒）；HTTP 錯誤或回應的 `ok` 不為真時 SHALL 讓執行失敗。

#### Scenario: 沒有接收資料設定

- **WHEN** 沒有設定 `GAS_INGEST_URL` 或 `GAS_INGEST_SECRET`
- **THEN** 系統 SHALL 只輸出 `out/payload.json` 並以 0 結束

#### Scenario: Apps Script 拒絕

- **WHEN** Apps Script 回應 `{"ok": false, ...}`
- **THEN** 系統 SHALL 丟出 `RuntimeError`，workflow 失敗

### Requirement: 除錯用資料

workflow SHALL 不論成功失敗都把 `out/payload.json` 上傳為名為 `payload` 的 artifact，保留 7 天。

#### Scenario: 抓完資料後失敗

- **WHEN** 送出資料的步驟失敗
- **THEN** `payload` artifact SHALL 仍然被上傳
