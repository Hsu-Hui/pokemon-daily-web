## ADDED Requirements

### Requirement: Claim reward rows skipped

限時調查步驟中英文為「Claim Reward!」的列 SHALL 不輸出為任務；巴哈或 LeekDuck 任務翻譯後文字為「領取獎勵」的 SHALL 一併略過。其餘任務的 `id` SHALL 不因此改變。

#### Scenario: Step ends with claim reward

- **WHEN** 某步驟有「Use a Star Piece」與「Claim Reward!」兩列
- **THEN** 任務組 SHALL 只有「使用 1 個星星碎片」
