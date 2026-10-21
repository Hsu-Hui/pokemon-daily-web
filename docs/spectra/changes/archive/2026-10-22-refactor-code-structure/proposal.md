## Summary

Clean up the scraper and Apps Script code without adding new features: one shared settings file, smaller files, simpler news/product handling, safer `doPost`, and tests for the Apps Script merge logic.

## Motivation

The code works but has grown messy, and it is hard to change safely:

- The six event categories, the reminder window (4 hours) and the retention days (7 days) are written separately in `scraper/translate.py`, `gas/Code.gs` and `gas/Index.html`, so one edit can leave the others out of date.
- `gas/Index.html` is 493 lines with CSS, markup and all JavaScript together; `render()` is one long chain of `if (ui.tab === ...)` blocks.
- `scraper/sources.py` holds five sources in 391 lines, with three separate date parsers.
- `main.build_news` maps kinds through `id(n)`, `dedupe_news` mutates its inputs, and the `known_titles` parameter is only used by a test.
- Products are serialised with `p.__dict__` while everything else uses explicit builders.
- The dashboard turns product news into fake products (`price: '看消息'`, hard-coded `'寶可夢官網' → '官網'`).
- `doPost` parses the body before the secret check, so a malformed body returns an Apps Script error page instead of JSON.
- `mergeTimed_` / `mergeFresh_` have no tests.
- `translate.PATTERNS` mixes sentence rules with place-name and meteor lookups.

Later changes in this batch (keyword categories, product search, Discord error notices, task fixes) build on this structure, so it goes first.

## Proposed Solution

- Add `shared/board.json` as the single source of categories, reminder hours and retention days. Python reads it directly; `scripts/build_gas_config.py` generates `gas/Board.gs` from it, the deploy script regenerates it before `clasp push`, and a unit test fails when the generated file is stale. `getData` returns the settings to the page.
- Split `gas/Index.html` into `Index.html`, `Styles.html` and `App.html` (joined by an `include()` helper) and replace the `if` chain with one render function per tab.
- Turn `scraper/sources.py` into a `scraper/sources/` package (one module per source plus shared `dates.py`), re-exporting the same names.
- Give `News` a `kind` field set before dedupe; `dedupe_news` returns new objects and loses `known_titles`.
- Build products with `dataclasses.asdict`. Product-kind news becomes a `Product` in the scraper (`source` 官網 or 寶可夢中心, empty price, `media` = outlet), so the page shows one list without conversion.
- Wrap `doPost` parsing so every failure returns `{ok:false, error}`.
- Add Node tests (`node --test tests/gas`) for the Apps Script merge functions and run them in the daily workflow.
- Move meteor and place-name lookups to `scraper/data/translations.json`.

## Non-Goals (optional)

See design.md.

## Impact

- Affected specs: news-feed, product-feed, data-ingest, dashboard
- Affected code:
  - Modified: scraper/main.py, scraper/translate.py, scraper/config.py, gas/Code.gs, gas/Index.html, scripts/deploy_gas.sh, .github/workflows/daily.yml, tests/test_scraper.py, README.md
  - New: shared/board.json, scripts/build_gas_config.py, gas/Board.gs, gas/Styles.html, gas/App.html, scraper/sources/__init__.py, scraper/sources/go.py, scraper/sources/pchome.py, scraper/sources/news.py, scraper/sources/official.py, scraper/sources/bahamut.py, scraper/sources/dates.py, scraper/data/translations.json, tests/gas/merge.test.js
  - Removed: scraper/sources.py
