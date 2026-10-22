## 1. Server

- [ ] 1.1 "Batch save on the server": `saveTasks(changes)` with key/value validation and one lock (Batch save requirement). Verify: node tests — valid batch saved, `bad change` on invalid key or value with state unchanged.

## 2. Page

- [ ] 2.1 "Ordered checking within a group" (Ordered task checking requirement): clicking task N updates the draft for 1..N or N..end. Verify: node tests over the example table. [after: 1.1]
- [ ] 2.2 "Draft and save bar" (Save bar, Optimistic update requirements): sticky bar with count, 儲存 calls `saveTasks`, draft kept on failure and across tabs, `beforeunload` warning, 放棄/復原 still immediate. Verify: node tests for count, success, failure and tab switch; manual check of the sticky bar and leave prompt on the deployed page. [after: 2.1]
- [ ] 2.3 "Overview task window" (Tabs requirement): `overviewTaskHours: 48` in `shared/board.json`, overview lists unfinished groups ending within 48 h. Verify: node test with a group ending in 40 h (listed) and 50 h (not listed); `test_board_gs_is_generated` passes. [after: 2.2]
