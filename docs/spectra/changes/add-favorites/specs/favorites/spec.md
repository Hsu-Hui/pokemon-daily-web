## Purpose

Let each user star Taiwan news and products and keep them on a 我的最愛 tab, even after the board removes the original items.

## ADDED Requirements

### Requirement: Star buttons

台灣活動的每則新聞、新商品頁與總覽「今天新上架」的每件商品 SHALL 有星號按鈕：未收藏顯示 ☆，已收藏顯示 ★。按下 SHALL 立即加入或移除我的最愛（不經過任務的「儲存」），且 SHALL 不開啟該新聞或商品的連結。

#### Scenario: Star a news item

- **WHEN** 使用者在台灣活動按某則新聞的 ☆
- **THEN** 星號 SHALL 變成 ★，該新聞 SHALL 出現在我的最愛

#### Scenario: Toggle fails

- **WHEN** 儲存收藏失敗
- **THEN** 星號 SHALL 恢復原狀並顯示「儲存失敗，請再試一次」

### Requirement: Favorites storage

收藏 SHALL 依 Google 帳號分開存在 UserProperties，每筆一個屬性，內容為快照：類型（news／product）、id、標題或名稱、網址、來源、媒體、價格、圖片、日期與收藏時間。`toggleFavorite(item, on)` SHALL 驗證類型、id、標題與 http(s) 網址，每個欄位最多 300 字；不合法時丟出 `bad favorite`；收藏超過 500 筆時 SHALL 丟出「我的最愛已滿」。`getData` SHALL 回傳目前使用者的收藏。

#### Scenario: Item removed after 7 days

- **WHEN** 一則已收藏的新聞 7 天後從新聞分頁被刪除
- **THEN** 它 SHALL 仍顯示在我的最愛，內容為收藏當時的快照

#### Scenario: Two users

- **WHEN** 使用者 A 收藏某商品
- **THEN** 使用者 B 的我的最愛 SHALL 不受影響

### Requirement: Favorites tab

看板 SHALL 有「我的最愛」分頁，分成「台灣活動」與「商品」兩區，各依收藏時間新到舊排列並每頁最多 25 筆；每筆有 ★ 可取消收藏；已不在目前列表中的項目 SHALL 標示「已下架」。沒有收藏時 SHALL 顯示「還沒有收藏，按 ☆ 加入」。

#### Scenario: Unstar from favorites

- **WHEN** 使用者在我的最愛按某商品的 ★
- **THEN** 該商品 SHALL 從我的最愛移除，新商品頁的星號 SHALL 變回 ☆
