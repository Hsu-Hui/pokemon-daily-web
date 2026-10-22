## ADDED Requirements

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
