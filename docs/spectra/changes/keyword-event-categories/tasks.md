## 1. Keyword table

- [x] 1.1 Add the default `keywords` to each category in `shared/board.json` and regenerate `gas/Board.gs`, so the Six categories requirement's table is the data. Verify: `test_board_gs_is_generated` passes.

## 2. Matching

- [x] 2.1 `translate.event_category(type_slug, name, name_zh="")` uses the slug table, then keywords in tab order on English (case-insensitive) and Chinese names; `main.build_events` passes the translated name (Six categories requirement). Verify: unittest `CategoryTests` covering every row of the example table. [after: 1.1]
- [x] 2.2 README 調整 section explains how to add keywords and regenerate `gas/Board.gs`. Verify: content review. [after: 2.1]
