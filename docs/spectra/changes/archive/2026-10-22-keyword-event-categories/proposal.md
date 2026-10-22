## 摘要

GO 活動名稱含某個分頁（分類）的關鍵字時，就歸到那個分類。關鍵字表放在 `shared/board.json`，Ryan 可以自己修改。

## 動機

ScrapedDuck 類型是 `event` 這種通用類型的活動，就算名稱已經寫明是什麼（例如「Dynamax Trails」「GO Pass: Halloween」），還是會被歸到「其他」。目前的名稱規則是寫死在 `translate.event_category` 裡的英文正規表示式，而且只涵蓋三個分類。

## 解決方式

- `shared/board.json` 的每個分類加上 `keywords` 清單（英文和中文）。
- `event_category(type_slug, name, name_zh)` 先查類型對照表；類型對不到時，依分頁順序檢查英文原名和翻譯後的中文名稱是否含該分類的關鍵字（不分大小寫），取第一個符合的；都不符合就是「其他」。
- 測試涵蓋一張範例名稱表。

## 不做的事

- 不在瀏覽器端比對關鍵字；分類每天由爬蟲決定。
- 類型對照表不變。

## 影響

- 影響的規格：go-events
- 影響的程式：
  - 修改：shared/board.json、gas/Board.gs、scraper/translate.py、scraper/main.py、tests/test_scraper.py、README.md
  - 新增：無
  - 刪除：無
