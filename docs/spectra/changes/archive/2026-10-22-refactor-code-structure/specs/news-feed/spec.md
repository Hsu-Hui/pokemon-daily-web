## MODIFIED Requirements

### Requirement: 新聞分類

官網消息的分類或標題含「商品」「發售」「上市」「販售」「新品」「周邊」「週邊」「寶可夢中心」其中之一時 `kind` SHALL 為 `product`，否則為 `event`；寶可夢中心新聞為 `product`；台灣活動新聞為 `event`。kind SHALL 在去重之前就決定，去重 SHALL 不修改輸入的新聞物件。去重後 `kind` 為 `product` 的消息 SHALL 轉成商品放進 payload 的 `products`（見 product-feed），payload 的 `news` SHALL 只包含 `event`。每筆 `news` 輸出 SHALL 包含 `id`、`kind`、`title`、`url`、`source`、`others`、`published`。

#### Scenario: 官網商品公告

- **WHEN** 官網消息分類為「商品」
- **THEN** 該消息 SHALL 出現在 payload 的 `products`，不出現在 `news`

#### Scenario: 台灣活動新聞

- **WHEN** 台灣活動新聞去重後保留
- **THEN** 該新聞 SHALL 出現在 payload 的 `news`，`kind` 為 `event`
