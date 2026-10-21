## 1. Dashboard

- [x] 1.1 Remove the event checkbox and 完成 column from GO 活動 rows and cards, list every event that has not ended, rename the overview stat to 進行中活動, and show ended events in 封存 without 復原 (GO events tab, Tabs, Archive tab, Derived status requirements). Verify: node tests in `tests/gas/app.test.js` — no `data-flag="done"` in the go tab, an event with an old `done` flag still listed, an ended event in archive without 復原.

## 2. Apps Script

- [x] 2.1 `setFlag` accepts only `taskDone` and `gaveUp`; `loadState_` no longer returns `done` (Set flag, Per-user state requirements). Verify: node test that `setFlag('done', …)` throws `bad kind`. [after: 1.1]
