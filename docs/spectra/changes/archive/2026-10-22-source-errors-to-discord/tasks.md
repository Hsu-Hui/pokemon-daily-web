## 1. Discord 通知

- [x] 1.1 新增 `notifyErrors_(errors, generatedAt)`，在 `doPost` 最後呼叫，發到 `DISCORD_WEBHOOK_URL`，webhook 失敗時不影響結果（抓取失敗通知）。驗證：用假的 `UrlFetchApp` 做 node 測試——有錯誤時發一則、沒有錯誤時不發、假物件丟出錯誤時仍回 `ok:true`。

## 2. 總覽

- [x] 2.1 拿掉總覽的錯誤橫幅和 `getData` 的 `errors`（資料載入）。驗證：node 測試確認 `getData()` 沒有 `errors`，並手動檢查總覽。[after: 1.1]
