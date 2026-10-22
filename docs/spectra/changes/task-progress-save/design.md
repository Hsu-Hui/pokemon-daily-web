## Context

Task check marks live in UserProperties (`state.taskDone`, keys `<groupId>#<taskId>`). `setFlag` saves one key per call and the page updates optimistically. Discord reminders read the saved state of the trigger owner.

## Goals / Non-Goals

**Goals:**

- Ordered checking within a group.
- One explicit save for task checks, with no silent loss of unsaved work.
- Overview list based on a 48-hour window for tasks.

**Non-Goals:**

- 放棄／復原 and favourites stay immediate (not part of the draft).
- No change to the Discord reminder window (4 hours).
- No ordering across different task groups.

## Decisions

### Ordered checking within a group

Order is the task list order shown on the page (LeekDuck step order, Bahamut post order, field research list order). Checking task N sets tasks 1..N to checked; unchecking task N sets N..end to unchecked. The rule applies to every task group, including monthly field research, unless Ryan decides otherwise (open question in the plan).

### Draft and save bar

`ui.draft` maps task keys to the new value; the page shows saved state overlaid with the draft. The bar is `position: sticky; top: 0` with the count and a 儲存 button (disabled when empty). Saving calls `saveTasks(draft)`; on success the returned state replaces `data.state` and the draft clears; on failure the draft stays and a toast says 「儲存失敗，請再試一次」. `beforeunload` warns when the draft is not empty. Tab switches keep the draft.

### Batch save on the server

`saveTasks(changes)` validates that every key matches `<groupId>#<taskId>` and every value is boolean, takes the user lock once, applies all changes and returns the new state. `setFlag` stays for `gaveUp` only.

### Overview task window

`shared/board.json` gains `overviewTaskHours: 48`. A group is listed when it is not given up, not ended, has unfinished tasks (saved state plus draft), and ends within that window. The event part of the list keeps the 24-hour rule.

## Implementation Contract

- Behaviour: checking #20 in a group shows #1–#20 ticked and the bar counts the changed boxes; nothing is sent until 儲存; reload with a non-empty draft prompts; after saving the ticks persist on another device.
- Interface: `saveTasks(changes: {[key]: boolean}) -> state`; `BOARD.overviewTaskHours`.
- Failure modes: invalid keys or values → `bad change` error, nothing written; network failure → draft kept, toast shown.
- Acceptance: node tests for ordered checking (check 20 → 1..20, check 5 → 1..5, uncheck 5 → 1..4 remain), draft count, save success/failure, `saveTasks` validation, overview 48-hour list; manual check of the sticky bar and leave warning.
- Scope: in — ordering, draft/save, overview window. Out — favourites, layout fixes, reminder window.

## Risks / Trade-offs

- [Field research tasks are not ordered in the game; auto-checking earlier ones is wrong there] → listed as a decision for Ryan; easy to limit to `ld-`/`bh-` groups.
- [Unsaved ticks are lost if the phone kills the tab] → `beforeunload` cannot always fire on mobile; the bar makes unsaved state visible.
