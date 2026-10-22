## Summary

Make task checking match how research works in the game and stop saving on every click: checking a task also checks every task above it, changes stay on the page until 儲存 is pressed, and 總覽 lists unfinished tasks whose group ends within two days.

## Motivation

- Timed research is done step by step; ticking task 20 means tasks 1–19 are done too, but today each box must be ticked by hand.
- Every tick is saved immediately with one server call; Ryan wants to tick several and save once.
- 「快結束了，還沒完成」 only lists task groups in their last 4 hours, which is too late to plan.

## Proposed Solution

- Sequential checking inside one task group: checking task N checks tasks 1..N; unchecking task N unchecks N..end.
- A sticky bar at the top of the page with 「儲存」 and 「有 N 項變更未儲存」. Task checks are a local draft until saved; the draft survives tab switches; leaving or reloading the page with unsaved changes asks for confirmation; a failed save keeps the draft and shows an error.
- `saveTasks(changes)` in Apps Script writes all changes in one call.
- 總覽 「快結束了，還沒完成」 lists task groups that are not finished, not given up, and end within 48 hours (`overviewTaskHours` in `shared/board.json`). Discord reminders keep the 4-hour window.

## Non-Goals (optional)

See design.md.

## Impact

- Affected specs: dashboard, user-progress
- Affected code:
  - Modified: gas/App.html, gas/Styles.html, gas/Code.gs, shared/board.json, gas/Board.gs, tests/gas/app.test.js, tests/gas/merge.test.js, tests/gas/app.js, README.md
  - New: none
  - Removed: none
