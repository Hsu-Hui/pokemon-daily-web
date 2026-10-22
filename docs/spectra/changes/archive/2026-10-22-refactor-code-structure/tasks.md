## 1. 共用設定

- [x] 1.1 實作「共用設定檔，加上產生的 Apps Script 版本」（共用設定）：新增 `shared/board.json`、`scripts/build_gas_config.py` 和產生的 `gas/Board.gs`；`scraper/translate.py` 從 board.json 讀分類；`scripts/deploy_gas.sh` 上傳前重新產生。驗證：新的單元測試 `test_board_gs_is_generated` 通過，且改了 board.json 沒重新產生時會失敗。

## 2. 爬蟲結構

- [x] 2.1 實作「sources package 與共用的日期模組」：用 `scraper/sources/` package 和共用的 `dates.py` 取代 `scraper/sources.py`，`from scraper import sources` 的名稱不變。驗證：除了拿掉的 `known_titles` 測試，`python -m unittest` 照樣通過。
- [x] 2.2 實作「去重前先標好分類」（新聞分類）：`News.kind` 在 `dedupe_news` 之前設定，`dedupe_news` 不再修改輸入，也不接受 `known_titles`。驗證：單元測試確認去重後輸入項目的 `others` 仍是空的。
- [x] 2.3 實作「商品公告在爬蟲端轉成商品」（商品消息轉成商品）：商品類新聞轉成帶 `media` 的 `Product`，商品用 `dataclasses.asdict` 輸出，`payload.news` 只有活動新聞。驗證：`main.build_news`／`news_to_product` 輸出格式的單元測試。[after: 2.2]
- [x] 2.4 實作「翻譯對照表放進資料檔」：月份、流星雨和地名搬到 `scraper/data/translations.json`。驗證：既有的翻譯測試，以及 `event_name("Pokémon GO Wild Area 2026: Sendai • Tohoku")` 前後結果相同。[after: 1.1]

## 3. Apps Script

- [x] 3.1 實作「doPost 一律回 JSON」（密碼檢查）和 `media` 欄（試算表儲存）；保留天數改讀 `BOARD`。驗證：node 測試送出格式錯誤的內容會得到 `{ok:false}`。[after: 1.1]
- [x] 3.2 實作「用 include() 拆分 Index.html」和新商品頁需求：`Index.html` + `Styles.html` + `App.html`，每個分頁一個 `RENDERERS` 函式，標籤和分類來自 `data.config`，商品直接顯示不轉換、沒有價格顯示「看消息」。驗證：部署後手動檢查六個分頁，並用 node 測試確認每個分頁都能畫出來。[after: 3.1]
- [x] 3.3 實作「Apps Script 純函式的 Node 測試」：`tests/gas/merge.test.js` 測 `mergeTimed_`（封存保留 30 天）和 `mergeFresh_`（已看過清單、7 天過期）；每日 workflow 執行 `node --test tests/gas`。驗證：本機 `node --test tests/gas` 通過。[after: 3.1]

## 4. 文件

- [x] 4.1 更新 README 的檔案表和「調整」段落，說明 `shared/board.json` 和新檔案。驗證：檢查內容。[after: 3.2]
