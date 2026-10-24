## MODIFIED Requirements

### Requirement: 任務依序勾選

Every trackable task group SHALL enforce page order: checking item N SHALL check items 1 through N, and unchecking item N SHALL uncheck item N through the final item. This SHALL apply to LeekDuck `ld-`, Bahamut `bh-`, manual `my-`, and any other group rendered as a trackable task group. Different groups SHALL remain independent. Daily field research reward groups with a `field-` id SHALL be rendered as reference data without checkboxes and SHALL NOT participate in this rule.

#### Scenario: 10 月田野調查任務依序勾選

- **WHEN** the user checks item 5 in a trackable group named "10 月田野調查任務"
- **THEN** items 1 through 5 SHALL all become checked and later items SHALL remain unchanged

#### Scenario: 勾選後面的任務

- **WHEN** a trackable group has 25 items and the user checks item 20
- **THEN** items 1 through 20 SHALL be checked and items 21 through 25 SHALL remain unchanged

#### Scenario: 取消前面的任務

- **WHEN** items 1 through 20 are checked and the user unchecks item 5
- **THEN** items 1 through 4 SHALL remain checked and items 5 through 25 SHALL be unchecked

##### Example: Ordered checkbox transitions

| Current checked items | Action | Resulting checked items |
| ---------- | ---- | ---------- |
| none | check item 5 | 1-5 |
| 1-5 | check item 20 | 1-20 |
| 1-20 | uncheck item 5 | 1-4 |

#### Scenario: 日常田野調查沒有勾選框

- **WHEN** the user views an active `field-` daily research reward group
- **THEN** no checkbox SHALL be rendered for its items
