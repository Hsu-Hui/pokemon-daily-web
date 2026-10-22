# discord-reminder Specification

## Purpose

任務快結束還沒完成時，透過 Discord webhook 提醒：結束前 2 天提醒一次，最後 4 小時每小時提醒。對應 `gas/Code.gs` 的 `remindTasks`。

## Requirements

### Requirement: 每小時檢查

`remindTasks` SHALL 由每小時的時間觸發器執行（由 `setup` 建立）；沒有設定 Script Property `DISCORD_WEBHOOK_URL` 時 SHALL 直接結束。提醒依據 SHALL 為觸發器擁有者（執行者）自己的勾選紀錄。

#### Scenario: 沒有設定 webhook

- **WHEN** `DISCORD_WEBHOOK_URL` 未設定
- **THEN** 系統 SHALL 不發送任何訊息

---
### Requirement: 提醒時間範圍

任務組 SHALL 在有結束時間、未被放棄、剩餘時間大於 0、且至少有一項未勾選時才可能提醒；每組一則訊息。剩餘時間不超過 `earlyRemindHours`（48 小時）但大於 `remindHours`（4 小時）時，每個任務組 SHALL 只提醒一次（記在觸發器擁有者 UserProperties 的 `earlyReminded`）；剩餘時間不超過 `remindHours` 時 SHALL 每小時提醒。兩個時數設定在 `shared/board.json`。

#### Scenario: 任務組剩 40 小時

- **WHEN** 某任務組剩 40 小時、還有未完成項目，觸發器連續執行兩次
- **THEN** 系統 SHALL 只在第一次發送提醒

#### Scenario: 任務組剩 3 小時

- **WHEN** 某任務組剩 3 小時 20 分、還有 2 項沒完成
- **THEN** 系統 SHALL 發送一則提醒，下一小時仍未完成時再發一次

#### Scenario: 已放棄的任務組

- **WHEN** 使用者已放棄該任務組
- **THEN** 系統 SHALL 不發送提醒

---
### Requirement: 提醒訊息內容

訊息 SHALL 包含「⏰ **任務快結束：<名稱>**」、剩餘小時與分鐘、未完成項數，最多列 15 項未完成任務（含獎勵），超過時附「…還有 N 項」；有設定 `VIEW_URL` 時 SHALL 附上看板網址。訊息內容 SHALL 截斷在 1900 字內。

#### Scenario: 很多未完成任務

- **WHEN** 有 20 項未完成
- **THEN** 訊息 SHALL 列出前 15 項並加上「…還有 5 項」

---
### Requirement: 抓取失敗通知

`doPost` 寫入資料後，payload 的 `errors` 不為空且有設定 `DISCORD_WEBHOOK_URL` 時，系統 SHALL 發送一則 Discord 訊息，內容包含「⚠️ 每日抓取有來源失敗：」與以「、」連接的失敗來源、payload 的 `generatedAt`（台灣時間），有設定 `VIEW_URL` 時附上看板網址。webhook 呼叫失敗 SHALL 只記錄在執行記錄，不影響接收資料的回應。`errors` 為空時 SHALL 不發送。

#### Scenario: 一個來源失敗

- **WHEN** 每日資料的 `errors` 為 `["PChome（請求次數過多被限制）"]`
- **THEN** Discord SHALL 收到一則包含「⚠️ 每日抓取有來源失敗：PChome（請求次數過多被限制）」的訊息，`doPost` 仍回應 `ok: true`

#### Scenario: 沒有失敗

- **WHEN** `errors` 為空陣列
- **THEN** 系統 SHALL 不發送 Discord 訊息

#### Scenario: Webhook 故障

- **WHEN** Discord webhook 回應錯誤
- **THEN** `doPost` SHALL 仍回應 `ok: true`
