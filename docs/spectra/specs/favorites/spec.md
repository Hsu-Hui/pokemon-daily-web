# favorites Specification

## Purpose

讓每個使用者收藏台灣活動新聞和商品，集中放在「我的最愛」分頁，原本的項目從看板刪掉後也還看得到。

## Requirements

### Requirement: 星號按鈕

活動&新聞的每則消息、新商品頁與總覽「今天新上架」的每件商品 SHALL 有星號按鈕：未收藏顯示 ☆，已收藏顯示 ★。按下 SHALL 立即加入或移除我的最愛（不經過任務的「儲存」），且 SHALL 不開啟該新聞或商品的連結。

#### Scenario: 收藏一則新聞

- **WHEN** 使用者在活動&新聞按某則新聞的 ☆
- **THEN** 星號 SHALL 變成 ★，該新聞 SHALL 出現在我的最愛

#### Scenario: 收藏失敗

- **WHEN** 儲存收藏失敗
- **THEN** 星號 SHALL 恢復原狀並顯示「儲存失敗，請再試一次」


<!-- @trace
source: news-tab-sources
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - scraper/main.py
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->

---
### Requirement: 收藏儲存

收藏 SHALL 依 Google 帳號分開存在 UserProperties，每筆一個屬性，內容為快照：類型（news／product）、id、標題或名稱、網址、來源、媒體、價格、圖片、日期與收藏時間。`toggleFavorite(item, on)` SHALL 驗證類型、id、標題與 http(s) 網址，每個欄位最多 300 字；不合法時丟出 `bad favorite`；收藏超過 500 筆時 SHALL 丟出「我的最愛已滿」。`getData` SHALL 回傳目前使用者的收藏。

#### Scenario: 7 天後項目被刪除

- **WHEN** 一則已收藏的新聞 7 天後從新聞分頁被刪除
- **THEN** 它 SHALL 仍顯示在我的最愛，內容為收藏當時的快照

#### Scenario: 兩個使用者

- **WHEN** 使用者 A 收藏某商品
- **THEN** 使用者 B 的我的最愛 SHALL 不受影響


<!-- @trace
source: add-favorites
updated: 2026-10-22
code:
  - gas/Index.html
  - scraper/sources/__init__.py
  - README.md
  - scraper/main.py
  - gas/App.html
  - tests/gas/app.js
  - scraper/sources/pchome.py
  - tests/gas/load.js
  - gas/Code.gs
  - .spectra.yaml
  - gas/Board.gs
  - shared/board.json
  - gas/Styles.html
tests:
  - tests/test_scraper.py
  - tests/gas/app.test.js
  - tests/gas/merge.test.js
-->

---
### Requirement: 我的最愛頁

看板 SHALL 有「我的最愛」分頁，分成「活動&新聞」與「商品」兩區，各依收藏時間新到舊排列並每頁最多 25 筆；每筆有 ★ 可取消收藏；已不在目前列表中的項目 SHALL 標示「已下架」。沒有收藏時 SHALL 顯示「還沒有收藏，按 ☆ 加入」。

#### Scenario: 從我的最愛取消收藏

- **WHEN** 使用者在我的最愛按某商品的 ★
- **THEN** 該商品 SHALL 從我的最愛移除，新商品頁的星號 SHALL 變回 ☆

<!-- @trace
source: news-tab-sources
updated: 2026-10-23
code:
  - README.md
  - gas/App.html
  - scraper/main.py
tests:
  - tests/gas/app.test.js
  - tests/test_scraper.py
-->