# news-feed Specification

## Purpose

收集寶可夢台灣官網最新消息與 Google 新聞，去掉重複報導，分成「新商品」（product）與「台灣活動」（event）兩類。對應 `scraper/sources/` 的 `parse_official_news`、`fetch_official_news`、`fetch_google_news`、`dedupe_news`、`similarity`，以及 `scraper/main.py` 的 `build_news`、`news_kind`。

## Requirements

### Requirement: 官網消息

系統 SHALL 解析 `https://tw.portal-pokemon.com/topics/` 列表中每個指向 `/topics/<slug>` 的連結，取最長的文字段（超過 4 字）為標題、1～4 字的段落為分類、文字中的日期（`YYYY.MM.DD`、`YYYY年M月D日` 或 `M.D.YYYY`）為發布日。只保留 3 天內（`OFFICIAL_MAX_AGE_DAYS`，從當天 00:00 起算）或沒有日期的消息。

#### Scenario: 標題重複

- **WHEN** 標題文字是「A A」這種同一句重複兩次
- **THEN** 標題 SHALL 只留一份

#### Scenario: 分類寫在標題裡

- **WHEN** 沒有獨立分類段落，而標題結尾是「 活動」「 商品」等分類字
- **THEN** 系統 SHALL 把結尾分類字拆出來當分類

---
### Requirement: Google 新聞

系統 SHALL 以 Google News RSS（zh-TW、TW）查詢兩組關鍵字：寶可夢中心新品（`pc_taipei`）與台灣寶可夢活動（`tw_events`），只收最近 24 小時、且標題（不分大小寫）含「寶可夢」「pokémon」「pokemon」「皮卡丘」「神奇寶貝」「ptcg」其中之一的新聞。

#### Scenario: 無關的標題

- **WHEN** 新聞標題是某品牌新品但沒有寶可夢相關字
- **THEN** 該新聞 SHALL 不收

#### Scenario: 標題清理

- **WHEN** 標題結尾是「 - 媒體名稱」、開頭是「討論牆 |」或結尾是「- 遊戲新聞」這類分類
- **THEN** 系統 SHALL 去掉這些前後綴

---
### Requirement: 同一則新聞去重

系統 SHALL 依官網、寶可夢中心新聞、台灣活動新聞的順序合併後去重：兩則標題的 bigram 相似度（交集數 ÷ 較小集合數，比較前去掉空白與標點並轉小寫）達 0.45（`NEWS_SIMILARITY`）以上視為同一則，只留先出現的那則，後來的媒體名稱（與保留者不同且未記錄過時）記在 `others`。

#### Scenario: 兩家媒體報導同一件事

- **WHEN** 兩家媒體報導同一活動，標題相似度 0.6
- **THEN** 只 SHALL 保留第一則，第二家媒體名稱出現在第一則的 `others`

#### Scenario: 保留官網版本

- **WHEN** 官網公告與新聞報導是同一件事
- **THEN** SHALL 保留官網版本

---
### Requirement: 新聞分類

官網消息的分類或標題含「商品」「發售」「上市」「販售」「新品」「周邊」「週邊」「寶可夢中心」其中之一時 `kind` SHALL 為 `product`，否則為 `event`；寶可夢中心新聞為 `product`；台灣活動新聞為 `event`。kind SHALL 在去重之前就決定，去重 SHALL 不修改輸入的新聞物件。去重後所有消息（不論 `kind`）SHALL 都放在 payload 的 `news`，不轉成商品。每筆 `news` 輸出 SHALL 包含 `id`、`kind`、`title`、`url`、`source`、`others`、`published`。

#### Scenario: 官網商品公告

- **WHEN** 官網消息分類為「商品」
- **THEN** 該消息 SHALL 出現在 payload 的 `news`，`kind` 為 `product`，且不出現在 `products`

#### Scenario: 台灣活動新聞

- **WHEN** 台灣活動新聞去重後保留
- **THEN** 該新聞 SHALL 出現在 payload 的 `news`，`kind` 為 `event`

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