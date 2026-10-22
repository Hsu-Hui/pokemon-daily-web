## MODIFIED Requirements

### Requirement: 先更新畫面再儲存

網頁 SHALL 把任務勾選先套用在畫面的草稿上，按「儲存」時以 `saveTasks` 一次送出；成功後以回傳狀態取代畫面狀態並清空草稿，失敗時 SHALL 保留草稿並顯示「儲存失敗，請再試一次」。「放棄」「復原」仍 SHALL 先套用在畫面並立即以 `setFlag` 儲存，失敗時還原並顯示同樣提示。

#### Scenario: 儲存失敗

- **WHEN** `saveTasks` 呼叫失敗
- **THEN** 勾選 SHALL 維持草稿狀態並顯示提示

## ADDED Requirements

### Requirement: 任務依序勾選

同一個任務組內的任務 SHALL 依頁面顯示順序具有先後關係：勾選第 N 項時，第 1 到 N 項 SHALL 都變成已勾選；取消第 N 項時，第 N 項到最後一項 SHALL 都變成未勾選。不同任務組互不影響。

#### Scenario: 勾選後面的任務

- **WHEN** 某組有 25 項，使用者勾第 20 項
- **THEN** 第 1–20 項 SHALL 都是已勾選，第 21–25 項不變

##### Example: 依序勾選

| 目前已勾選 | 動作 | 結果已勾選 |
| ---------- | ---- | ---------- |
| 無 | 勾第 5 項 | 1–5 |
| 1–5 | 勾第 20 項 | 1–20 |
| 1–20 | 取消第 5 項 | 1–4 |

### Requirement: 一次儲存

`saveTasks(changes)` SHALL 接受 `{ "<任務組id>#<任務id>": true|false }`，每個鍵與值都合法時才在同一個 user lock 內全部寫入並回傳最新狀態；有任何不合法的鍵或值時 SHALL 丟出 `bad change` 且不寫入。

#### Scenario: 不合法的值

- **WHEN** `saveTasks({"g1#t1": "yes"})`
- **THEN** 系統 SHALL 丟出 `bad change`，狀態不變
