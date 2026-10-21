## Context

The project has two runtimes: a Python scraper on GitHub Actions and Google Apps Script (deployed by clasp from `gas/`). clasp 2.4.2 only uploads `.gs`, `.js`, `.html` files and `appsscript.json`, so Apps Script cannot read an arbitrary JSON file from the repo at runtime. Behaviour must stay the same except where the delta specs say otherwise.

## Goals / Non-Goals

**Goals:**

- One place to edit categories, reminder hours and retention days.
- Smaller, single-purpose files in `scraper/sources/` and `gas/`.
- Product announcements stored and shown as products, with no conversion in the page.
- `doPost` always answers JSON.
- Automated tests for `mergeTimed_` and `mergeFresh_`.

**Non-Goals:**

- No new dashboard features (search, keyword categories and Discord notices are separate changes).
- No change to task ids or task sources (handled by `fix-empty-task-list`).
- No bundler or npm dependencies for Apps Script code.
- No change to sheet names or the ingest payload's top-level keys.

## Decisions

### Shared settings file with a generated Apps Script copy

`shared/board.json` holds `categories` (ordered list of `{name, keywords}`; keywords stay empty until `keyword-event-categories`), `remindHours`, `keepNewsDays`, `keepProductDays`, `keepArchiveDays`, `keepSeenDays`. `scripts/build_gas_config.py` writes `gas/Board.gs` as `const BOARD = <json>;` with a "generated, do not edit" header. `scripts/deploy_gas.sh` runs the generator before pushing, and `tests/test_scraper.py` asserts the committed `gas/Board.gs` equals the generator output. Alternative rejected: sending settings inside the daily payload — the page would show stale or missing settings until the next scrape, and reminders would depend on scraper runs.

### Split Index.html with include()

`Code.gs` gets `include(name)` returning `HtmlService.createHtmlOutputFromFile(name).getContent()`; `Index.html` keeps the skeleton and pulls `Styles` and `App` with `<?!= include('…') ?>`. `render()` becomes a `RENDERERS` map of per-tab functions (`renderOverview`, `renderGo`, `renderTasks`, `renderShop`, `renderTw`, `renderArchive`). Alternative rejected: separate pages per tab — would need several `google.script.run` loads.

### Sources package with shared dates module

`scraper/sources/` contains `go.py`, `pchome.py`, `news.py` (Google News + dedupe), `official.py`, `bahamut.py`, `http.py` (`_get`) and `dates.py` (`parse_time`, `parse_date`, `mkdate`). `__init__.py` re-exports the public names and the private helpers tests use (`_clean_title`), so `from scraper import sources` keeps working.

### Kind tagged before dedupe

`News` gains `kind: str = "event"`. `build_news` sets each item's kind (official items via `news_kind`) before calling `dedupe_news`, which copies kept items with `dataclasses.replace` and never mutates its input. `known_titles` is removed with its test.

### Product announcements become products in the scraper

After dedupe, `kind == "product"` news is converted by `news_to_product` into `Product(id, source="官網" if official else "寶可夢中心", name=title, url, price="", image="", media=<outlet>)` and appended to `products`; only `event` news stays in `news`. Products are serialised with `dataclasses.asdict`. The products sheet gains a `media` column. The page shows `看消息` when a product has no price. Old product-kind rows already in the 新聞 sheet still pass the page's `kind === 'event'` filter out and expire within 7 days.

### doPost always returns JSON

Parsing and the secret check move inside `try`; any exception returns `{ok:false, error:<message>}`. The script lock is taken only after the secret check.

### Node tests for Apps Script pure functions

`tests/gas/merge.test.js` loads `gas/Board.gs` and `gas/Code.gs` into a `vm` context with stub globals and tests `mergeTimed_` and `mergeFresh_` with `node:test`. The daily workflow runs `node --test tests/gas` after the Python tests (Node 20 via `actions/setup-node`).

### Translation lookups in a data file

`scraper/data/translations.json` holds `months`, `meteors` and `places`. `PATTERNS` keeps only regex rules; places are applied after the patterns, which matches their current position at the end of `PATTERNS`.

## Implementation Contract

- Behaviour: the dashboard, the ingest response, reminders and the payload look the same as before, except (a) product announcements arrive in `payload.products` with `source` 官網/寶可夢中心, `price: ""` and a `media` field, (b) malformed POST bodies return `{ok:false,error}`, (c) `getData()` also returns `config` (the BOARD object).
- Interface: `shared/board.json` keys listed above; `gas/Board.gs` defines global `BOARD`; `include(name)` in `Code.gs`; `scraper.sources` exposes the same names as before minus `dedupe_news(..., known_titles)`.
- Failure modes: a stale `gas/Board.gs` fails `python -m unittest`; deploy regenerates it anyway.
- Acceptance: `python -m unittest` and `node --test tests/gas` pass; `python -m scraper.main` without ingest settings writes `out/payload.json`; grep shows no hard-coded 4-hour or 7-day values or category list left in `gas/` or `scraper/translate.py` outside `Board.gs`/`board.json` readers.
- Scope: in — the items in this design. Out — new features, task ids, task sources, sheet renames.

## Risks / Trade-offs

- [Generated file forgotten after editing board.json] → unit test fails and deploy regenerates.
- [Apps Script `include` templates break the page] → manual check after deploy; the HTML is only re-arranged, not rewritten.
- [Product rows change shape] → old rows age out in 7 days; the page tolerates a missing `media`.

## Migration Plan

Merge to main; the deploy workflow regenerates `Board.gs` and pushes. The next daily run writes the new product shape. Rollback: revert the merge commit; the deploy workflow pushes the previous code.
