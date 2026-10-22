## MODIFIED Requirements

### Requirement: Tabs

看板 SHALL 有七個分頁：總覽、GO 活動、任務待辦、新商品、台灣活動、我的最愛、封存；目前分頁 SHALL 記在瀏覽器 localStorage，下次開啟沿用。

#### Scenario: Overview content

- **WHEN** 使用者在總覽頁
- **THEN** 頁面 SHALL 顯示「進行中活動」（已開始且未結束的活動數）、24 小時內結束的活動數、任務進度（完成項/全部項）、今天新商品數，「快結束了，還沒完成」清單（任務：未放棄、未全部完成、且在 48 小時（`overviewTaskHours`）內結束的任務組，顯示剩餘時間與未完成項數；活動：24 小時內結束），以及最多 8 件今天新上架商品

#### Scenario: Task group ends in 40 hours

- **WHEN** 某任務組 40 小時後結束且還有 3 項未完成
- **THEN** 該組 SHALL 出現在「快結束了，還沒完成」，顯示「剩 40 小時 · 3 項未完成」

#### Scenario: Favorites tab position

- **WHEN** 使用者打開看板
- **THEN** 「我的最愛」SHALL 位在「台灣活動」與「封存」之間
