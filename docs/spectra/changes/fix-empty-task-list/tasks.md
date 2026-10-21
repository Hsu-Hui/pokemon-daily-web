## 1. Task ids

- [ ] 1.1 Implement "Stable task ids by hash": `main.task_id(*parts)` and `TaskGroup.tasks` as (id, text, reward); Bahamut tasks get `task_id(text)` (Task line extraction, Per-user state requirements). Verify: unittest that the same text gives the same id and `build_tasks` output has `id` on every task.

## 2. Bahamut parsing

- [ ] 2.1 Implement "Full-date Bahamut periods" (Period parsing requirement) and skip lines ending in 。/！ (Task line extraction). Verify: unittests `test_full_date_period` and `test_announcement_post_has_no_tasks` using a trimmed announcement fixture; Post acceptance behaviour unchanged by existing tests. [after: 1.1]

## 3. LeekDuck event research

- [ ] 3.1 Implement "LeekDuck event pages as the timed research source": `parse_event_research` and `fetch_event_research` for active event pages, max 20 pages (Active event pages, Research steps parsing requirements). Verify: unittests on `tests/fixtures/leekduck_timed_research.html` (tasks + rewards) and `tests/fixtures/leekduck_no_research.html` (no group), and a mocked fetch that skips future events. [after: 1.1]
- [ ] 3.2 Implement "Event research group shape" (Event research group requirement): group id/name/url/period, translated text, `translate.reward` with an `items` table, and payload order Bahamut → LeekDuck → field research in `main.collect`. Verify: unittest on the example table (`轉動 10 個補給站或道館` / `蔓莓果 ×5`) and on group order. [after: 3.1]
