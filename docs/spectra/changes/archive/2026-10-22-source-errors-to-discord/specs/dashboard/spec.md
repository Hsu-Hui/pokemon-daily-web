## MODIFIED Requirements

### Requirement: Data loading

看板 SHALL 一次透過 `getData` 取得 `updatedAt`、活動、任務、商品、新聞、共用設定與目前使用者的勾選狀態；有 `updatedAt` 時顯示「最後更新 <時間>」，否則顯示「還沒有資料，等每日排程跑過一次」；載入失敗時顯示錯誤訊息。所有時間 SHALL 以台灣時區顯示。抓取失敗的來源 SHALL NOT 顯示在看板上（改由 Discord 通知）。

#### Scenario: Source errors today

- **WHEN** 今天的抓取有來源失敗
- **THEN** 總覽頁 SHALL 不顯示失敗訊息，`getData` SHALL 不回傳 `errors`
