## 1. Shared settings

- [x] 1.1 Implement "Shared settings file with a generated Apps Script copy" (Shared settings requirement): add `shared/board.json`, `scripts/build_gas_config.py` and generated `gas/Board.gs`; `scraper/translate.py` reads categories from board.json; `scripts/deploy_gas.sh` regenerates before push. Verify: new unittest `test_board_gs_is_generated` passes, and fails after editing board.json without regenerating.

## 2. Scraper structure

- [x] 2.1 Implement "Sources package with shared dates module": replace `scraper/sources.py` with the `scraper/sources/` package and shared `dates.py`, keeping `from scraper import sources` names. Verify: `python -m unittest` passes unchanged except the removed `known_titles` test.
- [x] 2.2 Implement "Kind tagged before dedupe" (News kind requirement): `News.kind` set before `dedupe_news`, which no longer mutates inputs or accepts `known_titles`. Verify: unittest asserting input items keep empty `others` after dedupe.
- [x] 2.3 Implement "Product announcements become products in the scraper" (Product announcements requirement): product-kind news becomes `Product` with `media`, products serialised by `dataclasses.asdict`, `payload.news` only has event news. Verify: unittest on `main.build_news`/`news_to_product` output shapes. [after: 2.2]
- [x] 2.4 Implement "Translation lookups in a data file": move months, meteors and places to `scraper/data/translations.json`. Verify: existing translation tests plus `event_name("Pokémon GO Wild Area 2026: Sendai • Tohoku")` unchanged before/after. [after: 1.1]

## 3. Apps Script

- [x] 3.1 Implement "doPost always returns JSON" (Secret check requirement) and the `media` column (Sheet storage requirement); retention constants come from `BOARD`. Verify: node test posting a malformed body gets `{ok:false}`. [after: 1.1]
- [x] 3.2 Implement "Split Index.html with include()" and the Products tab requirement: `Index.html` + `Styles.html` + `App.html`, `RENDERERS` per tab, labels and categories from `data.config`, products shown without conversion and `看消息` for empty price. Verify: manual check of all six tabs after deploy and a node test that `include`-joined HTML contains every tab renderer. [after: 3.1]
- [x] 3.3 Implement "Node tests for Apps Script pure functions": `tests/gas/merge.test.js` covering `mergeTimed_` (30-day archive keep) and `mergeFresh_` (seen map, 7-day expiry); daily workflow runs `node --test tests/gas`. Verify: `node --test tests/gas` passes locally. [after: 3.1]

## 4. Docs

- [x] 4.1 Update README file table and 調整 section for `shared/board.json` and the new files. Verify: content review. [after: 3.2]
