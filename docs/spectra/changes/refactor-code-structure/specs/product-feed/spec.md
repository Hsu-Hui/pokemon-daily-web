## ADDED Requirements

### Requirement: Product announcements

`kind` 為 `product` 的新聞 SHALL 轉成商品：`id` 沿用新聞 id，`source` 在官網消息時為「官網」、其他為「寶可夢中心」，`name` 為新聞標題，`url` 為新聞網址，`price` 與 `image` 為空字串，`media` 為新聞來源（媒體名稱）。PChome 商品的 `media` SHALL 為空字串。所有商品 SHALL 以相同欄位輸出。

#### Scenario: Pokémon Center news

- **WHEN** 寶可夢中心新聞「寶可夢中心台北聖誕新品」由「上報」報導
- **THEN** payload 的 `products` SHALL 包含 `source` 為「寶可夢中心」、`name` 為該標題、`price` 為空字串、`media` 為「上報」的商品
