# news-feed Specification

## Purpose

收集寶可夢台灣官網最新消息與 Google 新聞，去掉重複報導，分成「新商品」（product）與「台灣活動」（event）兩類。對應 `scraper/sources.py` 的 `parse_official_news`、`fetch_official_news`、`fetch_google_news`、`dedupe_news`、`similarity`，以及 `scraper/main.py` 的 `build_news`、`news_kind`。

## Requirements

### Requirement: Official news

系統 SHALL 解析 `https://tw.portal-pokemon.com/topics/` 列表中每個指向 `/topics/<slug>` 的連結，取最長的文字段（超過 4 字）為標題、1～4 字的段落為分類、文字中的日期（`YYYY.MM.DD`、`YYYY年M月D日` 或 `M.D.YYYY`）為發布日。只保留 3 天內（`OFFICIAL_MAX_AGE_DAYS`，從當天 00:00 起算）或沒有日期的消息。

#### Scenario: Title repeated

- **WHEN** 標題文字是「A A」這種同一句重複兩次
- **THEN** 標題 SHALL 只留一份

#### Scenario: Category inside title

- **WHEN** 沒有獨立分類段落，而標題結尾是「 活動」「 商品」等分類字
- **THEN** 系統 SHALL 把結尾分類字拆出來當分類

### Requirement: Google News

系統 SHALL 以 Google News RSS（zh-TW、TW）查詢兩組關鍵字：寶可夢中心新品（`pc_taipei`）與台灣寶可夢活動（`tw_events`），只收最近 24 小時、且標題（不分大小寫）含「寶可夢」「pokémon」「pokemon」「皮卡丘」「神奇寶貝」「ptcg」其中之一的新聞。

#### Scenario: Unrelated title

- **WHEN** 新聞標題是某品牌新品但沒有寶可夢相關字
- **THEN** 該新聞 SHALL 不收

#### Scenario: Title cleanup

- **WHEN** 標題結尾是「 - 媒體名稱」、開頭是「討論牆 |」或結尾是「- 遊戲新聞」這類分類
- **THEN** 系統 SHALL 去掉這些前後綴

### Requirement: Story dedupe

系統 SHALL 依官網、寶可夢中心新聞、台灣活動新聞的順序合併後去重：兩則標題的 bigram 相似度（交集數 ÷ 較小集合數，比較前去掉空白與標點並轉小寫）達 0.45（`NEWS_SIMILARITY`）以上視為同一則，只留先出現的那則，後來的媒體名稱（與保留者不同且未記錄過時）記在 `others`。

#### Scenario: Same story from two outlets

- **WHEN** 兩家媒體報導同一活動，標題相似度 0.6
- **THEN** 只 SHALL 保留第一則，第二家媒體名稱出現在第一則的 `others`

#### Scenario: Official version wins

- **WHEN** 官網公告與新聞報導是同一件事
- **THEN** SHALL 保留官網版本

### Requirement: News kind

官網消息的分類或標題含「商品」「發售」「上市」「販售」「新品」「周邊」「週邊」「寶可夢中心」其中之一時 `kind` SHALL 為 `product`，否則為 `event`；寶可夢中心新聞為 `product`；台灣活動新聞為 `event`。每筆輸出 SHALL 包含 `id`、`kind`、`title`、`url`、`source`、`others`、`published`。

#### Scenario: Official product announcement

- **WHEN** 官網消息分類為「商品」
- **THEN** `kind` SHALL 為 `product`
