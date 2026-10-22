## 摘要

總覽頁不再顯示抓取失敗；每日執行有來源失敗時，發一則 Discord 訊息到原本的 webhook。

## 動機

只要有來源失敗，總覽最上面就會出現紅色的「今天這些來源抓取失敗」橫幅，但只有 Ryan 能處理這件事。Ryan 已經在 Discord 收任務提醒，希望失敗通知也發到那裡。

## 解決方式

- `doPost` 寫入資料後，`data.errors` 不為空時發一則訊息到 `DISCORD_WEBHOOK_URL`：「⚠️ 每日抓取有來源失敗：<來源（原因）、…>」、抓取時間，有設定 `VIEW_URL` 時附上看板網址。
- webhook 呼叫失敗只記錄下來，不影響接收資料的回應。
- 拿掉總覽的橫幅和 `getData` 的 `errors` 欄位；錯誤仍記錄在「狀態」分頁。

## 不做的事

- 不新增 secret 或 webhook；GitHub Actions 本身不發 Discord。
- 不重試，也不跨天去重。

## 影響

- 影響的規格：dashboard、discord-reminder
- 影響的程式：
  - 修改：gas/Code.gs、gas/App.html、tests/gas/merge.test.js、README.md
  - 新增：無
  - 刪除：無
