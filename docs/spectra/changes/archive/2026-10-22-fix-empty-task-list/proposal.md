## Problem

The 任務待辦 page only ever shows the monthly field research group. The daily run on 2026-10-21 (Actions run 39625663387) sent 1 task group (10 月田野調查) and Apps Script stored it (`tasks: 1`); no event timed research ever appears.

## Root Cause

- The Bahamut source only reads 【情報】 posts whose title contains 調查/任務/課題. On 2026-10-21 the board's first page had 15 【情報】 posts; only the pinned collection thread matched, and it has no parsable period, so it was dropped.
- The other 【情報】 posts are Niantic announcements. Their bodies describe events ("田野調查課題即將登場") but do not list the actual tasks, so even with a looser title filter they produce only false "tasks" (descriptive sentences that contain numbers).
- Bahamut periods written with the year ("2026年11月9日10:00～2026年11月13日20:00") are mis-parsed: the end is taken as the start day at 23:59.
- Bahamut tasks have no id, so check marks are keyed by position and move to another task when the post is edited.

LeekDuck event pages (already linked from ScrapedDuck events) contain the real Timed/Special Research steps in structured markup (`.special-research-list .step-item .task-reward` with `.task-text` and `.reward-label`), e.g. "adidas Timed Research (1/3): Spin 10 PokéStops or Gyms → Razz Berry ×5".

## Proposed Solution

- New source: for ScrapedDuck events that are active now (excluding skipped types), fetch the LeekDuck event page and turn its timed/special research steps into a task group `ld-<eventID>` named `限時調查：<中文活動名>`, with the event's start/end. Tasks and rewards are translated with the existing dictionary plus a small item table.
- Bahamut: parse full dates with year, and ignore sentence lines ending in 。 or ！ as tasks.
- Give every Bahamut and LeekDuck task a stable `id` (hash of its text) so check marks follow the task.

## Non-Goals (optional)

- No AI translation and no new sites beyond LeekDuck event pages.
- No change to how the monthly field research group is built.

## Success Criteria

- Parsing the saved adidas event page yields 3 steps' tasks with rewards; parsing the into-the-wild page (empty research list) yields no group.
- `parse_period("台灣時間2026年11月9日10:00～2026年11月13日20:00", ...)` returns 11/9 10:00 to 11/13 20:00.
- The saved Bahamut announcement posts (Halloween Part 1, Wild Area week) yield no task group.
- After merge, the next daily run's log shows one or more `限時調查：` groups whenever LeekDuck lists timed research for an active event.

## Impact

- Affected specs: event-research (new), bahamut-tasks, user-progress
- Affected code:
  - Modified: scraper/main.py, scraper/config.py, scraper/translate.py, scraper/sources/bahamut.py, scraper/sources/dates.py, scraper/sources/__init__.py, scraper/data/translations.json, tests/test_scraper.py
  - New: scraper/sources/leekduck.py, tests/fixtures/leekduck_timed_research.html, tests/fixtures/leekduck_no_research.html
  - Removed: none
