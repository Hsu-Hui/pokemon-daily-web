## 摘要

讓任務勾選符合遊戲裡調查的進行方式，也不再每點一下就存：勾某個任務時，它上面的任務也一起勾；變更先留在頁面上，按「儲存」才送出；總覽列出 2 天內結束、還沒做完的任務。

## 動機

- 限時調查是一步一步解的；勾了第 20 項代表第 1～19 項也做完了，但現在每一格都要手動勾。
- 現在每勾一次就呼叫一次伺服器儲存；Ryan 想勾好幾個再一次儲存。
- 「快結束了，還沒完成」只列最後 4 小時的任務組，太晚了，來不及安排。

## 解決方式

- 同一個任務組裡依序勾選：勾第 N 項時第 1～N 項都打勾；取消第 N 項時第 N 項到最後都取消。
- 頁面最上面加固定的儲存列，顯示「儲存」和「有 N 項變更未儲存」。任務勾選先存在頁面的草稿，按儲存才送出；切換分頁草稿還在；有未儲存變更時離開或重新整理會先確認；儲存失敗保留草稿並提示。
- Apps Script 新增 `saveTasks(changes)`，一次寫入所有變更。
- 總覽「快結束了，還沒完成」列出沒做完、沒放棄、48 小時內結束的任務組（`shared/board.json` 的 `overviewTaskHours`）。Discord 提醒維持 4 小時。

## 不做的事

見 design.md。

## 影響

- 影響的規格：dashboard、user-progress
- 影響的程式：
  - 修改：gas/App.html、gas/Styles.html、gas/Code.gs、shared/board.json、gas/Board.gs、tests/gas/app.test.js、tests/gas/merge.test.js、tests/gas/app.js、README.md
  - 新增：無
  - 刪除：無
