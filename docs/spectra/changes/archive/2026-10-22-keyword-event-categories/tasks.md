## 1. 關鍵字表

- [x] 1.1 在 `shared/board.json` 每個分類加上預設 `keywords` 並重新產生 `gas/Board.gs`，讓「六大分類」需求裡的表格就是實際資料。驗證：`test_board_gs_is_generated` 通過。

## 2. 比對

- [x] 2.1 `translate.event_category(type_slug, name, name_zh="")` 先查類型對照表，再依分頁順序比對英文（不分大小寫）和中文名稱的關鍵字；`main.build_events` 傳入翻譯後的名稱（六大分類）。驗證：`CategoryTests` 單元測試涵蓋範例表的每一列。[after: 1.1]
- [x] 2.2 README 的「調整」段落說明怎麼加關鍵字並重新產生 `gas/Board.gs`。驗證：檢查內容。[after: 2.1]
