## MODIFIED Requirements

### Requirement: Tabs

看板 SHALL 有六個分頁：總覽、GO 活動、任務待辦、新商品、台灣活動、封存；目前分頁 SHALL 記在瀏覽器 localStorage，下次開啟沿用。

#### Scenario: Overview content

- **WHEN** 使用者在總覽頁
- **THEN** 頁面 SHALL 顯示「進行中活動」（已開始且未結束的活動數）、24 小時內結束的活動數、任務進度（完成項/全部項）、今天新商品數，「快結束了，還沒完成」清單（任務：未放棄、未全部完成、且在 48 小時（`overviewTaskHours`）內結束的任務組，顯示剩餘時間與未完成項數；活動：24 小時內結束），以及最多 8 件今天新上架商品

#### Scenario: Task group ends in 40 hours

- **WHEN** 某任務組 40 小時後結束且還有 3 項未完成
- **THEN** 該組 SHALL 出現在「快結束了，還沒完成」，顯示「剩 40 小時 · 3 項未完成」

## ADDED Requirements

### Requirement: Save bar

頁面頂端 SHALL 有固定的儲存列，顯示「有 N 項變更未儲存」與「儲存」按鈕；沒有變更時按鈕 SHALL 停用並顯示「已儲存」。任務勾選 SHALL 先存在頁面的草稿，按「儲存」才送出；切換分頁 SHALL 保留草稿；有未儲存變更時離開或重新整理頁面 SHALL 跳出瀏覽器確認。「放棄」「復原」SHALL 立即儲存，不經過草稿。

#### Scenario: Tick then save

- **WHEN** 使用者勾了 3 個任務後按「儲存」
- **THEN** 系統 SHALL 一次送出 3 項變更，成功後儲存列顯示「已儲存」

#### Scenario: Save fails

- **WHEN** 儲存失敗
- **THEN** 草稿 SHALL 保留，並顯示「儲存失敗，請再試一次」

#### Scenario: Leave with unsaved changes

- **WHEN** 有未儲存的勾選時重新整理頁面
- **THEN** 瀏覽器 SHALL 先詢問是否離開
