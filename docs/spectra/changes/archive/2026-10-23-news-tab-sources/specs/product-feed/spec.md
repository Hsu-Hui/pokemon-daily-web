## REMOVED Requirements

### Requirement: 商品消息轉成商品

**Reason**: 寶可夢中心新聞和官網商品公告是消息，不是可以買的商品；Ryan 要求放到「活動&新聞」。

**Migration**: 這些消息改由 news-feed 輸出在 payload 的 `news`，看板在「活動&新聞」顯示。試算表裡已存成商品的舊資料由看板轉到「活動&新聞」顯示，7 天內自然過期。
