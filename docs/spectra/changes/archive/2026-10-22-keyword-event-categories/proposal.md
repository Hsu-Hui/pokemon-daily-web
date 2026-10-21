## Summary

Put GO events into a tab (category) when their name contains that tab's keyword, using a keyword table that Ryan can edit in `shared/board.json`.

## Motivation

Events with a generic ScrapedDuck type such as `event` land in 其他 even when the name clearly says what they are (for example "Dynamax Trails" or "GO Pass: Halloween"). The current name rules are hard-coded English regexes in `translate.event_category`, and only cover three tabs.

## Proposed Solution

- Each category in `shared/board.json` gets a `keywords` list (English and Chinese).
- `event_category(type_slug, name, name_zh)` keeps the type-slug table first; if the slug is not mapped, it checks the English name and the translated Chinese name against each category's keywords in tab order (case-insensitive) and picks the first match; otherwise 其他.
- Tests cover a table of example names.

## Non-Goals (optional)

- No keyword matching in the browser; categories are decided by the scraper each day.
- No change to the slug table.

## Impact

- Affected specs: go-events
- Affected code:
  - Modified: shared/board.json, gas/Board.gs, scraper/translate.py, scraper/main.py, tests/test_scraper.py, README.md
  - New: none
  - Removed: none
