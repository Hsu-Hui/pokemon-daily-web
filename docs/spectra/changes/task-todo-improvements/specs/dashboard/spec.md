## ADDED Requirements

### Requirement: Daily field research reward reference

The Tasks page SHALL display every active `field-` group in a separate "日常田野調查獎勵" reference section. Each reference row SHALL show the research task text and its reward, SHALL link to the source when available, and SHALL NOT render a checkbox, completion count, progress bar, abandon control, archive entry, overview progress contribution, or Discord reminder.

#### Scenario: View daily field research rewards

- **WHEN** the current `field-202610` group contains "捕捉 5 隻寶可夢" with reward "遇見 皮卡丘"
- **THEN** the Tasks page SHALL show that task and reward in the reference section without a checkbox

#### Scenario: Reference data is excluded from task status

- **WHEN** a `field-` group is active and ends within the overview reminder window
- **THEN** its items SHALL NOT affect the task progress total or appear in "快結束了，還沒完成"

### Requirement: Preserve task-page scroll position

Task-page interactions that re-render task content SHALL preserve the user's vertical scroll position to the nearest position allowed by the resulting document height. This SHALL cover checking or unchecking a task, expanding or collapsing a completed group, abandoning a group, editing or deleting a manual group, and the success or failure response of those operations. Switching a main tab or selecting a pagination page SHALL continue to scroll to the top.

#### Scenario: Check a task near the bottom

- **WHEN** the user scrolls to a task near the bottom of the Tasks page and changes its checkbox
- **THEN** the task content SHALL re-render without moving the viewport to the top

#### Scenario: Delete a manual group near the bottom

- **WHEN** the user deletes a manual group while the Tasks page is scrolled down
- **THEN** both the optimistic removal and server response SHALL preserve the previous vertical position, clamped only when the shorter document cannot reach it

#### Scenario: Change pagination page

- **WHEN** the user selects another task pagination page
- **THEN** the viewport SHALL move to the top of the page

## MODIFIED Requirements

### Requirement: 分頁

The dashboard SHALL have seven tabs: Overview, GO Events, Tasks, New Products, Events & News, Favorites, and Archive. The current tab SHALL be stored in browser localStorage and restored on the next visit.

#### Scenario: 總覽內容

- **WHEN** the user opens Overview
- **THEN** the page SHALL show active event count, events ending within 24 hours, effective task progress for trackable tasks, today's new-product count, a "快結束了，還沒完成" list, and up to 8 products added today; the list SHALL include only non-abandoned trackable task groups whose effective state has at least one current task not completed and ending within `overviewTaskHours`, plus events ending within 24 hours

#### Scenario: 任務組 40 小時後結束

- **WHEN** a trackable task group ends in 40 hours and has 3 current tasks not completed in its effective state
- **THEN** the group SHALL appear in "快結束了，還沒完成" with "剩 40 小時 · 3 項未完成"

#### Scenario: 已完成的小隕星流星雨

- **WHEN** the Tasks page marks every current item in "小隕星流星雨：獵戶座 2026" as complete
- **THEN** the group SHALL immediately disappear from "快結束了，還沒完成"

#### Scenario: 尚未儲存的完成草稿

- **WHEN** the user checks the last unfinished item and the Tasks page marks the group as all complete before the draft is saved
- **THEN** Overview SHALL immediately exclude the group from "快結束了，還沒完成" because both pages SHALL use the same effective completion state

#### Scenario: 我的最愛分頁位置

- **WHEN** the user opens the dashboard
- **THEN** Favorites SHALL appear between Events & News and Archive

### Requirement: 任務待辦頁

The Tasks page SHALL list active trackable task groups that are neither abandoned nor ended, ordered by remaining time. Each group SHALL show its period, remaining time, completion count, progress bar, a checkbox and reward for each task, and an abandon control; a missing reward SHALL link to "見原文" only when a source URL exists. Active `field-` groups SHALL be rendered only in the separate daily field research reward reference section. Groups whose current items are all completed in saved state SHALL appear after unfinished groups under "已完成 N 組", collapsed by default with name, end time, "全部完成", and an expand control; an all-checked but unsaved group SHALL remain in place and expanded.

#### Scenario: 放棄任務組

- **WHEN** the user abandons a trackable task group
- **THEN** the group SHALL move to Archive and stop producing reminders

#### Scenario: 已完成的限時調查

- **WHEN** all items in a timed research group are checked and saved
- **THEN** the group SHALL move below "已完成 1 組", start collapsed, and expose its items when expanded

