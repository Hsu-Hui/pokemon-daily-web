## Summary

Remove the 完成 checkbox from GO events. Events stay on the GO 活動 tab until they end and then move to 封存 automatically.

## Motivation

Ryan does not want to tick off events; marking an event as done adds a step that nothing else uses (reminders only cover task groups).

## Proposed Solution

- GO 活動 table and cards no longer show a checkbox or a 完成 column; the tab lists every event that has not ended.
- 總覽's first stat becomes 「進行中活動」 (started and not ended).
- 封存 lists ended events only, without a 復原 button; given-up task groups keep their 復原 button.
- `setFlag` accepts only `taskDone` and `gaveUp`; old `done` entries in UserProperties are ignored.

## Non-Goals (optional)

- No change to task checkboxes, 放棄, or Discord reminders.
- No migration that deletes stored `done` flags.

## Impact

- Affected specs: dashboard, user-progress
- Affected code:
  - Modified: gas/App.html, gas/Code.gs, tests/gas/app.test.js, tests/gas/merge.test.js
  - New: none
  - Removed: none
