## 摘要

新增「我的最愛」分頁。台灣活動的每則新聞和新商品的每件商品都有星號按鈕；收藏的項目會出現在我的最愛，直到取消收藏為止，原本的項目從看板刪掉後也還在。

## 動機

新聞和商品 7 天後就會消失。Ryan 想把在意的項目收在同一個地方。

## 解決方式

- 台灣活動的每則新聞、新商品的每件商品（也包含總覽「今天新上架」的卡片）都有星號按鈕（☆／★）。按了馬上加入或取消（不經過任務的「儲存」）。
- 新的「我的最愛」分頁分成「台灣活動」和「商品」兩區，依收藏時間新到舊排列，每項都有同樣的星號可以取消。
- 收藏依 Google 帳號分開存在 UserProperties，存的是快照（標題／名稱、網址、來源、媒體、價格、圖片、日期、收藏時間），所以原本的項目從試算表刪掉後還看得到。
- Apps Script 新增 `toggleFavorite(item, on)`，`getData` 也回傳收藏。

## 不做的事

見 design.md。

## 影響

- 影響的規格：favorites（新）、dashboard
- 影響的程式：
  - 修改：gas/Code.gs、gas/App.html、gas/Styles.html、tests/gas/app.test.js、tests/gas/merge.test.js、tests/gas/app.js、tests/gas/load.js、README.md
  - 新增：無
  - 刪除：無
