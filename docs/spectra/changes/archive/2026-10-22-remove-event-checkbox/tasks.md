## 1. 看板

- [x] 1.1 拿掉 GO 活動列和卡片的勾選方塊與「完成」欄，列出所有未結束的活動，總覽數字改名為「進行中活動」，已結束的活動在封存頁顯示且沒有「復原」（GO 活動頁、分頁、封存頁、狀態判斷）。驗證：`tests/gas/app.test.js` 的 node 測試——GO 活動頁沒有 `data-flag="done"`、有舊 `done` 紀錄的活動仍然列出、已結束的活動在封存頁且沒有「復原」。

## 2. Apps Script

- [x] 2.1 `setFlag` 只接受 `taskDone` 和 `gaveUp`；`loadState_` 不再回傳 `done`（設定勾選、每個人的勾選紀錄）。驗證：node 測試確認 `setFlag('done', …)` 丟出 `bad kind`。[after: 1.1]
