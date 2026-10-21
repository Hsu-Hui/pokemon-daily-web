# discord-reminder Specification

## Purpose

任務快結束還沒完成時，每小時透過 Discord webhook 提醒。對應 `gas/Code.gs` 的 `remindTasks`。

## Requirements

### Requirement: Hourly check

`remindTasks` SHALL 由每小時的時間觸發器執行（由 `setup` 建立）；沒有設定 Script Property `DISCORD_WEBHOOK_URL` 時 SHALL 直接結束。提醒依據 SHALL 為觸發器擁有者（執行者）自己的勾選紀錄。

#### Scenario: No webhook configured

- **WHEN** `DISCORD_WEBHOOK_URL` 未設定
- **THEN** 系統 SHALL 不發送任何訊息

### Requirement: Reminder window

任務組 SHALL 在有結束時間、未被放棄、剩餘時間大於 0 且不超過 4 小時（`REMIND_HOURS`）、且至少有一項未勾選時發送提醒；每組一則訊息。

#### Scenario: Task group 3 hours left

- **WHEN** 某任務組剩 3 小時 20 分、還有 2 項沒完成
- **THEN** 系統 SHALL 發送一則提醒，下一小時仍未完成時再發一次

#### Scenario: Given up group

- **WHEN** 使用者已放棄該任務組
- **THEN** 系統 SHALL 不發送提醒

### Requirement: Message content

訊息 SHALL 包含「⏰ **任務快結束：<名稱>**」、剩餘小時與分鐘、未完成項數，最多列 15 項未完成任務（含獎勵），超過時附「…還有 N 項」；有設定 `VIEW_URL` 時 SHALL 附上看板網址。訊息內容 SHALL 截斷在 1900 字內。

#### Scenario: Many unfinished tasks

- **WHEN** 有 20 項未完成
- **THEN** 訊息 SHALL 列出前 15 項並加上「…還有 5 項」
