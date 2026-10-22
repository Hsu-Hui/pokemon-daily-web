## MODIFIED Requirements

### Requirement: 活動篩選

系統 SHALL 排除 `eventType` 為 `season` 或 `go-battle-league` 的活動、已結束的活動、沒有結束時間的活動，以及開始時間在 14 天（`GO_LOOKAHEAD_DAYS`）之後的活動。

#### Scenario: 太久以後的活動

- **WHEN** 活動開始時間是 20 天後
- **THEN** 該活動 SHALL 不出現在 payload 的 `events`

#### Scenario: 沒有結束時間的活動

- **WHEN** ScrapedDuck 的活動沒有結束時間（例如 `Dynamax Sneasel during Max Monday` 的 start 與 end 都是 null）
- **THEN** 該活動 SHALL 不出現在 payload 的 `events`
