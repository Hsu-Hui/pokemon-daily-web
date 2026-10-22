# user-progress Specification

## Purpose

每個使用者自己的完成、勾選與放棄紀錄。對應 `gas/Code.gs` 的 `loadState_`、`setFlag` 與 `gas/Index.html` 的 `setFlag`、`derive`。

## Requirements

### Requirement: 每個人的勾選紀錄

勾選紀錄 SHALL 以 JSON 存在 Apps Script UserProperties 的 `state`，包含 `taskDone`（`<任務組id>#<任務id>`；任務沒有 id 時才用項目順序）與 `gaveUp`（任務組 id）。舊版留下的 `done`（活動完成）紀錄 SHALL 被忽略。不同 Google 帳號的紀錄 SHALL 互不影響，同一帳號在不同裝置 SHALL 同步。

#### Scenario: 兩個使用者

- **WHEN** 使用者 A 勾選某任務完成
- **THEN** 使用者 B 的看板 SHALL 不受影響

#### Scenario: 任務順序改變

- **WHEN** 巴哈文章被編輯、任務順序改變
- **THEN** 已勾選的任務 SHALL 仍然對應同一段任務文字


<!-- @trace
source: remove-event-checkbox
updated: 2026-10-22
code:
  - gas/App.html
  - tests/gas/load.js
  - README.md
  - tests/gas/app.js
  - gas/Code.gs
  - gas/Styles.html
tests:
  - tests/gas/app.test.js
  - tests/gas/merge.test.js
-->

---
### Requirement: 設定勾選

`setFlag(kind, id, value)` SHALL 只接受 `taskDone`、`gaveUp`，其他值（包含 `done`）丟出錯誤；`value` 為真時設定、為假時刪除該 id，期間取得 user lock（最多等 10 秒），並回傳最新狀態。

#### Scenario: 不合法的種類

- **WHEN** 呼叫 `setFlag('done', ...)`
- **THEN** 系統 SHALL 丟出 `bad kind`


<!-- @trace
source: remove-event-checkbox
updated: 2026-10-22
code:
  - gas/App.html
  - tests/gas/load.js
  - README.md
  - tests/gas/app.js
  - gas/Code.gs
  - gas/Styles.html
tests:
  - tests/gas/app.test.js
  - tests/gas/merge.test.js
-->

---
### Requirement: 先更新畫面再儲存

網頁 SHALL 把任務勾選先套用在畫面的草稿上，按「儲存」時以 `saveTasks` 一次送出；成功後以回傳狀態取代畫面狀態並清空草稿，失敗時 SHALL 保留草稿並顯示「儲存失敗，請再試一次」。「放棄」「復原」仍 SHALL 先套用在畫面並立即以 `setFlag` 儲存，失敗時還原並顯示同樣提示。

#### Scenario: 儲存失敗

- **WHEN** `saveTasks` 呼叫失敗
- **THEN** 勾選 SHALL 維持草稿狀態並顯示提示


<!-- @trace
source: task-progress-save
updated: 2026-10-22
code:
  - .spectra.yaml
  - gas/Index.html
  - shared/board.json
  - tests/gas/app.js
  - gas/Styles.html
  - scraper/sources/pchome.py
  - gas/Board.gs
  - gas/App.html
  - scraper/sources/__init__.py
  - gas/Code.gs
  - tests/gas/load.js
  - README.md
  - scraper/main.py
tests:
  - tests/test_scraper.py
  - tests/gas/merge.test.js
  - tests/gas/app.test.js
-->

---
### Requirement: 狀態判斷

活動在已結束時 SHALL 視為封存；任務組在已放棄或已結束時 SHALL 視為封存。任務組「快結束」的條件 SHALL 為剩餘時間大於 0、小於 4 小時、且尚未全部完成；活動「快結束」為剩餘時間小於 24 小時且已開始。

#### Scenario: 任務全部完成

- **WHEN** 任務組所有項目都勾選完成
- **THEN** 該組 SHALL 顯示「全部完成」且不算快結束

#### Scenario: 舊的完成紀錄

- **WHEN** UserProperties 裡還有某活動的 `done` 紀錄而活動尚未結束
- **THEN** 該活動 SHALL 仍顯示在 GO 活動頁

<!-- @trace
source: remove-event-checkbox
updated: 2026-10-22
code:
  - gas/App.html
  - tests/gas/load.js
  - README.md
  - tests/gas/app.js
  - gas/Code.gs
  - gas/Styles.html
tests:
  - tests/gas/app.test.js
  - tests/gas/merge.test.js
-->

---
### Requirement: 任務依序勾選

限時調查任務組（LeekDuck `ld-` 與巴哈 `bh-` 開頭）內的任務 SHALL 依頁面顯示順序具有先後關係：勾選第 N 項時，第 1 到 N 項 SHALL 都變成已勾選；取消第 N 項時，第 N 項到最後一項 SHALL 都變成未勾選。不同任務組互不影響。每月田野調查（`field-` 開頭）的任務 SHALL 各自獨立勾選，不連動。

#### Scenario: 田野調查不連動

- **WHEN** 使用者在「10 月田野調查」勾第 5 項
- **THEN** 只有第 5 項 SHALL 變成已勾選

#### Scenario: 勾選後面的任務

- **WHEN** 某組有 25 項，使用者勾第 20 項
- **THEN** 第 1–20 項 SHALL 都是已勾選，第 21–25 項不變

##### Example: 依序勾選

| 目前已勾選 | 動作 | 結果已勾選 |
| ---------- | ---- | ---------- |
| 無 | 勾第 5 項 | 1–5 |
| 1–5 | 勾第 20 項 | 1–20 |
| 1–20 | 取消第 5 項 | 1–4 |


<!-- @trace
source: task-progress-save
updated: 2026-10-22
code:
  - .spectra.yaml
  - gas/Index.html
  - shared/board.json
  - tests/gas/app.js
  - gas/Styles.html
  - scraper/sources/pchome.py
  - gas/Board.gs
  - gas/App.html
  - scraper/sources/__init__.py
  - gas/Code.gs
  - tests/gas/load.js
  - README.md
  - scraper/main.py
tests:
  - tests/test_scraper.py
  - tests/gas/merge.test.js
  - tests/gas/app.test.js
-->

---
### Requirement: 一次儲存

`saveTasks(changes)` SHALL 接受 `{ "<任務組id>#<任務id>": true|false }`，每個鍵與值都合法時才在同一個 user lock 內全部寫入並回傳最新狀態；有任何不合法的鍵或值時 SHALL 丟出 `bad change` 且不寫入。

#### Scenario: 不合法的值

- **WHEN** `saveTasks({"g1#t1": "yes"})`
- **THEN** 系統 SHALL 丟出 `bad change`，狀態不變

<!-- @trace
source: task-progress-save
updated: 2026-10-22
code:
  - .spectra.yaml
  - gas/Index.html
  - shared/board.json
  - tests/gas/app.js
  - gas/Styles.html
  - scraper/sources/pchome.py
  - gas/Board.gs
  - gas/App.html
  - scraper/sources/__init__.py
  - gas/Code.gs
  - tests/gas/load.js
  - README.md
  - scraper/main.py
tests:
  - tests/test_scraper.py
  - tests/gas/merge.test.js
  - tests/gas/app.test.js
-->