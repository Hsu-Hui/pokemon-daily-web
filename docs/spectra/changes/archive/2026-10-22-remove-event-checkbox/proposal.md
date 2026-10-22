## 摘要

拿掉 GO 活動的「完成」勾選方塊。活動留在 GO 活動頁直到結束，結束後自動移到封存。

## 動機

Ryan 不想一個一個勾活動；勾選活動完成多了一個步驟，而且沒有其他功能用到它（提醒只針對任務組）。

## 解決方式

- GO 活動的表格和卡片不再有勾選方塊和「完成」欄；所有還沒結束的活動都列出來。
- 總覽第一個數字改成「進行中活動」（已開始且未結束）。
- 封存只列已結束的活動，沒有「復原」按鈕；已放棄的任務組仍保留「復原」。
- `setFlag` 只接受 `taskDone` 和 `gaveUp`；UserProperties 裡舊的 `done` 紀錄會被忽略。

## 不做的事

- 任務勾選、「放棄」和 Discord 提醒都不變。
- 不寫程式刪除已存的 `done` 紀錄。

## 影響

- 影響的規格：dashboard、user-progress
- 影響的程式：
  - 修改：gas/App.html、gas/Code.gs、tests/gas/app.test.js、tests/gas/merge.test.js
  - 新增：無
  - 刪除：無
