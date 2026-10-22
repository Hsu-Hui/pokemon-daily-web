## ADDED Requirements

### Requirement: Duplicate products removed

商品 SHALL 以「名稱（去掉多餘空白、不分大小寫）＋價格」為鍵去重，只保留第一筆（最新上架）。看板顯示時 SHALL 用同一個鍵再去重一次，讓試算表裡已存的重複商品不再顯示。

#### Scenario: Same product under two PChome ids

- **WHEN** PChome 回傳 `DECU5W-A900FSAGQ` 與 `DEAS4E-A900FSAIT`，名稱都是「皮卡丘 卡比獸 百變怪 精靈球 造型存錢筒」、價格都是 $590
- **THEN** payload 與新商品頁 SHALL 只有一筆

#### Scenario: Same name different price

- **WHEN** 兩件商品名稱相同但價格不同
- **THEN** 兩件 SHALL 都保留