#### Scenario: 勾完還沒儲存

- **WHEN** the user checks the final item but has not selected Save
- **THEN** the group SHALL stay in its current position and show all tasks

### Requirement: 儲存列

The Tasks page heading SHALL place "任務待辦" on the left and the saved or unsaved status plus Save button on the far right of the same heading row. With no draft changes, the disabled button SHALL show "已儲存"; with draft changes, the heading SHALL show "有 N 項變更未儲存" and an enabled "儲存" button. Other tabs SHALL NOT render these controls. Task checkbox changes SHALL remain in a page draft until Save sends them together; switching tabs SHALL retain the draft; leaving or reloading with a draft SHALL trigger browser confirmation. Abandon and restore SHALL continue to save immediately.

#### Scenario: 勾選後儲存

- **WHEN** the user changes 3 task items and selects Save
- **THEN** the system SHALL send all 3 changes in one request and show the disabled "已儲存" state in the Tasks heading after success

#### Scenario: 儲存失敗

- **WHEN** saving fails
- **THEN** the draft SHALL remain and the page SHALL show "儲存失敗，請再試一次"

#### Scenario: 有未儲存變更時離開

- **WHEN** the user reloads with unsaved checkbox changes
- **THEN** the browser SHALL ask for confirmation before leaving

#### Scenario: 其他分頁沒有儲存列

- **WHEN** the user changes a task and switches to GO Events
- **THEN** GO Events SHALL NOT show save controls, and returning to Tasks SHALL restore the draft and save controls in the heading

#### Scenario: 窄螢幕標題列

- **WHEN** the Tasks page is shown at 375 px width
- **THEN** "任務待辦" and the Save button SHALL remain in the same heading row without covering each other, while the descriptive text SHALL appear on a separate row

### Requirement: 手動新增任務組

The Tasks page SHALL provide a "＋ 新增任務組" form with name (maximum 60 characters), future end time, and ordered task lines using "任務 → 獎勵", `->`, or `=>`, with an optional reward. Blank name, past end time, or no tasks SHALL be rejected with a visible message. Manual groups SHALL be stored per user in UserProperties under `manual:<id>` with a `my-` id; each user SHALL have at most 30 groups, each group at most 30 tasks, each task and reward at most 80 characters, and content over 9 KB SHALL be rejected. Manual groups SHALL support ordered checkbox behavior, saving, abandonment, collapsing, reminders, editing, and confirmed deletion; they SHALL display "手動" and SHALL NOT show "見原文" without a source URL. Manual groups ended beyond `keepArchiveDays` SHALL be deleted when data is loaded.

#### Scenario: 新增遊戲裡才看得到的限時調查

- **WHEN** the user enters "限時調查：30 年的軌跡", an end time 3 days later, and two task lines, then selects Add
- **THEN** the Tasks page SHALL show a "手動" group and checking its second task SHALL also check its first task

##### Example: 任務行

| Input | Task | Reward |
| ---- | ---- | ---- |
| 捕捉 30 隻寶可夢 → 精靈球 ×10 | 捕捉 30 隻寶可夢 | 精靈球 ×10 |
| 轉動 5 個補給站 | 轉動 5 個補給站 | empty |
| 孵化 1 顆蛋 -> 星星沙 ×500 | 孵化 1 顆蛋 | 星星沙 ×500 |
| blank line | ignored | empty |

#### Scenario: 只有自己看得到

- **WHEN** another user opens the dashboard
- **THEN** that user SHALL NOT see Ryan's manual task groups

#### Scenario: 編輯手動任務組

- **WHEN** the user selects Edit, corrects the group name, end time, task text, or reward, and saves valid values
- **THEN** the same manual group id SHALL remain visible with the updated values and a successful message

#### Scenario: 編輯時保留完成紀錄

- **WHEN** an existing manual task item keeps its stable item id while its text or reward is corrected
- **THEN** its saved completion state SHALL remain associated with that item

#### Scenario: 編輯時新增與移除項目

- **WHEN** editing removes one task and adds another
- **THEN** the removed task's completion key SHALL be deleted, the new task SHALL receive an unused item id and start unfinished, and all retained tasks SHALL preserve their ids and completion state

#### Scenario: 編輯驗證失敗

- **WHEN** edited data violates the same limits used for adding a group
- **THEN** the server SHALL reject the entire update, keep the previous group and completion state unchanged, and the client SHALL keep the edit form open with the entered values

#### Scenario: 刪除

- **WHEN** the user selects Delete on a manual group and confirms
- **THEN** that group SHALL disappear from Tasks
